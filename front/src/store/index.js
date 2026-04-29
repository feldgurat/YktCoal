// src/store/index.js
import { configureStore } from '@reduxjs/toolkit';

import authReducer from './authSlice';

// configureStore — рекомендуемый способ создания store в RTK.
// Он автоматически:
//   — подключает redux-thunk (для createAsyncThunk);
//   — настраивает Redux DevTools (расширение для браузера, очень
//     рекомендую поставить — оно показывает все экшены, состояние
//     и позволяет «отматывать» историю действий);
//   — добавляет дев-only middleware-чеки (мутации state, сериализуемость).
//
// Если в будущем появятся другие срезы состояния (заявки, заказы,
// уведомления), просто добавляй их в reducer-объект ниже.
export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
});
