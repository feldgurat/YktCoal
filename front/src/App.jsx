import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import MainLayout from './layouts/MainLayout';
import { Landing } from './pages/Landing'
import { Test } from './pages/Test'
import { Orders } from './pages/Orders'
import { Profile } from './pages/Profile'
import { Requests } from './pages/Requests'
import { Header } from './components/Header'
import { Footer } from './components/Footer'
import Login from './pages/Login';

function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />

          <Route element={<MainLayout />}>
            <Route path="/test" element={<Test />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/requests" element={<Requests />} />
          </Route>

        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
