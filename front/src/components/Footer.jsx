import { Link, useNavigate } from "react-router-dom"
import { useState } from "react";
import { useSelector } from 'react-redux';
import AuthModal from '../components/AuthModal';
import { selectIsAuthenticated } from '../store/authSlice';

const PhoneIcon = ({ className = 'w-5 h-5' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z" />
  </svg>
);
const MailIcon = ({ className = 'w-5 h-5' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="4" width="20" height="16" rx="2" />
    <path d="m2 7 10 6 10-6" />
  </svg>
);
const PinIcon = ({ className = 'w-5 h-5' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);

export const Footer = () => {
  const navigate = useNavigate();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const [showModal, setShowModal] = useState(false);

  const handleAuthClick = () => {
    if (!isAuthenticated) {
      setShowModal(true);
    }
    else {
      navigate('/profile');
    }
  };

  const handleAuthSuccess = () => {
    navigate('/profile');
  };

  return (
    <footer className="w-full bg-[#000000] h-[140px] shadow-[0_4px_4px_8px_rgba(0,0,0,0.25)] ">
      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={handleAuthSuccess}
      />
      <div className="max-w-7xl mx-auto h-full flex items-center justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 text-blue-500">
              <PinIcon className="w-3 h-3 " />
            </div>
            <span className="font-montserrat text-xs text-white">
              село Тулагино, ул. Юбилейная, д. 1
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 text-blue-500">
              <PhoneIcon className="w-3 h-3 " />
            </div>
            <span className="font-montserrat text-xs text-white">
              +7 (924) 369 69 09 
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 text-blue-500">
              <MailIcon className="w-3 h-3 " />
            </div>
            <span className="font-montserrat text-xs text-white">
              infocoalykt@mail.ru
            </span>
          </div>
        </div>

        <div className="space-y-2">
          <button onClick={handleAuthClick} className="block font-montserrat text-xs text-white hover:underline underline-offset-4">
            {isAuthenticated ? 'Личный кабинет' : 'Войти в систему'}
          </button>
          <a href="#" className="block font-montserrat text-xs text-white hover:underline underline-offset-4">
            Контакты
          </a>
          <a href="#" className="block font-montserrat text-xs text-white hover:underline underline-offset-4">
            Документы
          </a>
        </div>

        <div className="space-y-2">
          <a href="#" className="block font-montserrat text-xs text-[#A1A1A1] hover:underline underline-offset-4">
            Согласие на обработку персональных данных
          </a>
          <a href="#" className="block font-montserrat text-xs text-[#A1A1A1] hover:underline underline-offset-4">
            Политика конфиденциальности
          </a>
          <a href="#" className="block font-montserrat text-xs text-[#A1A1A1] hover:underline underline-offset-4">
            Условия пользования
          </a>
        </div>

        <div className="flex flex-col items-end">
          <a href="#" className="font-['Dela_Gothic_One'] text-4xl text-white leading-none">
            УгольЯкт
          </a>
          <p className="font-montserrat font-semibold text-[18.5px] text-white mt-1">
            Доставка угля в Якутске
          </p>
        </div>
      </div>
    </footer>
  )
}
