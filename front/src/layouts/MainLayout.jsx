// src/layouts/MainLayout.jsx
import { Outlet } from 'react-router-dom';
import { Header } from '../components/Header'
import { Footer } from '../components/Footer'

const MainLayout = () => {
  return (
    <>
      <Header />
      <main>
        <Outlet />  {/* Сюда подставятся компоненты страниц */}
      </main>
      <Footer />
    </>
  );
};

export default MainLayout;