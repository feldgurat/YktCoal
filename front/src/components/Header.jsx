// src/components/Header.jsx
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';

import { logout } from '../store/authSlice';

export const Header = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await dispatch(logout());
    navigate('/login', { replace: true });
  };

  return (
    <header className="w-full bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] fixed py-4 z-40">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
        <div className="flex flex-col">
          <span className="font-['Dela_Gothic_One'] text-4xl text-black leading-none">
            <Link to="/">УгольЯкт</Link>
          </span>
        </div>

        <nav className="flex gap-8 items-center">
          <Link
            to="/orders"
            className="font-montserrat font-semibold text-lg text-black hover:underline underline-offset-4"
          >
            Мои заказы
          </Link>
          <Link
            to="/profile"
            className="font-montserrat font-semibold text-lg text-black hover:underline underline-offset-4"
          >
            Профиль
          </Link>

        </nav>
      </div>
    </header>
  );
};
