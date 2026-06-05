import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';

import './index.css';
import App from './App.jsx';
import { setOnUnauthorized } from './api';
import { store } from './store';
import { setGuest } from './store/authSlice';

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
