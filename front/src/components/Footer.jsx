import { Link } from "react-router-dom"
export const Footer = () => {
  return (
    <footer className="w-full bg-[#434343] h-[140px] shadow-[0_4px_4px_8px_rgba(0,0,0,0.25)] text-white">
      <div className="max-w-7xl mx-auto px-4 h-full flex items-center justify-between">
        {/* Left column: Contact info with icons */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-300"></div>
            <span className="font-montserrat text-xs text-white">
              село Тулагино, ул. Аргунова, Александра
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-300"></div>
            <span className="font-montserrat text-xs text-white">
              +7 (9219123) 912912 12383
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-300"></div>
            <span className="font-montserrat text-xs text-white">
              infocoalykt@mail.ru
            </span>
          </div>
        </div>

        {/* Middle-left column: White links */}
        <div className="space-y-2">
          <a href="#" className="block font-montserrat text-xs text-white hover:underline underline-offset-4">
            <Link to="/login">Войти в систему</Link>
          </a>
          <a href="#" className="block font-montserrat text-xs text-white hover:underline underline-offset-4">
            Контакты
          </a>
          <a href="#" className="block font-montserrat text-xs text-white hover:underline underline-offset-4">
            Документы
          </a>
        </div>

        {/* Middle-right column: Gray links */}
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

        {/* Right column: Logo and subtitle */}
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
