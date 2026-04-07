import { useState } from 'react';
import PhoneForm from './PhoneForm';
import CodeForm from './CodeForm';
import RegisterForm from './RegisterForm';

function AuthModal({ isOpen, onClose, onSuccess }) {
    const [step, setStep] = useState('phone'); // 'phone', 'register', 'code'
    const [phone, setPhone] = useState(null);
    const [code, setCode] = useState(null);

    const handleLoginCodeSent = (data) => {
        setPhone(data.userPhone || data.phone);
        setCode(data.debug_code);
        setStep('code');
    };

    const handleRegisterSuccess = (data) => {
        setPhone(data.userPhone || data.phone);
        setCode(data.message);
        setStep('code');
    };

    const handleLogin = (tokens) => {
        // Здесь можно сохранить токены и данные пользователя (если нужно)
        // Пока просто закрываем модалку и вызываем onSuccess
        // localStorage.setItem('access_token', tokens.access_token);
        // localStorage.setItem('refresh_token', tokens.refresh_token);
        onSuccess(tokens);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center ">
            <div className="absolute inset-0 bg-black-900/40 backdrop-blur-sm" onClick={onClose} />
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
                {step === 'code' && (
                <CodeForm phone={phone} expectedCode={code} onLogin={handleLogin} />
                )}
            </div>
        </div>
    );
    }

export default AuthModal;