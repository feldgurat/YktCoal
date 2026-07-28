import { useState } from 'react';
import api from '../api';
import { Link } from "react-router-dom";
import { AUTH } from '../api/endpoints'

function RegisterForm({ onRegSuccess }) {
    const [name, setName] = useState('');
    const [phone, setPhone] = useState('');
    const [address, setAddress] = useState('');

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await api.post(AUTH.REGISTER, {
                name,
                contact_number: phone,
                telegram_user_id: null,
                address: address.trim() || null });

        onRegSuccess({ 
        ...response.data,
        userPhone: phone
        });

        } catch (err) {
            const getErrorMessage = (error) => {
                if (error.response) {
                    const { data, status } = error.response;
                    if (status === 422 && data.detail) {
                        if (Array.isArray(data.detail)) {
                            const firstError = data.detail[0];
                            return `Ошибка в поле "${firstError.loc.join('.')}": ${firstError.msg}`;
                        } else if (typeof data.detail === 'string') {
                            return data.detail;
                        } else {
                            return JSON.stringify(data.detail);
                        }
                    }
                    if (data.detail) {
                        return typeof data.detail === 'string' 
                        ? data.detail 
                        : JSON.stringify(data.detail);
                    }
                }
                return err.message || 'Произошла ошибка. Попробуйте снова.';
            };
            setError(getErrorMessage(err));
        } finally {
        setLoading(false);
        }
    };

return (
    <form onSubmit={handleSubmit} className='text-center items-center flex flex-col gap-5'>
        <a className='font-dela text-[40px]'>    
            <Link to="/">УгольЯкт</Link>
        </a>
        <h2 className='font-montserrat font-semibold'>Регистрация</h2>
        <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Введите ИМЯ"
            required
            className='font-montserrat bg-gray-200 p-1 rounded-[3px] focus:outline-none focus:ring-0'
        />
        <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Введите номер"
            required
            className='font-montserrat bg-gray-200 p-1 rounded-[3px] focus:outline-none focus:ring-0'
        />
        <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Введите адрес (необязательно)"
            className='font-montserrat bg-gray-200 p-1 rounded-[3px] focus:outline-none focus:ring-0'
        />
        <button type="submit" disabled={loading} className='font-semibold font-montserrat bg-blue-500 text-white
        px-2 py-2 rounded-[8px]'>
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
        {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
);
}

export default RegisterForm;