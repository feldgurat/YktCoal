import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import CodeForm from '../components/CodeForm';
import RegisterForm  from '../components/RegisterForm';

function Register() {
    const navigate = useNavigate();
    const [step, setStep] = useState('register'); 
    const [phone, setPhone] = useState(null);
    const [code, setCode] = useState(null);

    const handleCodeSent = (data) => {
        setPhone(data.userPhone);
        setCode(data.message);
        setStep('code');
    };

    const handleLoginAfterCode = (tokens) => {
        // Сохраняем токены после подтверждения кода
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        if (tokens.user) {
            localStorage.setItem('user', JSON.stringify(tokens.user));
        }
        // После регистрации и подтверждения кода перенаправляем в профиль
        navigate('/profile');
    };

    return (
        <div className='flex items-center justify-center min-h-screen
        bg-gradient-to-br from-[#DAEAFF] via-[#DAEAFF] to-[#9BA3AD]'>
                <div className="bg-white w-80 
                shadow-[0_0_33px_7px_rgba(0,0,0,0.25)] rounded-[11px] p-6">
                    {step === 'register' && <RegisterForm onRegSuccess={handleCodeSent} />}
                    {step === 'code' && (
                        <CodeForm 
                        phone={phone} 
                        expectedCode={code} 
                        onLogin={handleLoginAfterCode} />
                    )}
                    <div className="mt-4 text-center">
                        <Link
                            to="/login"
                            className="text-sm text-blue-600 hover:underline"
                        >
                            Уже есть аккаунт? Войти
                        </Link>
                    </div>
                </div>
        </div>
    );
}

export default Register;