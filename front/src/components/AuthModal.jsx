import { useState } from 'react';
import { useDispatch } from 'react-redux';

import PhoneForm from './PhoneForm';
import CodeForm from './CodeForm';
import RegisterForm from './RegisterForm';
import { login } from '../store/authSlice';

function AuthModal({ isOpen, onClose, onSuccess }) {
  const dispatch = useDispatch();
  const [step, setStep] = useState('phone');
  const [phone, setPhone] = useState(null);
  const [error, setError] = useState('');

  const handleLoginCodeSent = (data) => {
    setPhone(data.userPhone || data.phone);
    setStep('code');
  };

  const handleRegisterSuccess = (data) => {
    setPhone(data.userPhone || data.phone);
    setStep('code');
  };

  const handleLogin = async (tokens) => {
    try {
      await dispatch(login(tokens.access_token)).unwrap();
      onSuccess?.(tokens);
      onClose();
    } catch (err) {
      console.error('Не удалось войти:', err);
      setError('Не удалось войти. Попробуйте ещё раз.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center ">
      <div
        className="absolute inset-0 bg-black-900/40 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="bg-white rounded-lg shadow-xl w-96 p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
        >
          <strong>✕</strong>
        </button>
        {step === 'phone' && (
          <>
            <PhoneForm onCodeSent={handleLoginCodeSent} />
            <div className="mt-4 text-center">
              <button
                onClick={() => setStep('register')}
                className="text-sm text-blue-600 hover:underline"
              >
                Нет аккаунта? Зарегистрироваться
              </button>
            </div>
          </>
        )}
        {step === 'register' && (
          <>
            <RegisterForm onRegSuccess={handleRegisterSuccess} />
            <div className="mt-4 text-center">
              <button
                onClick={() => setStep('phone')}
                className="text-sm text-blue-600 hover:underline"
              >
                Уже есть аккаунт? Войти
              </button>
            </div>
          </>
        )}
        {step === 'code' && <CodeForm phone={phone} onLogin={handleLogin} />}
        {error && (
          <p className="mt-3 text-center text-red-600 text-sm">{error}</p>
        )}
      </div>
    </div>
  );
}

export default AuthModal;
