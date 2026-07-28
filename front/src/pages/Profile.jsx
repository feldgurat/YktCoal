import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';

import {
  logout,
  selectIsDriver,
  selectUser,
  updateProfile,
} from '../store/authSlice';

const ROLE_LABELS = {
  user: 'Заказчик',
  driver: 'Водитель',
  admin: 'Администратор',
};

function Profile() {
  const user = useSelector(selectUser);
  const isDriver = useSelector(selectIsDriver);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [editing, setEditing] = useState(false);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  const startEditing = () => {
    setName(user?.name ?? '');
    setPhone(user?.contact_number ?? '');
    setAddress(user?.address ?? '');
    setError('');
    setSaved(false);
    setEditing(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    const fields = {};
    if (name !== user?.name) fields.name = name;
    if (phone !== user?.contact_number) fields.contact_number = phone;
    if ((address || null) !== (user?.address || null)) {
      fields.address = address.trim() || null;
    }

    try {
      if (Object.keys(fields).length > 0) {
        await dispatch(updateProfile(fields)).unwrap();
      }
      setEditing(false);
      setSaved(true);
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Не удалось сохранить');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    await dispatch(logout());
    navigate('/login', { replace: true });
  };

  const roles = user?.roles ?? [];

  return (
    <div className="p-8 mx-20 font-montserrat">
      <h1 className="text-3xl font-bold mb-6 font-dela">
        Добро пожаловать, {user?.name || 'пользователь'}!
      </h1>

      <div className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-6 max-w-md">
        {saved && !editing && (
          <p className="mb-3 text-sm text-green-700 bg-green-50 border border-green-200 rounded-md p-2">
            Профиль сохранён
          </p>
        )}

        {!editing ? (
          <>
            <div className="flex flex-col gap-2 text-sm">
              <p>
                <span className="font-semibold">Имя:</span> {user?.name}
              </p>
              <p>
                <span className="font-semibold">Телефон:</span>{' '}
                {user?.contact_number}
              </p>
              <p>
                <span className="font-semibold">Адрес:</span>{' '}
                {user?.address || 'не указан'}
              </p>
              <p className="flex items-center gap-2 flex-wrap">
                <span className="font-semibold">Роли:</span>
                {roles.map((r) => (
                  <span
                    key={r}
                    className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800"
                  >
                    {ROLE_LABELS[r] ?? r}
                  </span>
                ))}
              </p>
            </div>

            <div className="flex items-center gap-4 mt-4">
              <button
                className="text-blue-500 font-semibold hover:underline"
                onClick={startEditing}
              >
                Редактировать
              </button>
              <button
                className="text-red-500 font-semibold hover:underline"
                onClick={handleLogout}
              >
                Выйти
              </button>
            </div>
          </>
        ) : (
          <form onSubmit={handleSave} className="flex flex-col gap-3">
            {error && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
                {error}
              </p>
            )}

            <label className="text-sm">
              <span className="font-semibold block mb-1">Имя</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full bg-gray-100 p-2 rounded-md border border-gray-300
                          focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>

            <label className="text-sm">
              <span className="font-semibold block mb-1">Телефон</span>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
                className="w-full bg-gray-100 p-2 rounded-md border border-gray-300
                          focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>

            <label className="text-sm">
              <span className="font-semibold block mb-1">Адрес</span>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Не указан"
                className="w-full bg-gray-100 p-2 rounded-md border border-gray-300
                          focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>

            <div className="flex items-center gap-4 mt-1">
              <button
                type="submit"
                disabled={saving}
                className="font-semibold text-white bg-blue-500 px-4 py-2 rounded-lg
                          hover:bg-blue-600 transition-colors
                          disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? 'Сохранение...' : 'Сохранить'}
              </button>
              <button
                type="button"
                onClick={() => setEditing(false)}
                className="font-semibold text-gray-500 hover:underline"
              >
                Отмена
              </button>
            </div>
          </form>
        )}
      </div>

      {!isDriver && (
        <div className="mt-6 max-w-md bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-900">
            Хотите возить уголь и зарабатывать?{' '}
            <Link
              to="/become-driver"
              className="font-semibold underline hover:no-underline"
            >
              Станьте водителем
            </Link>
          </p>
        </div>
      )}
    </div>
  );
}

export default Profile;
