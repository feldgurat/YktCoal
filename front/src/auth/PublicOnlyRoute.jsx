// src/auth/PublicOnlyRoute.jsx
import { useSelector } from 'react-redux';
import { Navigate, Outlet } from 'react-router-dom';

import { selectAuthStatus } from '../store/authSlice';

// Оборачивает /login и /register — страницы, куда авторизованному
// попадать не надо. Решает задачу «залогиненный может снова войти
// в другой аккаунт»: его просто редиректит в /profile.
export default function PublicOnlyRoute() {
  const status = useSelector(selectAuthStatus);

  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="font-montserrat">Загрузка...</p>
      </div>
    );
  }

  if (status === 'authenticated') {
    return <Navigate to="/profile" replace />;
  }

  return <Outlet />;
}
