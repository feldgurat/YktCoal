// components/PhoneForm.jsx
import { useState } from 'react';
import api from '../api';
import { Link } from "react-router-dom"

function PhoneForm({ onCodeSent }) {
    const [phone, setPhone] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await api.post('/auth/sign-in-code-request', { phone });
    // Добавляем исходный номер в объект, который передаём в onCodeSent
        onCodeSent({ 
        ...response.data,   // то, что вернул бэкенд (может быть code, session_id и т.д.)
        userPhone: phone    // исходный номер, который ввёл пользователь
        });
        } catch (err) {
            const message = err.response?.data?.detail || 'Ошибка при отправке кода';
            setError(message);
        } finally {
        setLoading(false);
        }
    };

return (
    <form onSubmit={handleSubmit} className='text-center items-center flex flex-col gap-5'>
        <a className='font-dela text-[40px]'>    
            <Link to="/">УгольЯкт</Link>
        </a>
        <h2 className='font-montserrat font-semibold'>Вход по номеру телефона</h2>
        <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Введите номер"
            required
            className='font-montserrat bg-gray-200 p-1 rounded-[3px] focus:outline-none focus:ring-0'
        />
        <button type="submit" disabled={loading} className='font-semibold font-montserrat bg-blue-500 text-white
        px-2 py-2 rounded-[8px]'>
            {loading ? 'Отправка...' : 'Получить код'}
        </button>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <Link className='font-montserrat' to="/">Вернуться</Link>
    </form>
);
}

export default PhoneForm;