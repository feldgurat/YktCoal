// src/components/OrderCard.jsx
import { useDispatch } from 'react-redux';
import { cancelOrder } from '../store/orderSlice';
import { useState } from 'react';

// Цвета для статусов
const STATUS_COLORS = {
  1: 'bg-blue-100 text-blue-800',     // Новый
  2: 'bg-yellow-100 text-yellow-800', // Принят
  3: 'bg-purple-100 text-purple-800', // В пути
  4: 'bg-green-100 text-green-800',   // Выполнен
  5: 'bg-gray-100 text-gray-600',     // Отменён
  6: 'bg-red-100 text-red-700',       // Отклонён
};

// Статусы, из которых можно отменить (NEW, ACCEPTED, IN_PROGRESS)
const CANCELLABLE = [1, 2, 3];

function OrderCard({ order }) {
  const dispatch = useDispatch();
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState('');

  const handleCancel = async () => {
    if (!window.confirm('Вы уверены, что хотите отменить заявку?')) return;

    setCancelling(true);
    setError('');
    try {
      await dispatch(cancelOrder(order.id)).unwrap();
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Не удалось отменить');
    } finally {
      setCancelling(false);
    }
  };

  const createdDate = order.created_at
    ? new Date(order.created_at).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '—';

  const statusColor = STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-800';

  return (
    <div className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-5 font-montserrat">
      {/* Шапка: ID-статус */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-gray-400">
          #{order.id?.slice(0, 8)}
        </span>
        <span
          className={`text-xs font-semibold px-2.5 py-1 rounded-full ${statusColor}`}
        >
          {order.status_label}
        </span>
      </div>

      {/* Основная информация */}
      <div className="flex flex-col gap-1.5 text-sm">
        <p>
          <span className="font-semibold">Ресурс:</span>{' '}
          {order.resource?.name || '—'}
        </p>
        <p>
          <span className="font-semibold">Объём:</span>{' '}
          {order.volume} {order.resource?.unit || 'т.'}
        </p>
        <p>
          <span className="font-semibold">Стоимость:</span>{' '}
          {order.cost?.toLocaleString('ru-RU')} ₽
        </p>
        <p>
          <span className="font-semibold">Адрес:</span> {order.dest_address}
        </p>
        {order.delivery_date && (
          <p>
            <span className="font-semibold">Дата доставки:</span>{' '}
            {order.delivery_date}
          </p>
        )}
        {order.comment && (
          <p>
            <span className="font-semibold">Комментарий:</span>{' '}
            {order.comment}
          </p>
        )}
        <p className="text-xs text-gray-400 mt-1">Создано: {createdDate}</p>
      </div>

      {/* Ошибка отмены */}
      {error && (
        <p className="text-xs text-red-600 mt-2">{error}</p>
      )}

      {/* Кнопка отмены */}
      {CANCELLABLE.includes(order.status) && (
        <button
          onClick={handleCancel}
          disabled={cancelling}
          className="mt-3 text-sm font-semibold text-red-500 hover:underline
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {cancelling ? 'Отмена...' : 'Отменить заявку'}
        </button>
      )}
    </div>
  );
}

export default OrderCard;
