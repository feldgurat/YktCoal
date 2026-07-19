import axios from 'axios';
import { AUTH, BASE_URL } from './api/endpoints';
import {
  getAccessToken,
  setAccessToken,
  clearAccessToken,
} from './auth/tokenStore';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


let isRefreshing = false;
let waiters = [];

const notifyWaiters = (err) => {
  waiters.forEach(({ resolve, reject }) => {
    if (err) reject(err);
    else resolve();
  });
  waiters = [];
};

let onUnauthorized = () => {};
export const setOnUnauthorized = (cb) => {
  onUnauthorized = cb;
};

api.interceptors.response.use(
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
          return api(originalRequest);
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
        return api(originalRequest);
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

export default api;
