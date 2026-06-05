import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';

import MapComponent from '../components/MapComponent';
import { logout, selectUser } from '../store/authSlice';

function Profile() {
  const user = useSelector(selectUser);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await dispatch(logout());
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
    </div>
  );
}

export default Profile;
