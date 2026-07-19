import axios from 'axios';
import { AUTH, BASE_URL, ORDER_BASE_URL } from './endpoints';
import {
  getAccessToken,
  setAccessToken,
  clearAccessToken,
} from '../auth/tokenStore';

const orderApi = axios.create({
  baseURL: ORDER_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

orderApi.interceptors.request.use((config) => {
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

orderApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          waiters.push({ resolve, reject });
        }).then(() => {
          originalRequest.headers.Authorization = `Bearer ${getAccessToken()}`;
          return orderApi(originalRequest);
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
        return orderApi(originalRequest);
      } catch (refreshErr) {
        notifyWaiters(refreshErr);
        clearAccessToken();
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default orderApi;
