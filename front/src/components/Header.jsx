import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';

import { selectIsDriver } from '../store/authSlice';

export const Header = () => {
  const isDriver = useSelector(selectIsDriver);

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
          {isDriver ? (
            <Link
              to="/driver"
              className="font-montserrat font-semibold text-lg text-black hover:underline underline-offset-4"
            >
              Кабинет водителя
            </Link>
          ) : (
            <Link
              to="/become-driver"
              className="font-montserrat font-semibold text-lg text-black hover:underline underline-offset-4"
            >
              Стать водителем
            </Link>
          )}
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
