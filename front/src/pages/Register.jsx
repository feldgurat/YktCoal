import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';

import CodeForm from '../components/CodeForm';
import RegisterForm from '../components/RegisterForm';
import { login } from '../store/authSlice';

function Register() {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [step, setStep] = useState('register');
  const [phone, setPhone] = useState(null);
  const [error, setError] = useState('');

  const handleCodeSent = (data) => {
    setPhone(data.userPhone);
    setStep('code');
  };

  const handleLoginAfterCode = async (tokens) => {
    try {
      await dispatch(login(tokens.access_token)).unwrap();
      navigate('/profile', { replace: true });
    } catch (err) {
      console.error('Не удалось войти после регистрации:', err);
      setError(
        'Регистрация прошла, но не удалось войти. Попробуйте со страницы входа.',
      );
    }
  };

  return (
    <div
      className="flex items-center justify-center min-h-screen
        bg-gradient-to-br from-[#DAEAFF] via-[#DAEAFF] to-[#9BA3AD]"
    >
      <div
        className="bg-white w-80
                shadow-[0_0_33px_7px_rgba(0,0,0,0.25)] rounded-[11px] p-6"
      >
        {step === 'register' && <RegisterForm onRegSuccess={handleCodeSent} />}
        {step === 'code' && (
          <CodeForm phone={phone} onLogin={handleLoginAfterCode} />
        )}
        {error && (
          <p className="mt-3 text-center text-red-600 text-sm">{error}</p>
        )}
        <div className="mt-4 text-center">
          <Link to="/login" className="text-sm text-blue-600 hover:underline">
            Уже есть аккаунт? Войти
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
