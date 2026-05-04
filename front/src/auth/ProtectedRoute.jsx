import { useSelector } from 'react-redux';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { selectAuthStatus } from '../store/authSlice';

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
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
