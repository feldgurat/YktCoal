import { useEffect } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { useDispatch } from 'react-redux';

import './App.css';
import MainLayout from './layouts/MainLayout';
import { Landing } from './pages/Landing';
import { Orders } from './pages/Orders';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import DriverCabinet from './pages/DriverCabinet';
import BecomeDriver from './pages/BecomeDriver';

import ProtectedRoute from './auth/ProtectedRoute';
import PublicOnlyRoute from './auth/PublicOnlyRoute';
import { bootstrapAuth } from './store/authSlice';

function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(bootstrapAuth());
  }, [dispatch]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />

        <Route element={<PublicOnlyRoute />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/orders" element={<Orders />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/driver" element={<DriverCabinet />} />
            <Route path="/become-driver" element={<BecomeDriver />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
