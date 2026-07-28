// Клиент Driver-сервиса (заявки на роль водителя, профиль водителя, техника).
import { createApiClient } from './client';
import { DRIVER_BASE_URL } from './endpoints';

const driverApi = createApiClient(DRIVER_BASE_URL);

export default driverApi;
