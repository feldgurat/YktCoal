from datetime import datetime, timedelta, timezone
import uuid

from fastapi import APIRouter, HTTPException, status

from api.routes import ANSWER_SIGN_IN_SMS_CODE, API_V1_PREFIX, AUTH, REFRESH, REGISTER, SEND_SIGN_IN_SMS_CODE
from data.entities.Person import Person
from data.schemas.Auth import RefreshIn, RegisterAnswer, SmsCodeRequestAnswer, SmsRequestIn, SmsVerifyIn, TokenPair
from data.schemas.Person import PersonCreate
from data.schemas.User import UserCreateWithPerson
from services.AdminService import AdminServiceDep
from services.AuthService import OTP_TTL_SECONDS, AuthServiceDep
from services.DriverService import DriverServiceDep
from services.Exeptions import InvalidToken, InvalidTokenType, OtpRateLimitError, TokenHasExpired
from services.PersonService import PersonServiceDep
from services.UserService import UserServiceDep




router = APIRouter(prefix=f"{API_V1_PREFIX}{AUTH}", tags=["Auth"])



@router.post(SEND_SIGN_IN_SMS_CODE
             #, response_model=SmsCodeRequestAnswer
             )
async def sms_code_request(
    data: SmsRequestIn,
    authService: AuthServiceDep,
    personService: PersonServiceDep
):
    
    try:
        phone = authService.normalize_phone(data.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if await personService.get_by_contact_number(phone) is None:
        raise HTTPException(status_code=409, detail="Пользователя с таким номером нет в системе")
        

    try:
        await authService.resending_prot(phone)
    except Exception as e:
        if isinstance(e, OtpRateLimitError):
            raise HTTPException(status_code=429, detail="Попробуйте запросить код чуть позже")
        raise
    

    code = authService.generate_code()
    code_hash = authService.hash_code(phone, code)
    expires_at = datetime.utcnow() + timedelta(seconds=int(OTP_TTL_SECONDS))

    text = f"Ваш код подтверждения: {code}"

    # await send_sms_via_exolve(destination=phone, text=text)

    await authService.invalide_old_codes(phone)

    await authService.add_new_sms_code(phone, code_hash, expires_at)
    await authService.session.commit()

    return {"status": "ok", "message": "Код отправлен", "code": code}


@router.post(ANSWER_SIGN_IN_SMS_CODE, response_model=TokenPair)
async def sms_code_answer(
    data: SmsVerifyIn,
    authService: AuthServiceDep,
    personService: PersonServiceDep
):
    try:
        phone = authService.normalize_phone(data.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = await personService.get_by_contact_number(phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    sms_code = await authService.get_actual_sms_code(phone)
    if not sms_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код не найден",
        )

    now = datetime.now(timezone.utc)

    expires_at = sms_code.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        raise HTTPException(status_code=400, detail="Срок действия кода истёк")
    
    if sms_code.code_hash != authService.hash_code(phone, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код",
        )

    await authService.invalide_old_codes(phone)
    await authService.session.commit()

    access_token = authService.create_access_token(str(user.id), user.token_version)
    refresh_token = authService.create_refresh_token(
        user_id=str(user.id),
        version=user.token_version,
    )


    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.post(REFRESH, response_model=TokenPair)
async def refresh_tokens(
    data: RefreshIn,
    authService: AuthServiceDep,
    personService: PersonServiceDep
):
    try:
        payload = authService.decode_token(data.refresh_token, expected_type="refresh")
    except TokenHasExpired as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.message))
    except InvalidToken as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.message))
    except InvalidTokenType as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.message))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    jti = payload["jti"]
    user_id = payload["sub"]
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    token_version = payload.get("ver")

    if await authService.is_token_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Токен отозван")

    user = await personService.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    if token_version != user.token_version:
        raise HTTPException(status_code=401, detail="Токен устарел")

    exp_ts = payload["exp"]
    await authService.add_token_to_blacklist(jti=jti, exp_ts=exp_ts)

    access_token = authService.create_access_token(str(user.id), user.token_version)
    refresh_token = authService.create_refresh_token(str(user.id), user.token_version)
    #Надо добавить инкремент версии токена
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(REGISTER, response_model=RegisterAnswer, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreateWithPerson,
    authService: AuthServiceDep,
    userService: UserServiceDep,
):
    try:
        phone = authService.normalize_phone(data.contact_number)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    existing_user = await userService.get_by_contact_number(phone)
    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="User с таким номером уже существует",
        )
    
    try:
        user = UserCreateWithPerson(
            name=data.name,
            contact_number=phone,
            telegram_user_id=data.telegram_user_id,
            address=data.address
        )

        user = await userService.create_full(user)
        await userService.session.commit()

        try:
            await authService.resending_prot(phone)
        except Exception as e:
            if isinstance(e, OtpRateLimitError):
                raise HTTPException(status_code=429, detail="Попробуйте запросить код чуть позже")
            raise
        

        code = authService.generate_code()
        code_hash = authService.hash_code(phone, code)
        expires_at = datetime.utcnow() + timedelta(seconds=int(OTP_TTL_SECONDS))

        text = f"Ваш код подтверждения: {code}"

        # await send_sms_via_exolve(destination=phone, text=text)

        await authService.invalide_old_codes(phone)

        await authService.add_new_sms_code(phone, code_hash, expires_at)
        await authService.session.commit()

        return RegisterAnswer(
            success=True,
            status=f"User создан. Код отпарвлен. {code}"
        )

    except ValueError as e:
        await userService.session.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        await userService.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))