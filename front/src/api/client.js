// Фабрика axios-клиентов с единой логикой: Bearer-токен в каждом запросе
// и прозрачный refresh по 401 с повтором исходного запроса.
// Каждый бэкенд-сервис (User / Order / Driver) получает свой инстанс,
// но refresh всегда ходит в User-сервис.
import axios from 'axios';

import { AUTH, BASE_URL } from './endpoints';
import {
  getAccessToken,
  setAccessToken,
  clearAccessToken,
} from '../auth/tokenStore';

let onUnauthorized = () => {};
export const setOnUnauthorized = (cb) => {
  onUnauthorized = cb;
};

// Refresh общий для всех инстансов: если один клиент уже ротирует токен,
// остальные ждут его результата, а не шлют параллельный /refresh
// (бэк ротирует refresh-куку — второй запрос попал бы в blacklist).
let isRefreshing = false;
let waiters = [];

const notifyWaiters = (err) => {
  waiters.forEach(({ resolve, reject }) => {
    if (err) reject(err);
    else resolve();
  });
  waiters = [];
};

export function createApiClient(baseURL) {
  const client = axios.create({
    baseURL,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true,
  });

  client.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      const isRefreshCall = originalRequest?.url?.endsWith(AUTH.REFRESH);

      if (
        error.response?.status === 401 &&
        !originalRequest._retry &&
        !isRefreshCall
      ) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            waiters.push({ resolve, reject });
          }).then(() => {
            originalRequest.headers.Authorization = `Bearer ${getAccessToken()}`;
            return client(originalRequest);
          });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const { data } = await axios.post(
            `${BASE_URL}${AUTH.REFRESH}`,
            {},
            { withCredentials: true },
          );

          setAccessToken(data.access_token);
          notifyWaiters(null);

          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return client(originalRequest);
        } catch (refreshErr) {
          notifyWaiters(refreshErr);
          clearAccessToken();
          onUnauthorized();
          return Promise.reject(refreshErr);
        } finally {
          isRefreshing = false;
        }
      }

      return Promise.reject(error);
    },
  );

  return client;
}
