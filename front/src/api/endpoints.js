// src/api/endpoints.js

// Базовый URL (можно вынести в .env)
export const BASE_URL = 'http://localhost:8000';

// Эндпоинты авторизации
export const AUTH = {
  SEND_CODE: '/api/v1/auth/sign-in-code-request',          // или '/send-code'
  VERIFY_CODE: '/api/v1/auth/sign-in-code-answer',
  REFRESH: '/api/v1/auth/refresh',
  REGISTER: '/api/v1/auth/register',
  LOGOUT: '/api/v1/auth/logout'
};

// Эндпоинты пользователей
export const USERS = {
  GET_ME: '/api/v1/users/me',
  // ...
};