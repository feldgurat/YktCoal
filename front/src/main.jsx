// src/main.jsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';

import './index.css';
import App from './App.jsx';
import { setOnUnauthorized } from './api';
import { store } from './store';
import { setGuest } from './store/authSlice';

// Связываем axios-интерцептор со store: когда /refresh окончательно
// провалился, api.js дёргает onUnauthorized() — мы диспатчим setGuest,
// и UI сам переедет на /login через PublicOnlyRoute/ProtectedRoute.
//
// Делаем это здесь, а не внутри React-дерева: store уже создан, и
// нам не нужны хуки или жизненный цикл компонентов — просто один
// раз при загрузке модуля регистрируем колбэк.
setOnUnauthorized(() => {
  store.dispatch(setGuest());
});

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </StrictMode>,
);
