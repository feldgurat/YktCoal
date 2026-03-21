# app/api/routes.py

API_PREFIX = "/api"
API_V1_PREFIX = f"{API_PREFIX}/v1"

DRIVERS = "/drivers"
ADMINS = "/admins"
PERSONS = "/persons"

AUTH = "/auth"
BY_PERSON_ID = "/{person_id}"
SEND_SIGN_IN_SMS_CODE = "/sign-in-code-request"
ANSWER_SIGN_IN_SMS_CODE = "/sign-in-code-answer"
REFRESH = "/refresh"

REGISTER = "/register"

USERS = "/users"

TELEGRAM = "/telegram"