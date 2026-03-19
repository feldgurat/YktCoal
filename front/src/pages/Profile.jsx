// pages/Profile.jsx
import { useEffect, useState } from 'react';
import api from '../api'; // ваш настроенный axios instance

function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await api.get('/api/my_profile');
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
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">
        Добро пожаловать, {user?.name || 'пользователь'}!
      </h1>
      <div className="bg-white shadow rounded-lg p-6 max-w-md">
        <p><span className="font-semibold">Имя:</span> {user?.name}</p>
        <p><span className="font-semibold">Телефон:</span> {user?.contactNumber}</p>
        <p><span className="font-semibold">Telegram ID:</span> {user?.telegramUserId}</p>
      </div>
    </div>
  );
}

export default Profile;