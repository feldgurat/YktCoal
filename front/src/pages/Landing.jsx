import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import bgImage from '../assets/coal2.jpg';
import lightImage from '../assets/light.png';
import { Footer } from '../components/Footer';
import AuthModal from '../components/AuthModal';
import { useAuth } from '../auth/AuthContext';

export const Landing = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [showModal, setShowModal] = useState(false);

  // Колбэк после успешного входа через модалку.
  // Всё сохранение токенов и user state уже сделано в AuthModal → useAuth.login().
  // Здесь остаётся только редирект.
  const handleAuthSuccess = () => {
    navigate('/profile');
  };

  // Кликается кнопка «Войти в систему»:
  //   — если уже залогинен → сразу в профиль (без перелогина)
  //   — иначе → открываем модалку
  const handleAuthButtonClick = () => {
    if (isAuthenticated) {
      navigate('/profile');
    } else {
      setShowModal(true);
    }
  };

  return (
    <>
      <div
        className="h-screen w-full bg-cover bg-center bg-black"
        style={{ backgroundImage: `url(${bgImage})` }}
      >
        <div className="absolute inset-0 bg-black opacity-50"></div>
        <header className="flex items-start justify-between px-20 py-5 relative z-10">
          <div className="flex flex-col">
            <span className="font-dela text-[40px] text-white leading-tight">
              УгольЯкт
            </span>
            <span className="font-montserrat font-semibold text-lg text-white">
              Доставка угля в Якутске
            </span>
          </div>
          <nav className="flex gap-8 mt-7">
            <a
              href="#"
              className="hover:underline underline-offset-6 font-montserrat text-[20px] font-bold text-white"
            >
              Перейти в ТГ-бота
            </a>
            <button
              onClick={handleAuthButtonClick}
              className="hover:underline underline-offset-6 font-montserrat text-[20px] font-bold text-white"
            >
              {isAuthenticated ? 'Личный кабинет' : 'Войти в систему'}
            </button>
          </nav>
        </header>

        <div className="relative z-10 text-center flex flex-col items-center pt-20 justify-center gap-10">
          <a className="text-[44px] font-dela text-white block">
            УгольЯкт - Доставка угля в Якутске
          </a>
          <a
            className="
          text-shadow-lg text-shadow-black/30 text-[32px] font-montserrat font-semibold text-white"
          >
            Надежная и быстрая доставка
            <br /> качественного угля по Якутску и <br />
            пригороду. Работаем с физическими <br />и юридическими лицами
          </a>
          <a
            href="#whyus"
            className="text-[25px] font-montserrat font-semibold text-white border-2 rounded-[6px] px-6 py-2
          transition-colors duration-300 hover:bg-white hover:text-black"
          >
            Почему мы?
          </a>
        </div>
      </div>

      <div className="h-screen w-full bg-white pl-40 pr-40" id="whyus">
        <div className="text-center pt-15 items-center gap-3 flex flex-col">
          <a className="font-dela text-[44px]">Почему мы?</a>
          <hr className="border-none h-1 bg-blue-500 w-50"></hr>
        </div>
        <div className="mt-20 items-center justify-center flex gap-20">
          <div
            className="w-[317px] h-[317px] bg-white
          shadow-[0_0_33px_7px_rgba(0,0,0,0.25)] rounded-[11px]
          flex flex-col items-center gap-2"
          >
            <div
              style={{ backgroundImage: `url(${lightImage})` }}
              className="w-[42px] h-[64px] bg-contain bg-cover rounded-[2px] mt-8"
            ></div>
            <h3 className="font-['Dela_Gothic_One'] text-2xl text-center text-black">
              24/7
            </h3>
            <p className=" left-[52px] top-[140px] w-[213px] font-['Montserrat'] text-xl text-center text-black">
              Доставка осуществляется 24/7, работаем при любых погодных условиях
            </p>
          </div>

          <div
            className="w-[317px] h-[317px] bg-white
          shadow-[0_0_33px_7px_rgba(0,0,0,0.25)] rounded-[11px]
          flex flex-col items-center gap-2"
          >
            <div
              style={{ backgroundImage: `url(${lightImage})` }}
              className="w-[42px] h-[64px] bg-contain bg-cover rounded-[2px] mt-8"
            ></div>
            <h3 className="font-['Dela_Gothic_One'] text-2xl leading-[35px] text-center text-black">
              Гарантия качества
            </h3>
            <p className="font-['Montserrat'] text-xl text-center text-black">
              Гарантируем качество <br />
              всего доставляемого
              <br /> товара, весь уголь <br />
              проходит необходимую проверку
            </p>
          </div>

          <div
            className="w-[317px] h-[317px] bg-white
          shadow-[0_0_33px_7px_rgba(0,0,0,0.25)] rounded-[11px]
          flex flex-col items-center gap-2"
          >
            <div
              style={{ backgroundImage: `url(${lightImage})` }}
              className="w-[42px] h-[64px] bg-contain bg-cover rounded-[2px] mt-8"
            ></div>
            <h3 className="  font-['Dela_Gothic_One'] text-2xl leading-[35px] text-center text-black">
              Доступные цены
            </h3>
            <p className=" font-['Montserrat'] text-xl text-center text-black">
              Предоставляем самые доступные цены на
              <br /> рынке, начиная от X <br />
              рублей.
            </p>
          </div>
        </div>
        <div className="items center justify-center flex mt-20">
          <a
            href="#howitworks"
            className="font-montserrat
          font-semibold text-[24px]
          px-5 py-4 rounded-[10px] bg-blue-500 text-white
          hover:bg-[#3d90fc] transition-all hover:scale-102"
          >
            Как это работает?
          </a>
        </div>
      </div>

      <div className="h-screen w-full bg-gray-100 pl-30 pr-30" id="howitworks">
        <div className="text-center pt-15 items-center gap-3 flex flex-col">
          <a className="font-dela text-[44px]">Как это работает?</a>
          <hr className="border-none h-1 bg-blue-500 w-50"></hr>
        </div>
        <div className="items center justify-center flex mt-20">
          <a
            className="font-montserrat
          font-semibold text-[24px]
          px-5 py-4 rounded-[10px] bg-blue-500 text-white
          hover:bg-[#3d90fc] transition-all hover:scale-102"
          >
            <Link to="/Test">Сделать заказ</Link>
          </a>
        </div>
      </div>

      <Footer />
      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={handleAuthSuccess}
      />
    </>
  );
};
