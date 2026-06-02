// src/App.jsx
import { useEffect } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { useDispatch } from 'react-redux';

import './App.css';
import MainLayout from './layouts/MainLayout';
import { Landing } from './pages/Landing';
import { Test } from './pages/Test';
import { Orders } from './pages/Orders';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';

import ProtectedRoute from './auth/ProtectedRoute';
import PublicOnlyRoute from './auth/PublicOnlyRoute';
import { bootstrapAuth } from './store/authSlice';

function App() {
  const dispatch = useDispatch();

  // Тихий вход при старте приложения. StrictMode в dev запустит этот
  // эффект дважды, но createAsyncThunk в bootstrapAuth настроен с
  // condition — второй dispatch не выполнится, пока первый в полёте.
  useEffect(() => {
    dispatch(bootstrapAuth());
  }, [dispatch]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Лендинг доступен всем — логика кнопки «Войти» внутри страницы. */}
        <Route path="/" element={<Landing />} />

        {/* Только для неавторизованных: если залогинен — редирект на /profile */}
        <Route element={<PublicOnlyRoute />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* Только для авторизованных: если не залогинен — редирект на /login */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/test" element={<Test />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/profile" element={<Profile />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
