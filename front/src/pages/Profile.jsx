// pages/Profile.jsx
import { useNavigate } from 'react-router-dom';
import MapComponent from '../components/MapComponent';
import { useAuth } from '../auth/AuthContext';

function Profile() {
  // AuthProvider уже загрузил пользователя при старте или после логина —
  // здесь просто берём его из контекста. Отдельный fetch /users/me не нужен.
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="p-8 mx-20">
      <h1 className="text-3xl font-bold mb-6">
        Добро пожаловать, {user?.name || 'пользователь'}!
      </h1>
      <div className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-6 max-w-md">
        <p>
          <span className="font-semibold">Имя:</span> {user?.name}
        </p>
        <p>
          <span className="font-semibold">Телефон:</span> {user?.contact_number}
        </p>
        <button
          className="text-red-500 font-semibold hover:underline mt-2"
          onClick={handleLogout}
        >
          Выйти
        </button>
      </div>
      <MapComponent />
    </div>
  );
}

export default Profile;
