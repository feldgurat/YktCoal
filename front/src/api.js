// Клиент User-сервиса (auth + профиль).
// Логика перехватчиков живёт в api/client.js — общая для всех сервисов.
import { createApiClient, setOnUnauthorized } from './api/client';
import { BASE_URL } from './api/endpoints';

const api = createApiClient(BASE_URL);

export { setOnUnauthorized };
export default api;
