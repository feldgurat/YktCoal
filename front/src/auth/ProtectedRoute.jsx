// src/auth/ProtectedRoute.jsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

// Оборачивает страницы, на которые можно заходить только авторизованному.
// Если ещё грузим статус — показываем заглушку (чтобы не моргнуть редиректом
// на /login, когда пользователь на самом деле залогинен).
export default function ProtectedRoute() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="font-montserrat">Загрузка...</p>
      </div>
    );
  }

  if (status === 'guest') {
    // Запоминаем, куда юзер хотел попасть — после логина можно вернуть.
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
