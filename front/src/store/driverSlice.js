// Водительский стейт: доступные заказы, мои предложения, назначенные
// заказы (Order-сервис) и заявка на роль водителя + техника (Driver-сервис).
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

import orderApi from '../api/orderApi';
import driverApi from '../api/driverApi';
import { APPLICATIONS, DRIVERS, OFFERS, ORDERS } from '../api/endpoints';
import {
  mapApplication,
  mapOffer,
  mapOrder,
  mapVehicle,
} from '../api/mappers';

const errorDetail = (err, fallback) => {
  const detail = err.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join('; ');
  return fallback;
};

// ── Заказы (Order-сервис, роль driver) ───────────────────────────

export const fetchAvailableOrders = createAsyncThunk(
  'driver/fetchAvailableOrders',
  async () => {
    const { data } = await orderApi.get(ORDERS.AVAILABLE);
    return data.map(mapOrder);
  },
);

export const fetchMyDriverOrders = createAsyncThunk(
  'driver/fetchMyDriverOrders',
  async () => {
    const { data } = await orderApi.get(ORDERS.DRIVER_MY);
    return data.map(mapOrder);
  },
);

export const startOrder = createAsyncThunk(
  'driver/startOrder',
  async (orderId, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(ORDERS.START(orderId));
      return mapOrder(data);
    } catch (err) {
      return rejectWithValue(errorDetail(err, 'Не удалось начать выполнение'));
    }
  },
);

export const driverWithdrawOrder = createAsyncThunk(
  'driver/driverWithdrawOrder',
  async (orderId, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(ORDERS.DRIVER_WITHDRAW(orderId));
      return mapOrder(data);
    } catch (err) {
      return rejectWithValue(
        errorDetail(err, 'Не удалось отказаться от заказа'),
      );
    }
  },
);

// ── Мои предложения ──────────────────────────────────────────────

export const fetchMyOffers = createAsyncThunk(
  'driver/fetchMyOffers',
  async () => {
    const { data } = await orderApi.get(OFFERS.MY);
    return data.map(mapOffer);
  },
);

export const createOffer = createAsyncThunk(
  'driver/createOffer',
  async (payload, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(OFFERS.CREATE, payload);
      return mapOffer(data);
    } catch (err) {
      return rejectWithValue(
        errorDetail(err, 'Не удалось отправить предложение'),
      );
    }
  },
);

export const withdrawOffer = createAsyncThunk(
  'driver/withdrawOffer',
  async (offerId, { rejectWithValue }) => {
    try {
      const { data } = await orderApi.post(OFFERS.WITHDRAW(offerId));
      return mapOffer(data);
    } catch (err) {
      return rejectWithValue(
        errorDetail(err, 'Не удалось отозвать предложение'),
      );
    }
  },
);

// ── Заявка на роль водителя (Driver-сервис) ──────────────────────

export const fetchMyApplications = createAsyncThunk(
  'driver/fetchMyApplications',
  async () => {
    const { data } = await driverApi.get(APPLICATIONS.MY);
    return data.map(mapApplication);
  },
);

export const submitApplication = createAsyncThunk(
  'driver/submitApplication',
  async (payload, { rejectWithValue }) => {
    try {
      const { data } = await driverApi.post(APPLICATIONS.CREATE, payload);
      return mapApplication(data);
    } catch (err) {
      return rejectWithValue(errorDetail(err, 'Не удалось отправить заявку'));
    }
  },
);

// ── Техника ──────────────────────────────────────────────────────

export const fetchMyVehicles = createAsyncThunk(
  'driver/fetchMyVehicles',
  async () => {
    const { data } = await driverApi.get(DRIVERS.MY_VEHICLES);
    return data.map(mapVehicle);
  },
);

export const addVehicle = createAsyncThunk(
  'driver/addVehicle',
  async (payload, { rejectWithValue }) => {
    try {
      const { data } = await driverApi.post(DRIVERS.MY_VEHICLES, payload);
      return mapVehicle(data);
    } catch (err) {
      return rejectWithValue(errorDetail(err, 'Не удалось добавить машину'));
    }
  },
);

export const deleteVehicle = createAsyncThunk(
  'driver/deleteVehicle',
  async (vehicleId, { rejectWithValue }) => {
    try {
      await driverApi.delete(DRIVERS.MY_VEHICLE(vehicleId));
      return vehicleId;
    } catch (err) {
      return rejectWithValue(errorDetail(err, 'Не удалось удалить машину'));
    }
  },
);

// ── Slice ────────────────────────────────────────────────────────

const initialState = {
  availableOrders: [],
  availableStatus: 'idle',

  driverOrders: [],
  driverOrdersStatus: 'idle',

  myOffers: [],
  myOffersStatus: 'idle',

  applications: [],
  applicationsStatus: 'idle',
  submitStatus: 'idle',
  submitError: null,

  vehicles: [],
  vehiclesStatus: 'idle',
};

