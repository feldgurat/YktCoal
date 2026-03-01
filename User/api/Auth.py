from fastapi import APIRouter, HTTPException, status
import httpx

from data.Database import SessionDep
from data.schemas.Person import PersonCreate
from data.schemas.User import UserReadFull
from services.PersonService import add_new_person
from services.UserService import add_new_user


router = APIRouter()


EXOLVE_API_URL = "https://api.exolve.ru/messaging/v1/SendSMS"
EXOLVE_API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJRV05sMENiTXY1SHZSV29CVUpkWjVNQURXSFVDS0NWODRlNGMzbEQtVHA0In0.eyJleHAiOjIwODcxOTAwNzksImlhdCI6MTc3MTgzMDA3OSwianRpIjoiNzM1YTZjYTktY2Y0Yi00ZDljLTk0MWItYzkzN2E5NDU5YjFhIiwiaXNzIjoiaHR0cHM6Ly9zc28uZXhvbHZlLnJ1L3JlYWxtcy9FeG9sdmUiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiYmNkMjFlYTUtYTQ0Ny00MWQ4LTk2ZTgtN2FmMWE2NTc0OGU3IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYzk5NjJkNjUtYzdiZC00YzU0LWFkZDItNTBlY2U1ZDU2NDk5Iiwic2Vzc2lvbl9zdGF0ZSI6IjQ4ZTVjN2Y1LTI2MWYtNGMzNi04ZDQzLTA1ZDVhNDIwYTc4OCIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1leG9sdmUiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJleG9sdmVfYXBwIHByb2ZpbGUgZW1haWwiLCJzaWQiOiI0OGU1YzdmNS0yNjFmLTRjMzYtOGQ0My0wNWQ1YTQyMGE3ODgiLCJ1c2VyX3V1aWQiOiI1MzI1N2FkMy1mNzVkLTQ0MmUtYWUwMS1jNDhlMGZjNDNmOTAiLCJjbGllbnRIb3N0IjoiMTcyLjE2LjE2MS4xOSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SWQiOiJjOTk2MmQ2NS1jN2JkLTRjNTQtYWRkMi01MGVjZTVkNTY0OTkiLCJhcGlfa2V5Ijp0cnVlLCJhcGlmb25pY2Ffc2lkIjoiYzk5NjJkNjUtYzdiZC00YzU0LWFkZDItNTBlY2U1ZDU2NDk5IiwiYmlsbGluZ19udW1iZXIiOiIxMzU3Njc0IiwiYXBpZm9uaWNhX3Rva2VuIjoiYXV0ZWRiYzZjYjgtNGNiYy00YzUzLThlYTEtMGJjZGFmM2NkNjZiIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LWM5OTYyZDY1LWM3YmQtNGM1NC1hZGQyLTUwZWNlNWQ1NjQ5OSIsImN1c3RvbWVyX2lkIjoiMTU1Njg4IiwiY2xpZW50QWRkcmVzcyI6IjE3Mi4xNi4xNjEuMTkifQ.fXlQNRyi4c7lzvjHGj2XWNkiumRgJ1QIhuU4sCsUKZvV6KBkTNB1JefWY6pBnLphSjyMLzHOBLryFqj-0IJcxn3naLFN8_38Bm4Ai5CE417Ltv2YYIiby4G-JZ03wxls4TOOn8BVChAtwWNNknhA1EGluIgjCxs5PfdmYqjkZUy0bifRAUtVxfY20KYqOaAOVcrd72IkZ48y1DZPeaEx8-hc69lz95CHNCTFk7LmSMJQt5yeV4Jgl-vYKIIWk5Q6PA6ktDfL09vOjvdn3sXaB8GK37LHuq-Ci6sMGmniaDAWUdKh-kkhoDwwL5hE0UKdf7OtWK1lf_DLOl2OrUguZA"  # используйте os.getenv("EXOLVE_API_KEY")


@router.post("/send-sms")
async def send_sms():
    payload = {
        "number": "79587363725",
        "text": "Test",
        "destination": "79644191716"
    }

    headers = {
        "Authorization": f"Bearer {EXOLVE_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                EXOLVE_API_URL,
                json=payload,
                headers=headers,
                timeout=10.0 
            )
            response.raise_for_status()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="API Exolve не ответил вовремя")
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Ошибка от Exolve: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")
    return {"status": "success", "data": response.json()}


@router.post("/register", response_model=UserReadFull, status_code=status.HTTP_201_CREATED)
async def register(user: PersonCreate, session: SessionDep):
    try:
        new_person = await add_new_person(user, session)
        new_user = await add_new_user(new_person, session)
        new = new_person.model_dump()
        new["address"] = new_user.model_dump()["address"]
        await session.commit()
        return new
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=409, detail=str(e))