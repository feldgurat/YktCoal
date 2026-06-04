import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

import api from '../api';
import { AUTH, USERS } from '../api/endpoints';
import { clearAccessToken, setAccessToken } from '../auth/tokenStore';

// ── Async thunks ─────────────────────────────────────────────────
//
// createAsyncThunk автоматически генерирует три экшена для каждого:
// pending / fulfilled / rejected. Их подбирает extraReducers ниже.
//

// Тихий вход при старте приложения. Дёргает /refresh — refresh-кука
// летит автоматически. Если кука валидна — получаем access-токен,
// затем грузим профиль /users/me. Возвращаемое значение становится
// payload'ом fulfilled-экшена.
export const bootstrapAuth = createAsyncThunk(
  'auth/bootstrap',
  async () => {
    const { data } = await api.post(AUTH.REFRESH);
    setAccessToken(data.access_token);
    const me = await api.get(USERS.GET_ME);
    return me.data;
  },
  {
    // condition вызывается ПЕРЕД pending-экшеном. Если вернуть false,
    // thunk не выполнится — даже pending не диспатчнется.
    //
    // Решает гонку с React.StrictMode в dev-режиме: StrictMode
    // намеренно запускает useEffect дважды, чтобы ловить баги. Без
    // condition мы бы получили ДВА параллельных /refresh, и второй
    // упал бы с 401 (бэк ротирует refresh-токен — старый токен из
    // второго запроса уже в blacklist'е после первого).
    //
    // Здесь мы проверяем: если первый thunk уже в полёте (status
    // === 'loading') — второй просто не запускаем.
    condition: (_arg, { getState }) => {
      const { auth } = getState();
      if (auth.status === 'loading' && auth.bootstrapInFlight) {
        return false;
      }
    },
  },
);

// Вход после успешного ввода SMS-кода. На входе access_token из
// тела ответа /sign-in-code-answer. Refresh-кука уже стоит у браузера.
export const login = createAsyncThunk('auth/login', async (accessToken) => {
  setAccessToken(accessToken);
  const me = await api.get(USERS.GET_ME);
  return me.data;
});

// Выход: говорим бэку забыть сессию (он добавит refresh-токен в
// blacklist и удалит куку) и чистим клиентское состояние. Если бэк
// не ответил — всё равно чистим локально.
export const logout = createAsyncThunk('auth/logout', async () => {
  try {
    await api.post(AUTH.LOGOUT);
  } catch {
    // игнорируем — клиентский logout важнее
  }
  clearAccessToken();
});

// ── Slice ────────────────────────────────────────────────────────

const initialState = {
  status: 'loading', // 'loading' | 'authenticated' | 'guest'
  user: null,
  bootstrapInFlight: false, // вспомогательный флаг для condition выше
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  // Обычные синхронные reducers — для редких случаев, когда нужно
  // обновить состояние без сетевого запроса (например, api-интерцептор
  // получил неудачный refresh и хочет сбросить нас в guest).
  reducers: {
    setGuest(state) {
      state.status = 'guest';
      state.user = null;
      clearAccessToken();
    },
    setUser(state, action) {
      state.user = action.payload;
    },
  },
  // extraReducers реагируют на экшены, генерируемые createAsyncThunk.
  // Здесь мы просто декларативно описываем, как меняется state на
  // каждый этап жизни запроса.
  extraReducers: (builder) => {
    builder
      // bootstrap
      .addCase(bootstrapAuth.pending, (state) => {
        state.status = 'loading';
        state.bootstrapInFlight = true;
      })
      .addCase(bootstrapAuth.fulfilled, (state, action) => {
        state.status = 'authenticated';
        state.user = action.payload;
        state.bootstrapInFlight = false;
      })
      .addCase(bootstrapAuth.rejected, (state) => {
        state.status = 'guest';
        state.user = null;
        state.bootstrapInFlight = false;
      })
      // login
      .addCase(login.fulfilled, (state, action) => {
        state.status = 'authenticated';
        state.user = action.payload;
      })
      .addCase(login.rejected, (state) => {
        // Ошибка после ввода SMS-кода — редкий случай, но обрабатываем:
        // сбрасываем токен и переводим в guest, чтобы UI не залип.
        state.status = 'guest';
        state.user = null;
        clearAccessToken();
      })
      // logout
      .addCase(logout.fulfilled, (state) => {
        state.status = 'guest';
        state.user = null;
      });
  },
});

export const { setGuest, setUser } = authSlice.actions;

// ── Селекторы ────────────────────────────────────────────────────
// Селекторы — хорошая практика: компоненты не лезут руками в форму
// state.auth.*, а подписываются через селектор. Если завтра форма
// state поменяется (например, появится feature-флаг внутри auth) —
// поправим только селекторы, компоненты останутся как есть.

export const selectAuthStatus = (state) => state.auth.status;
export const selectUser = (state) => state.auth.user;
export const selectIsAuthenticated = (state) =>
  state.auth.status === 'authenticated';
export const selectIsAuthLoading = (state) => state.auth.status === 'loading';

export default authSlice.reducer;
