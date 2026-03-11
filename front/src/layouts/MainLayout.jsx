// src/layouts/MainLayout.jsx
import { Outlet } from 'react-router-dom';
import { Header } from '../components/Header'
import { Footer } from '../components/Footer'
import './MainLayout.css'; // создадим этот файл

const MainLayout = () => {
  return (
    <>
    <div className="layout">
      <Header />
      <main className="layout-main">
        <Outlet />
      </main>
      <Footer />
    </div>
    </>
  );
};

export default MainLayout;