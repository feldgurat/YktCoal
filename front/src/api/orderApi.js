// Клиент Order-сервиса (заказы, предложения, ресурсы).
import { createApiClient } from './client';
import { ORDER_BASE_URL } from './endpoints';

const orderApi = createApiClient(ORDER_BASE_URL);

export default orderApi;
