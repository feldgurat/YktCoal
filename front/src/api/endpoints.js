export const BASE_URL =
  import.meta.env.VITE_USER_API_URL ?? 'http://localhost:8000';

export const ORDER_BASE_URL =
  import.meta.env.VITE_ORDER_API_URL ?? 'http://localhost:8001';

export const AUTH = {
  SEND_CODE: '/api/v1/auth/sign-in-code-request',
  VERIFY_CODE: '/api/v1/auth/sign-in-code-answer',
  REFRESH: '/api/v1/auth/refresh',
  REGISTER: '/api/v1/auth/register',
  LOGOUT: '/api/v1/auth/logout',
};

export const USERS = {
  GET_ME: '/api/v1/users/me',
};

export const ORDERS = {
  CREATE: '/api/v1/orders',
  MY: '/api/v1/orders/me',
  GET_BY_ID: (id) => `/api/v1/orders/${id}`,
  UPDATE: (id) => `/api/v1/orders/${id}`,
  CANCEL: (id) => `/api/v1/orders/${id}/cancel`,
};

export const RESOURCES = {
  LIST: '/api/v1/resources',
  GET_BY_ID: (id) => `/api/v1/resources/${id}`,
};

export const OFFERS = {
  BY_ORDER: (orderId) => `/api/v1/orders/${orderId}/offers`,
  ACCEPT: (orderId, offerId) =>
    `/api/v1/orders/${orderId}/offers/${offerId}/accept`,
  REJECT: (orderId, offerId) =>
    `/api/v1/orders/${orderId}/offers/${offerId}/reject`,
};
