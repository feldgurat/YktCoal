// src/pages/Landing.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

import bgImage from '../assets/coal2.jpg';
import bgImage2 from '../assets/coal3.jpg';
import lightImage from '../assets/light.png';
import { Footer } from '../components/Footer';
import AuthModal from '../components/AuthModal';
import { selectIsAuthenticated } from '../store/authSlice';

const ArrowRight = ({ className = 'w-5 h-5' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14M13 5l7 7-7 7" />
  </svg>
);
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
const ClockIcon = ({ className = 'w-5 h-5' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <path d="M12 6v6l4 2" />
  </svg>
);
const TelegramIcon = ({ className = 'w-5 h-5' }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.89-.86.2-1.3l15.97-6.16c.73-.33 1.43.18 1.15 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42z" />
  </svg>
);

export const Landing = () => {
  const navigate = useNavigate();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const [showModal, setShowModal] = useState(false);

  const handleAuthSuccess = () => {
    navigate('/profile');
  };

  const steps = [
    {
      n: '01',
      title: 'Войдите в систему',
      text: 'Войдите в нашу систему с вашим номером телефона и подтвердите его СМС-сообщением',
      meta: 'Займёт 1 минуту',
    },
    {
      n: '02',
      title: 'Создайте заявку',
      text: 'Заполните необходимые данные о вашем заказе и отправьте заявку на обработку',
      meta: 'Уголь · объём · адрес',
    },
    {
      n: '03',
      title: 'Доставка и оплата',
      text: 'После подтверждения заявки доставляем уголь в указанное место. Оплата производится по факту получения',
      meta: 'В день заказа',
    },
  ];

  // Если уже залогинен → сразу в профиль; иначе → открываем модалку.
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
      
      <section
        id="howitworks"
        className="relative w-full bg-cover bg-center py-28"
        style={{ backgroundImage: `url(${bgImage2})` }}
      >
        <div className="absolute inset-0 bg-black/75"></div>

        <div className="relative z-10 max-w-[1280px] mx-auto px-10">
          {/* заголовок */}
          <div className="flex flex-col items-center text-center gap-3">
            <a className="font-dela text-[44px] text-white">Как это работает?</a>
            <hr className="border-none h-1 bg-blue-500 w-50" />
          </div>

          {/* шаги */}
          <div className="mt-16 grid md:grid-cols-3 gap-px bg-white/10 rounded-2xl overflow-hidden border border-white/10">
            {steps.map((s, i) => (
              <div
                key={s.n}
                className="relative bg-black/60 backdrop-blur-sm p-10 group hover:bg-black/70 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <span
                    className="font-dela text-[88px] leading-none"
                    style={{
                      WebkitTextStroke: '1.5px rgba(255,255,255,0.75)',
                      color: 'transparent',
                    }}
                  >
                    {s.n}
                  </span>
                  <span className="font-montserrat text-[12px] tracking-[0.2em] uppercase text-blue-400 inline-flex items-center gap-2 mt-3">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                    Шаг {i + 1}
                  </span>
                </div>

                <h3 className="font-['Dela_Gothic_One'] text-[24px] text-white mt-8 leading-[1.2]">
                  {s.title}
                </h3>
                <p className="font-montserrat text-white/70 text-[17px] mt-4 leading-relaxed">
                  {s.text}
                </p>

                <div className="mt-8 pt-5 border-t border-white/10 flex items-center justify-between">
                  <span className="font-montserrat text-[12px] tracking-wider uppercase text-white/40">
                    {s.meta}
                  </span>
                  {i < 2 && <ArrowRight className="w-5 h-5 text-white/30 hidden md:block" />}
                </div>

                {/* hover-акцент слева */}
                <div className="absolute left-0 top-0 h-full w-[3px] bg-blue-500 scale-y-0 group-hover:scale-y-100 origin-top transition-transform duration-300"></div>
              </div>
            ))}
          </div>

          {/* CTA-стрип */}
          <div className="mt-14 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 bg-white/[0.04] border border-white/10 rounded-2xl p-7">
            <div>
              <h4 className="font-['Dela_Gothic_One'] text-white text-[22px] leading-tight">
                Готовы оформить доставку?
              </h4>
              <p className="font-montserrat text-white/60 text-[15px] mt-2">
                Заявка занимает меньше минуты. Связь через сайт или Telegram-бота.
              </p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <Link
                to="/Test"
                className="font-montserrat font-semibold text-[20px] px-6 py-3 rounded-[10px] bg-blue-500 text-white hover:bg-[#3d90fc] transition-all hover:scale-105 inline-flex items-center gap-2"
              >
                Сделать заказ <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="#"
                className="font-montserrat font-semibold text-[18px] px-5 py-3 rounded-[10px] border border-white/20 text-white hover:bg-white/10 transition-colors inline-flex items-center gap-2"
              >
                <TelegramIcon className="w-5 h-5" />
                В Telegram-бот
              </a>
            </div>
          </div>
        </div>
      </section>

      <section id="contact" className="w-full bg-white py-28">
        <div className="max-w-[1280px] mx-auto px-10">
          <div className="flex flex-col items-center text-center gap-3">
            <a className="font-dela text-[44px]">Остались вопросы?</a>
            <hr className="border-none h-1 bg-blue-500 w-50" />
            <p className="font-montserrat text-black/60 text-[18px] mt-4 max-w-xl">
              Напишите нам — менеджер ответит в рабочие часы. Срочные заказы — звонком или в Telegram.
            </p>
          </div>

          <div className="mt-16 grid lg:grid-cols-5 rounded-[20px] overflow-hidden shadow-[0_0_33px_7px_rgba(0,0,0,0.20)] border border-black/5">
            <div
              className="lg:col-span-2 relative bg-cover bg-center text-white p-10"
              style={{ background: 'radial-gradient(ellipse at top, #1a1a1a 0%, #0a0a0a 60%, #000 100%)' }}
            >
              <div className="absolute inset-0 bg-black/75"></div>

              <div className="relative z-10 flex flex-col gap-8 h-full">
                <div>
                  <span className="font-montserrat text-[12px] tracking-[0.2em] uppercase text-blue-400">
                    Прямой контакт
                  </span>
                  <h3 className="font-['Dela_Gothic_One'] text-[26px] leading-[1.2] mt-3">
                    Свяжитесь напрямую
                  </h3>
                </div>

                <ul className="flex flex-col gap-5">
                  <li className="flex items-start gap-4">
                    <div className="w-11 h-11 rounded-[10px] bg-white/5 border border-white/10 grid place-items-center text-blue-400 shrink-0">
                      <PhoneIcon />
                    </div>
                    <div>
                      <div className="font-montserrat text-[11px] uppercase tracking-wider text-white/40">
                        Телефон
                      </div>
                      <a
                        href="tel:+79219123912"
                        className="block mt-1 font-montserrat font-semibold text-[18px] text-white hover:text-blue-300 transition-colors"
                      >
                        +7 (9219123) 912 12 12
                      </a>
                    </div>
                  </li>
                  <li className="flex items-start gap-4">
                    <div className="w-11 h-11 rounded-[10px] bg-white/5 border border-white/10 grid place-items-center text-blue-400 shrink-0">
                      <MailIcon />
                    </div>
                    <div>
                      <div className="font-montserrat text-[11px] uppercase tracking-wider text-white/40">
                        Почта
                      </div>
                      <a
                        href="mailto:infocoalyit@mail.ru"
                        className="block mt-1 font-montserrat font-semibold text-[18px] text-white hover:text-blue-300 transition-colors"
                      >
                        infocoalyit@mail.ru
                      </a>
                    </div>
                  </li>
                  <li className="flex items-start gap-4">
                    <div className="w-11 h-11 rounded-[10px] bg-white/5 border border-white/10 grid place-items-center text-blue-400 shrink-0">
                      <ClockIcon />
                    </div>
                    <div>
                      <div className="font-montserrat text-[11px] uppercase tracking-wider text-white/40">
                        Время работы
                      </div>
                      <div className="mt-1 font-montserrat text-[16px] text-white">
                        Круглосуточно · 24/7
                      </div>
                    </div>
                  </li>
                </ul>

                <a
                  href="#"
                  className="mt-auto inline-flex items-center gap-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-[10px] px-4 py-3 transition-colors"
                >
                  <TelegramIcon className="w-5 h-5 text-blue-400" />
                  <span className="font-montserrat text-[15px]">Написать в Telegram-бота</span>
                  <ArrowRight className="w-4 h-4 ml-auto text-white/40" />
                </a>
              </div>
            </div>

            {/* ПРАВО — форма */}
            <div className="lg:col-span-3 bg-white p-10 lg:p-12">
              <div className="flex items-baseline justify-between flex-wrap gap-2">
                <h3 className="font-['Dela_Gothic_One'] text-[28px] text-black leading-[1.2]">
                  Напишите нам
                </h3>
                <span className="font-montserrat text-[12px] tracking-widest uppercase text-black/40">
                  Ответим в течение часа
                </span>
              </div>
              <p className="font-montserrat text-black/60 text-[16px] mt-2">
                Оставьте контакты и свой вопрос.
              </p>

              <form className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label htmlFor="name" className="block font-montserrat text-[13px] font-semibold text-black/70">
                    Имя
                  </label>
                  <input
                    id="name"
                    type="text"
                    placeholder="Ваше имя"
                    className="mt-1.5 w-full rounded-[10px] border border-gray-200 bg-white px-4 py-3 font-montserrat text-[16px] text-black placeholder:text-black/30 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition"
                  />
                </div>
                <div>
                  <label htmlFor="phone" className="block font-montserrat text-[13px] font-semibold text-black/70">
                    Номер телефона
                  </label>
                  <input
                    id="phone"
                    type="tel"
                    placeholder="+7 (___) ___ __ __"
                    className="mt-1.5 w-full rounded-[10px] border border-gray-200 bg-white px-4 py-3 font-montserrat text-[16px] text-black placeholder:text-black/30 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label htmlFor="email" className="block font-montserrat text-[13px] font-semibold text-black/70">
                    Электронная почта
                  </label>
                  <input
                    id="email"
                    type="email"
                    placeholder="example@mail.com"
                    className="mt-1.5 w-full rounded-[10px] border border-gray-200 bg-white px-4 py-3 font-montserrat text-[16px] text-black placeholder:text-black/30 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label htmlFor="msg" className="block font-montserrat text-[13px] font-semibold text-black/70">
                    Сообщение
                  </label>
                  <textarea
                    id="msg"
                    rows={5}
                    placeholder="Задайте свой вопрос здесь"
                    className="mt-1.5 w-full rounded-[10px] border border-gray-200 bg-white px-4 py-3 font-montserrat text-[16px] text-black placeholder:text-black/30 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition resize-none"
                  ></textarea>
                </div>

                <div className="sm:col-span-2 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <label className="flex items-center gap-2.5 font-montserrat text-[13px] text-black/60 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="w-4 h-4 rounded border-gray-300 text-blue-500 focus:ring-blue-400"
                    />
                    <span>
                      Согласен на обработку{' '}
                      <a href="#" className="underline decoration-gray-300 underline-offset-2 hover:text-black">
                        персональных данных
                      </a>
                    </span>
                  </label>
                  <button
                    type="button"
                    className="font-montserrat font-semibold text-[20px] px-6 py-3 rounded-[10px] bg-blue-500 text-white hover:bg-[#3d90fc] transition-all hover:scale-105 inline-flex items-center justify-center gap-2"
                  >
                    Отправить <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>
      <Footer />
      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={handleAuthSuccess}
      />
    </>
  );
};
