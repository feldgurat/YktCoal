import React, { useState } from 'react';
import axios from 'axios';

const Button = () => {
    const [name, setName] = useState('');
    const [responseMessage, setResponseMessage] = useState('');
    const [error, setError] = useState('');

    // Получаем базовый URL из переменной окружения
    const API_URL = "http://127.0.0.1:8000";

    const handleSubmit = async (e) => {
        e.preventDefault(); // если используете форму
        setError('');
        setResponseMessage('');

    try {
        // Отправляем POST-запрос с данными
        const response = await axios.get(`${API_URL}/`, {
            headers: {"Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlOGViNjM4OC03MmI4LTQ3ZmUtYTZjMi04YmRjNzE0MDFjYmIiLCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzczMTI2MDQ3LCJleHAiOjE3NzMxMjY5NDcsImp0aSI6IjU1YjFlYTUyLTQ5NjItNGM3MS1hNmUyLTZjYTQwZjM0MWU4MyIsInZlciI6MH0.DVOyFgLavM9y8LiUlQBNk2W39ykyk5W5Y-mL1QFgmtI"} ,
            // data:{
            //     name: name,
            // }
        // можно добавить другие поля
        });

        // Обрабатываем успешный ответ
        setResponseMessage(`Успешно: ${response.data}`);
        console.log(response.data);
    } catch (err) {
      // Обрабатываем ошибку
      if (err.response) {
        // Сервер вернул ответ с кодом ошибки (4xx, 5xx)
        setError(`Ошибка ${err.response.status}: ${err.response.data.detail || err.message}`);
      } else if (err.request) {
        // Запрос был отправлен, но ответ не получен (например, сервер не запущен)
        setError('Сервер не отвечает. Проверьте, запущен ли бэкенд.');
      } else {
        // Что-то пошло не так при настройке запроса
        setError(`Ошибка: ${err.message}`);
      }
    }
  };

  return (
    <div>
      <h2>Отправить данные</h2>
      <form onSubmit={handleSubmit}>
        <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Введите имя"
        />
        <button type="submit">Отправить</button>
      </form>
      {responseMessage && <p style={{ color: 'green' }}>{responseMessage}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default Button;