const replaceById = (list, item) => {
  const idx = list.findIndex((x) => x.id === item.id);
  if (idx !== -1) list[idx] = item;
};

const driverSlice = createSlice({
  name: 'driver',
  initialState,
  reducers: {
    resetSubmitStatus(state) {
      state.submitStatus = 'idle';
      state.submitError = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAvailableOrders.pending, (state) => {
        state.availableStatus = 'loading';
      })
      .addCase(fetchAvailableOrders.fulfilled, (state, action) => {
        state.availableStatus = 'succeeded';
        state.availableOrders = action.payload;
      })
      .addCase(fetchAvailableOrders.rejected, (state) => {
        state.availableStatus = 'failed';
      })

      .addCase(fetchMyDriverOrders.pending, (state) => {
        state.driverOrdersStatus = 'loading';
      })
      .addCase(fetchMyDriverOrders.fulfilled, (state, action) => {
        state.driverOrdersStatus = 'succeeded';
        state.driverOrders = action.payload;
      })
      .addCase(fetchMyDriverOrders.rejected, (state) => {
        state.driverOrdersStatus = 'failed';
      })

      .addCase(startOrder.fulfilled, (state, action) => {
        replaceById(state.driverOrders, action.payload);
      })
      .addCase(driverWithdrawOrder.fulfilled, (state, action) => {
        // Заказ вернулся в NEW и больше не наш.
        state.driverOrders = state.driverOrders.filter(
          (o) => o.id !== action.payload.id,
        );
      })

      .addCase(fetchMyOffers.pending, (state) => {
        state.myOffersStatus = 'loading';
      })
      .addCase(fetchMyOffers.fulfilled, (state, action) => {
        state.myOffersStatus = 'succeeded';
        state.myOffers = action.payload;
      })
      .addCase(fetchMyOffers.rejected, (state) => {
        state.myOffersStatus = 'failed';
      })

      .addCase(createOffer.fulfilled, (state, action) => {
        state.myOffers.unshift(action.payload);
      })
      .addCase(withdrawOffer.fulfilled, (state, action) => {
        replaceById(state.myOffers, action.payload);
      })

      .addCase(fetchMyApplications.pending, (state) => {
        state.applicationsStatus = 'loading';
      })
      .addCase(fetchMyApplications.fulfilled, (state, action) => {
        state.applicationsStatus = 'succeeded';
        state.applications = action.payload;
      })
      .addCase(fetchMyApplications.rejected, (state) => {
        state.applicationsStatus = 'failed';
      })

      .addCase(submitApplication.pending, (state) => {
        state.submitStatus = 'loading';
        state.submitError = null;
      })
      .addCase(submitApplication.fulfilled, (state, action) => {
        state.submitStatus = 'succeeded';
        state.applications.unshift(action.payload);
      })
      .addCase(submitApplication.rejected, (state, action) => {
        state.submitStatus = 'failed';
        state.submitError = action.payload || 'Неизвестная ошибка';
      })

      .addCase(fetchMyVehicles.pending, (state) => {
        state.vehiclesStatus = 'loading';
      })
      .addCase(fetchMyVehicles.fulfilled, (state, action) => {
        state.vehiclesStatus = 'succeeded';
        state.vehicles = action.payload;
      })
      .addCase(fetchMyVehicles.rejected, (state) => {
        state.vehiclesStatus = 'failed';
      })
      .addCase(addVehicle.fulfilled, (state, action) => {
        state.vehicles.push(action.payload);
      })
      .addCase(deleteVehicle.fulfilled, (state, action) => {
        state.vehicles = state.vehicles.filter(
          (v) => v.id !== action.payload,
        );
      });
  },
});

export const { resetSubmitStatus } = driverSlice.actions;

export const selectAvailableOrders = (state) => state.driver.availableOrders;
export const selectAvailableStatus = (state) => state.driver.availableStatus;
export const selectDriverOrders = (state) => state.driver.driverOrders;
export const selectDriverOrdersStatus = (state) =>
  state.driver.driverOrdersStatus;
export const selectMyOffers = (state) => state.driver.myOffers;
export const selectMyOffersStatus = (state) => state.driver.myOffersStatus;
export const selectApplications = (state) => state.driver.applications;
export const selectApplicationsStatus = (state) =>
  state.driver.applicationsStatus;
export const selectSubmitStatus = (state) => state.driver.submitStatus;
export const selectSubmitError = (state) => state.driver.submitError;
export const selectVehicles = (state) => state.driver.vehicles;
export const selectVehiclesStatus = (state) => state.driver.vehiclesStatus;

export default driverSlice.reducer;
