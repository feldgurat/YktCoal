// src/api.js
import axios from 'axios';
import { AUTH } from './api/endpoints';
import {
  getAccessToken,
  setAccessToken,
  clearAccessToken,
} from './auth/tokenStore';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  // Критически важно: без этого браузер не отправит HttpOnly cookie
  // с refresh-токеном на кросс-доменные запросы (фронт и бэк на разных портах).
  withCredentials: true,
});

// ── Request: подставляем Authorization из памяти ─────────────────
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Refresh-очередь ──────────────────────────────────────────────
// Если access протух, несколько параллельных запросов могут одновременно
// получить 401. Без очереди они бы все рванули рефрешить — это и лишняя
// нагрузка, и риск: каждый рефреш инвалидирует предыдущий (см. бэк —
// token_version увеличивается при каждом refresh). Поэтому:
//   — первый 401 запускает один рефреш
//   — остальные кладутся в очередь и ждут его результата
//   — после успеха они повторяют свой запрос с новым токеном

let isRefreshing = false;
let waiters = [];

const notifyWaiters = (err) => {
  waiters.forEach(({ resolve, reject }) => {
    if (err) reject(err);
    else resolve();
  });
  waiters = [];
};

// AuthProvider регистрирует сюда свой колбэк, чтобы мы могли
// сбросить состояние аутентификации, если рефреш провалился.
// Это развязывает api.js и AuthContext (нет циклической зависимости).
let onUnauthorized = () => {};
export const setOnUnauthorized = (cb) => {
  onUnauthorized = cb;
};

// ── Response: обрабатываем 401, пытаемся обновить access ─────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Не трогаем 401 от самого /refresh — иначе уйдём в бесконечный цикл.
    const isRefreshCall = originalRequest?.url?.endsWith(AUTH.REFRESH);

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !isRefreshCall
    ) {
      // Если рефреш уже идёт — встаём в очередь
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          waiters.push({ resolve, reject });
        }).then(() => {
          originalRequest.headers.Authorization = `Bearer ${getAccessToken()}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Вызываем рефреш чистым axios (не через `api`), чтобы не ловить
        // этот же response-интерсептор рекурсивно.
        // Тело пустое — refresh-токен бэк читает из HttpOnly cookie.
        const { data } = await axios.post(
          `${API_BASE_URL}${AUTH.REFRESH}`,
          {},
          { withCredentials: true },
        );

        setAccessToken(data.access_token);
        notifyWaiters(null);

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshErr) {
        notifyWaiters(refreshErr);
        clearAccessToken();
        // Сообщаем AuthProvider'у: пользователь больше не авторизован.
        // Он переведёт состояние в 'guest', а ProtectedRoute сделает редирект.
        onUnauthorized();
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default api;
