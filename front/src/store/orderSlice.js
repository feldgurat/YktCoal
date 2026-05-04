// src/store/orderSlice.js
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

import orderApi from '../api/orderApi';
import { ORDERS, RESOURCES } from '../api/endpoints';

// ── Async thunks ─────────────────────────────────────────────────

// Загрузить список ресурсов (типы угля) — нужны для формы создания заявки.
export const fetchResources = createAsyncThunk(
  'orders/fetchResources',
  async () => {
    const { data } = await orderApi.get(RESOURCES.LIST);
    return data;
  },
);

// Загрузить заявки текущего пользователя.
export const fetchMyOrders = createAsyncThunk(
  'orders/fetchMyOrders',
  async () => {
    const { data } = await orderApi.get(ORDERS.MY);
    return data;
  },
);

// Создать новую заявку.
export const createOrder = createAsyncThunk(
  'orders/createOrder',
  async (orderData, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(ORDERS.CREATE, orderData);
      return data;
    } catch (err) {
      const detail = err.response?.data?.detail;
      return rejectWithValue(
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((d) => d.msg).join('; ')
            : 'Ошибка при создании заявки',
      );
    }
  },
);

// Отменить заявку.
export const cancelOrder = createAsyncThunk(
  'orders/cancelOrder',
  async (orderId, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(ORDERS.CANCEL(orderId));
      return data;
    } catch (err) {
      const detail = err.response?.data?.detail;
      return rejectWithValue(
        typeof detail === 'string' ? detail : 'Не удалось отменить заявку',
      );
    }
  },
);

// ── Slice ────────────────────────────────────────────────────────

const initialState = {
  resources: [],
  resourcesStatus: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'

  orders: [],
  ordersStatus: 'idle',

  createStatus: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  createError: null,
};

const orderSlice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    resetCreateStatus(state) {
      state.createStatus = 'idle';
      state.createError = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // ── fetchResources ──
      .addCase(fetchResources.pending, (state) => {
        state.resourcesStatus = 'loading';
      })
      .addCase(fetchResources.fulfilled, (state, action) => {
        state.resourcesStatus = 'succeeded';
        state.resources = action.payload;
      })
      .addCase(fetchResources.rejected, (state) => {
        state.resourcesStatus = 'failed';
      })

      // ── fetchMyOrders ──
      .addCase(fetchMyOrders.pending, (state) => {
        state.ordersStatus = 'loading';
      })
      .addCase(fetchMyOrders.fulfilled, (state, action) => {
        state.ordersStatus = 'succeeded';
        state.orders = action.payload;
      })
      .addCase(fetchMyOrders.rejected, (state) => {
        state.ordersStatus = 'failed';
      })

      // ── createOrder ──
      .addCase(createOrder.pending, (state) => {
        state.createStatus = 'loading';
        state.createError = null;
      })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.createStatus = 'succeeded';
        // Добавляем новый заказ в начало списка
        state.orders.unshift(action.payload);
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.createStatus = 'failed';
        state.createError = action.payload || 'Неизвестная ошибка';
      })

      // ── cancelOrder ──
      .addCase(cancelOrder.fulfilled, (state, action) => {
        const updated = action.payload;
        const idx = state.orders.findIndex((o) => o.id === updated.id);
        if (idx !== -1) {
          state.orders[idx] = updated;
        }
      });
  },
});

export const { resetCreateStatus } = orderSlice.actions;

// ── Селекторы ────────────────────────────────────────────────────
export const selectResources = (state) => state.orders.resources;
export const selectResourcesStatus = (state) => state.orders.resourcesStatus;
export const selectMyOrders = (state) => state.orders.orders;
export const selectOrdersStatus = (state) => state.orders.ordersStatus;
export const selectCreateStatus = (state) => state.orders.createStatus;
export const selectCreateError = (state) => state.orders.createError;

export default orderSlice.reducer;
