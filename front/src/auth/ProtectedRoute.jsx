import { useSelector } from 'react-redux';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { selectAuthStatus } from '../store/authSlice';

// Оборачивает страницы, доступные только авторизованному пользователю.
// Если статус ещё 'loading' — показываем заглушку, чтобы не моргнуть
// редиректом, пока bootstrapAuth ещё в полёте.
export default function ProtectedRoute() {
  const status = useSelector(selectAuthStatus);
  const location = useLocation();

  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="font-montserrat">Загрузка...</p>
      </div>
    );
  }

  if (status === 'guest') {
    // Запоминаем, куда юзер хотел попасть — после логина вернём.
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
