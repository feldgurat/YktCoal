// src/pages/Login.jsx
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';

import PhoneForm from '../components/PhoneForm';
import CodeForm from '../components/CodeForm';
import { login } from '../store/authSlice';

function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();

  const [step, setStep] = useState('phone');
  const [phone, setPhone] = useState(null);
  const [code, setCode] = useState(null);
  const [loginError, setLoginError] = useState('');

  const handleCodeSent = (data) => {
    setPhone(data.userPhone);
    setCode(data.debug_code);
    setStep('code');
  };

  // tokens = ответ /sign-in-code-answer = { access_token }
  // refresh-кука к этому моменту уже стоит у браузера.
  const handleLogin = async (tokens) => {
    try {
      // .unwrap() превращает результат thunk'а в обычный промис:
      // если thunk зарезолвился — получим payload, если упал —
      // нормальное исключение. Без unwrap thunk всегда «успешен»
      // с точки зрения dispatch (он возвращает action), и ошибки
      // придётся ловить через .meta.requestStatus — это менее удобно.
      await dispatch(login(tokens.access_token)).unwrap();
      const redirectTo = location.state?.from?.pathname || '/profile';
      navigate(redirectTo, { replace: true });
    } catch (err) {
      console.error('Не удалось загрузить профиль после входа:', err);
      setLoginError('Не удалось войти. Попробуйте ещё раз.');
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
        {step === 'phone' && <PhoneForm onCodeSent={handleCodeSent} />}
        {step === 'code' && (
          <CodeForm phone={phone} expectedCode={code} onLogin={handleLogin} />
        )}
        {loginError && (
          <p className="mt-3 text-center text-red-600 text-sm">{loginError}</p>
        )}
        <div className="mt-4 text-center">
          <Link to="/register" className="text-sm text-blue-600 hover:underline">
            Нет аккаунта? Зарегистрироваться
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
