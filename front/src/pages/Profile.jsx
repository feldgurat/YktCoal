// pages/Profile.jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api'; // ваш настроенный axios instance
import { USERS, AUTH } from '../api/endpoints';
import MapComponent from '../components/MapComponent';

function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await api.get(USERS.GET_ME);
        setUser(response.data);
        console.log(response.data);
      } catch (err) {
        setError('Не удалось загрузить данные пользователя');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const handleLogout = async() => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      await api.post(AUTH.LOGOUT, { refresh_token: refresh });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
    } catch (error){
      console.error('Ошибка при выходе:', error);
      //localStorage.removeItem('access_token');
      //localStorage.removeItem('refresh_token');
      //navigate('/login');
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Загрузка...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }


  return (
    <div className="p-8 mx-20">
      <h1 className="text-3xl font-bold mb-6">
        Добро пожаловать, {user?.name || 'пользователь'}!
      </h1>
      <div className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-6 max-w-md">
        <p><span className="font-semibold">Имя:</span> {user?.name}</p>
        <p><span className="font-semibold">Телефон:</span> {user?.contact_number}</p>
        {/* <p><span className="font-semibold">Telegram ID:</span> {user?.telegram_user_id}</p> */}
        <button className='text-red-500 font-semibold hover:underline'
        onClick={handleLogout}>Выйти</button>
      </div>
      <MapComponent />
      
    </div>
  );
}

export default Profile;