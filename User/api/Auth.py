from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status

from data.Database import SessionDep
from data.schemas.Auth import RefreshIn, SmsCodeRequestAnswer, SmsRequestIn, SmsVerifyIn, TokenPair
from services.AuthService import OTP_TTL_SECONDS, add_new_sms_code, add_token_to_blacklist, create_access_token, create_refresh_token, decode_token, generate_code, get_actual_sms_code, hash_code, invalide_old_codes, is_token_blacklisted, normalize_phone, resending_prot, send_sms_via_exolve
from services.Exeptions import InvalidToken, InvalidTokenType, OtpRateLimitError, TokenHasExpired
from services.PersonService import get_person_by_id, get_person_by_number, is_user_exist_by_number



router = APIRouter()



@router.post("/auth/sign-in-code-request"
             #, response_model=SmsCodeRequestAnswer
             )
async def sms_code_request(
    data: SmsRequestIn,
    session: SessionDep,
):
    try:
        phone = normalize_phone(data.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not await is_user_exist_by_number(phone, session):
        raise HTTPException(status_code=409, detail="Пользователя с таким номером нет в системе")
        

    try:
        await resending_prot(phone, session)
    except Exception as e:
        if isinstance(e, OtpRateLimitError):
            raise HTTPException(status_code=429, detail="Попробуйте запросить код чуть позже")
        raise
    

    code = generate_code()
    code_hash = hash_code(phone, code)
    expires_at = datetime.utcnow() + timedelta(seconds=OTP_TTL_SECONDS)

    text = f"Ваш код подтверждения: {code}"

    # сначала отправляем SMS
    # await send_sms_via_exolve(destination=phone, text=text)

    await invalide_old_codes(phone, session)

    await add_new_sms_code(phone, code_hash, expires_at, session)
    await session.commit()

    return {"status": "ok", "message": "Код отправлен", "code": code}


@router.post("/auth/sign-in-code-answer", response_model=TokenPair)
async def sms_code_answer(
    data: SmsVerifyIn,
    session: SessionDep,
):
    try:
        phone = normalize_phone(data.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = await get_person_by_number(phone, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    sms_code = await get_actual_sms_code(phone, session)
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
    
    if sms_code.code_hash != hash_code(phone, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код",
        )

    # одноразовый код -> помечаем использованным / инвалидируем
    await invalide_old_codes(phone, session)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(
        user_id=str(user.id),
        version=user.token_version,   # поле в БД
    )

    await session.commit()

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.post("/auth/refresh", response_model=TokenPair)
async def refresh_tokens(
    data: RefreshIn,
    session: SessionDep,
):
    try:
        payload = decode_token(data.refresh_token, expected_type="refresh")
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
    token_version = payload.get("ver")

    # 1. check blacklist
    if await is_token_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Токен отозван")

    user = await get_person_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    # 2. check version
    if token_version != user.token_version:
        raise HTTPException(status_code=401, detail="Токен устарел")

    # 3. rotate refresh token: старый в blacklist
    exp_ts = payload["exp"]
    await add_token_to_blacklist(jti=jti, exp_ts=exp_ts)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id), user.token_version)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )