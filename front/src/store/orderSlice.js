import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

import orderApi from '../api/orderApi';
import { ORDERS, RESOURCES, OFFERS } from '../api/endpoints';
import { mapOffer, mapOrder, mapResource } from '../api/mappers';

const errorDetail = (err, fallback) => {
  const detail = err.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join('; ');
  return fallback;
};

export const fetchResources = createAsyncThunk(
  'orders/fetchResources',
  async () => {
    const { data } = await orderApi.get(RESOURCES.LIST);
    return data.map(mapResource);
  },
);

export const fetchMyOrders = createAsyncThunk(
  'orders/fetchMyOrders',
  async () => {
    const { data } = await orderApi.get(ORDERS.MY);
    return data.map(mapOrder);
  },
);

export const createOrder = createAsyncThunk(
  'orders/createOrder',
  async (orderData, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(ORDERS.CREATE, orderData);
      return mapOrder(data);
    } catch (err) {
      return rejectWithValue(errorDetail(err, 'Ошибка при создании заявки'));
    }
  },
);

export const cancelOrder = createAsyncThunk(
  'orders/cancelOrder',
  async (orderId, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(ORDERS.CANCEL(orderId));
      return mapOrder(data);
    } catch (err) {
      return rejectWithValue(errorDetail(err, 'Не удалось отменить заявку'));
    }
  },
);

export const fetchOrderOffers = createAsyncThunk(
  'orders/fetchOrderOffers',
  async (orderId) => {
    const { data } = await orderApi.get(OFFERS.BY_ORDER(orderId));
    return { orderId, offers: data.map(mapOffer) };
  },
);

export const acceptOffer = createAsyncThunk(
  'orders/acceptOffer',
  async ({ offerId, orderId }, { rejectWithValue }) => {
    try {
      const { data: orderDto } = await orderApi.post(
        OFFERS.ACCEPT(orderId, offerId),
      );
      const { data: offersDto } = await orderApi.get(OFFERS.BY_ORDER(orderId));
      return {
        orderId,
        order: mapOrder(orderDto),
        offers: offersDto.map(mapOffer),
      };
    } catch (err) {
      return rejectWithValue(errorDetail(err, 'Не удалось принять предложение'));
    }
  },
);

export const rejectOffer = createAsyncThunk(
  'orders/rejectOffer',
  async ({ offerId, orderId }, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(OFFERS.REJECT(orderId, offerId));
      return { orderId, offer: mapOffer(data) };
    } catch (err) {
      return rejectWithValue(errorDetail(err, 'Не удалось отклонить предложение'));
    }
  },
);

const initialState = {
  resources: [],
  resourcesStatus: 'idle',

  orders: [],
  ordersStatus: 'idle',

  createStatus: 'idle',
  createError: null,

  offersByOrder: {},
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

      .addCase(createOrder.pending, (state) => {
        state.createStatus = 'loading';
        state.createError = null;
      })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.createStatus = 'succeeded';
        state.orders.unshift(action.payload);
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.createStatus = 'failed';
        state.createError = action.payload || 'Неизвестная ошибка';
      })

      .addCase(cancelOrder.fulfilled, (state, action) => {
        const updated = action.payload;
        const idx = state.orders.findIndex((o) => o.id === updated.id);
        if (idx !== -1) {
          state.orders[idx] = updated;
        }
      })

      .addCase(fetchOrderOffers.pending, (state, action) => {
        const orderId = action.meta.arg;
        state.offersByOrder[orderId] = {
          ...(state.offersByOrder[orderId] || {}),
          status: 'loading',
        };
      })
      .addCase(fetchOrderOffers.fulfilled, (state, action) => {
        const { orderId, offers } = action.payload;
        state.offersByOrder[orderId] = {
          status: 'succeeded',
          offers,
          error: null,
        };
      })
      .addCase(fetchOrderOffers.rejected, (state, action) => {
        const orderId = action.meta.arg;
        state.offersByOrder[orderId] = {
          status: 'failed',
          offers: [],
          error: 'Не удалось загрузить предложения',
        };
      })

      .addCase(acceptOffer.fulfilled, (state, action) => {
        const { orderId, order, offers } = action.payload;
        state.offersByOrder[orderId] = {
          status: 'succeeded',
          offers,
          error: null,
        };
        const idx = state.orders.findIndex((o) => o.id === orderId);
        if (idx !== -1) {
          state.orders[idx] = order;
        }
      })

      .addCase(rejectOffer.fulfilled, (state, action) => {
        const { orderId, offer } = action.payload;
        const cached = state.offersByOrder[orderId];
        if (cached?.offers) {
          cached.offers = cached.offers.map((o) =>
            o.id === offer.id ? offer : o,
          );
        }
      });
  },
});

export const { resetCreateStatus } = orderSlice.actions;

export const selectResources = (state) => state.orders.resources;
export const selectResourcesStatus = (state) => state.orders.resourcesStatus;
export const selectMyOrders = (state) => state.orders.orders;
export const selectOrdersStatus = (state) => state.orders.ordersStatus;
export const selectCreateStatus = (state) => state.orders.createStatus;
export const selectCreateError = (state) => state.orders.createError;
export const selectOffersByOrder = (orderId) => (state) =>
  state.orders.offersByOrder[orderId] || {
    status: 'idle',
    offers: [],
    error: null,
  };

export default orderSlice.reducer;
