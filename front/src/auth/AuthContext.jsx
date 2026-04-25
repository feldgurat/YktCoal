// src/auth/AuthContext.jsx
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useReducer,
} from 'react';

import api, { setOnUnauthorized } from '../api';
import { AUTH, USERS } from '../api/endpoints';
import { clearAccessToken, setAccessToken } from './tokenStore';

// Состояние:
//   status: 'loading'       — при старте пытаемся тихо войти через /refresh
//           'authenticated' — есть валидный access и пользователь загружен
//           'guest'         — не авторизован
//   user:   данные /users/me или null
const initialState = {
  status: 'loading',
  user: null,
};

function authReducer(state, action) {
  switch (action.type) {
    case 'AUTH_SUCCESS':
      return { status: 'authenticated', user: action.user };
    case 'AUTH_GUEST':
      return { status: 'guest', user: null };
    case 'SET_USER':
      return { ...state, user: action.user };
    default:
      return state;
  }
}

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Регистрируем глобальный хэндлер: если api.js не смог обновить токен,
  // он дёрнет этот колбэк, и мы переведём состояние в 'guest'.
  useEffect(() => {
    setOnUnauthorized(() => {
      clearAccessToken();
      dispatch({ type: 'AUTH_GUEST' });
    });
  }, []);

  // Тихий вход при старте приложения.
  // Refresh-кука отправляется браузером автоматически — если она
  // живая, получим новый access и сразу загрузим профиль.
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const { data } = await api.post(AUTH.REFRESH);
        if (cancelled) return;
        setAccessToken(data.access_token);

        const me = await api.get(USERS.GET_ME);
        if (cancelled) return;
        dispatch({ type: 'AUTH_SUCCESS', user: me.data });
      } catch {
        if (cancelled) return;
        dispatch({ type: 'AUTH_GUEST' });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  // Вызывается из формы логина/регистрации после успешного
  // /sign-in-code-answer. На входе — access_token из тела ответа.
  // Refresh-кука к этому моменту уже установлена бэком.
  const login = useCallback(async (accessToken) => {
    setAccessToken(accessToken);
    const me = await api.get(USERS.GET_ME);
    dispatch({ type: 'AUTH_SUCCESS', user: me.data });
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post(AUTH.LOGOUT);
    } catch {
      // Даже если сервер не ответил — очищаем клиентское состояние.
      // Бэк всё равно увидит старую куку как невалидную после истечения.
    }
    clearAccessToken();
    dispatch({ type: 'AUTH_GUEST' });
  }, []);

  const updateUser = useCallback((user) => {
    dispatch({ type: 'SET_USER', user });
  }, []);

  const value = useMemo(
    () => ({
      status: state.status,
      user: state.user,
      isAuthenticated: state.status === 'authenticated',
      isLoading: state.status === 'loading',
      login,
      logout,
      updateUser,
    }),
    [state, login, logout, updateUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth должен использоваться внутри <AuthProvider>');
  }
  return ctx;
}
