export const BASE_URL =
  import.meta.env.VITE_USER_API_URL ?? 'http://localhost:8000';

export const ORDER_BASE_URL =
  import.meta.env.VITE_ORDER_API_URL ?? 'http://localhost:8001';

export const DRIVER_BASE_URL =
  import.meta.env.VITE_DRIVER_API_URL ?? 'http://localhost:8002';

// ── User-сервис ──────────────────────────────────────────────────

export const AUTH = {
  SEND_CODE: '/api/v1/auth/sign-in-code-request',
  VERIFY_CODE: '/api/v1/auth/sign-in-code-answer',
  REFRESH: '/api/v1/auth/refresh',
  REGISTER: '/api/v1/auth/register',
  LOGOUT: '/api/v1/auth/logout',
};

export const USERS = {
  GET_ME: '/api/v1/users/me',
  UPDATE_ME: '/api/v1/users/me',
};

// ── Order-сервис ─────────────────────────────────────────────────

export const ORDERS = {
  CREATE: '/api/v1/orders',
  MY: '/api/v1/orders/me',
  GET_BY_ID: (id) => `/api/v1/orders/${id}`,
  UPDATE: (id) => `/api/v1/orders/${id}`,
  CANCEL: (id) => `/api/v1/orders/${id}/cancel`,
  COMPLETE: (id) => `/api/v1/orders/${id}/complete`,
  // Водительские
  AVAILABLE: '/api/v1/orders/available/list',
  DRIVER_MY: '/api/v1/orders/driver/me',
  START: (id) => `/api/v1/orders/${id}/start`,
  DRIVER_WITHDRAW: (id) => `/api/v1/orders/${id}/driver-withdraw`,
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
  // Водительские
  CREATE: '/api/v1/offers',
  MY: '/api/v1/offers/me',
  WITHDRAW: (offerId) => `/api/v1/offers/${offerId}/withdraw`,
};

// ── Driver-сервис ────────────────────────────────────────────────

export const APPLICATIONS = {
  CREATE: '/api/v1/applications',
  MY: '/api/v1/applications/me',
  UPLOAD_DOC: '/api/v1/applications/upload-doc',
  FILE: (filename) => `/api/v1/applications/files/${filename}`,
};

export const DRIVERS = {
  ME: '/api/v1/drivers/me',
  MY_VEHICLES: '/api/v1/drivers/me/vehicles',
  MY_VEHICLE: (id) => `/api/v1/drivers/me/vehicles/${id}`,
};
