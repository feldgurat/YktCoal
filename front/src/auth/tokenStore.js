// src/auth/tokenStore.js
// Access-токен живёт только в памяти JS — не в localStorage и не в cookie.
// Это защищает его от XSS (скрипт на странице не сможет его вытащить из Storage).
// При перезагрузке страницы токен теряется, но это не страшно: при старте
// приложения AuthProvider дергает /auth/refresh (refresh-кука отправляется
// браузером автоматически) и получает новый access.

let accessToken = null;

export const getAccessToken = () => accessToken;

export const setAccessToken = (token) => {
  accessToken = token;
};

export const clearAccessToken = () => {
  accessToken = null;
};
