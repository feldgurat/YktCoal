import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import { Landing } from './pages/Landing';
import { Test } from './pages/Test';
import { Orders } from './pages/Orders';
import Profile from './pages/Profile';
import { Requests } from './pages/Requests';
import Login from './pages/Login';
import Register from './pages/Register';

import ProtectedRoute from './auth/ProtectedRoute';
import PublicOnlyRoute from './auth/PublicOnlyRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Лендинг доступен всем, логика «Войти/Профиль» — внутри самой страницы */}
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
            <Route path="/requests" element={<Requests />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
