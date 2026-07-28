import { configureStore } from '@reduxjs/toolkit';

import authReducer from './authSlice';
import orderReducer from './orderSlice';
import driverReducer from './driverSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    orders: orderReducer,
    driver: driverReducer,
  },
});
