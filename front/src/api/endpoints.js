// src/api/endpoints.js

// Базовый URL User-сервиса
export const BASE_URL = 'http://localhost:8000';

// Базовый URL Order-сервиса
export const ORDER_BASE_URL = 'http://localhost:8001';

// Эндпоинты авторизации (User-сервис)
export const AUTH = {
  SEND_CODE: '/api/v1/auth/sign-in-code-request',
  VERIFY_CODE: '/api/v1/auth/sign-in-code-answer',
  REFRESH: '/api/v1/auth/refresh',
  REGISTER: '/api/v1/auth/register',
  LOGOUT: '/api/v1/auth/logout',
};

// Эндпоинты пользователей (User-сервис)
export const USERS = {
  GET_ME: '/api/v1/users/me',
};

// Эндпоинты заказов (Order-сервис)
export const ORDERS = {
  CREATE: '/api/v1/orders',
  MY: '/api/v1/orders/my',
  GET_BY_ID: (id) => `/api/v1/orders/${id}`,
  UPDATE: (id) => `/api/v1/orders/${id}`,
  CANCEL: (id) => `/api/v1/orders/${id}/cancel`,
};

// Эндпоинты ресурсов (Order-сервис)
export const RESOURCES = {
  LIST: '/api/v1/resources',
  GET_BY_ID: (id) => `/api/v1/resources/${id}`,
};

// Эндпоинты предложений (Order-сервис)
export const OFFERS = {
  BY_ORDER: (orderId) => `/api/v1/orders/${orderId}/offers`,
  ACCEPT: (offerId) => `/api/v1/offers/${offerId}/accept`,
  REJECT: (offerId) => `/api/v1/offers/${offerId}/reject`,
};
