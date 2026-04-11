import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PhoneForm from '../components/PhoneForm';
import CodeForm from '../components/CodeForm';

function Login() {
    const navigate = useNavigate();
    const [step, setStep] = useState('phone'); 
    const [phone, setPhone] = useState(null);
    const [code, setCode] = useState(null);

    const handleCodeSent = (data) => {
        setPhone(data.userPhone);
        setCode(data.debug_code);
        setStep('code');
    };

    const handleLogin = (tokens) => {
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        navigate('/profile');
    };

    return (
        <div className='flex items-center justify-center min-h-screen
        bg-gradient-to-br from-[#DAEAFF] via-[#DAEAFF] to-[#9BA3AD]'>
                <div className="bg-white w-80 
                shadow-[0_0_33px_7px_rgba(0,0,0,0.25)] rounded-[11px] p-6">
                    {step === 'phone' && <PhoneForm onCodeSent={handleCodeSent} />}
                    {step === 'code' && (
                        <CodeForm phone={phone} expectedCode={code} onLogin={handleLogin} />
                    )}
                </div>
        </div>
    );
}

export default Login;