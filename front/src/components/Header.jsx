import { Link } from "react-router-dom"

export const Header = () => {
  return (
    <>
      <header className="w-full bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] fixed py-4">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
          {/* Left: Logo and subtitle */}
          <div className="flex flex-col">
            <a className="font-['Dela_Gothic_One'] text-4xl text-black leading-none">
              <Link to="/">УгольЯкт</Link>
            </a>
          </div>

          {/* Right: Navigation */}
          <nav className="flex gap-8">
            <a href="#" className="font-montserrat font-semibold text-lg text-black hover:underline underline-offset-4">
              <Link to="/requests">Мои заявки</Link>
            </a>
            <a href="#" className="font-montserrat font-semibold text-lg text-black hover:underline underline-offset-4">
              <Link to="/orders">Мои заказы</Link>
            </a>
            <a href="#" className="font-montserrat font-semibold text-lg text-black hover:underline underline-offset-4тз">
              <Link to="/profile">Профиль</Link>
            </a>
          </nav>
        </div>
      </header>
    </>
  )
}
