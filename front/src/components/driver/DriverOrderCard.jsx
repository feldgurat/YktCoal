import { useState } from 'react';
import { useDispatch } from 'react-redux';

import { driverWithdrawOrder, startOrder } from '../../store/driverSlice';

const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
    : '—';

// Заказ, в котором текущий водитель — назначенный исполнитель.
function DriverOrderCard({ order, resource }) {
  const dispatch = useDispatch();
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');

  const run = async (thunk, confirmText) => {
    if (confirmText && !window.confirm(confirmText)) return;
    setProcessing(true);
    setError('');
    try {
      await dispatch(thunk(order.id)).unwrap();
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Ошибка');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-5 font-montserrat">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-gray-400">#{order.id?.slice(0, 8)}</span>
        <span
          className={`text-xs font-semibold px-2.5 py-1 rounded-full ${order.statusColor}`}
        >
          {order.statusLabel}
        </span>
      </div>

      <div className="flex flex-col gap-1.5 text-sm">
        <p>
          <span className="font-semibold">Ресурс:</span>{' '}
          {resource?.name || '—'}
        </p>
        <p>
          <span className="font-semibold">Объём:</span> {order.volume}{' '}
          {resource?.unit || 'т'}
        </p>
        <p>
          <span className="font-semibold">Цена:</span>{' '}
          <span className="text-green-700 font-bold">
            {order.finalPrice != null
              ? order.finalPrice.toLocaleString('ru-RU')
              : '—'}{' '}
            ₽
          </span>
        </p>
        <p>
          <span className="font-semibold">Адрес:</span> {order.destAddress}
        </p>
        <p>
          <span className="font-semibold">Желаемая дата:</span>{' '}
          {formatDate(order.requestedDeliveryDate)}
        </p>
        {order.comment && (
          <p>
            <span className="font-semibold">Комментарий:</span> {order.comment}
          </p>
        )}
      </div>

      {error && <p className="text-xs text-red-600 mt-2">{error}</p>}

      {order.status === 'accepted' && (
        <div className="flex items-center gap-3 mt-3">
          <button
            onClick={() => run(startOrder)}
            disabled={processing}
            className="text-sm font-semibold text-white bg-blue-500 px-4 py-2 rounded-lg
                      hover:bg-blue-600 transition-colors
                      disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {processing ? '...' : 'Начать выполнение'}
          </button>
          <button
            onClick={() =>
              run(
                driverWithdrawOrder,
                'Отказаться от заказа? Он вернётся в общий список.',
              )
            }
            disabled={processing}
            className="text-sm font-semibold text-red-500 hover:underline
                      disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Отказаться
          </button>
        </div>
      )}

      {order.status === 'in_process' && (
        <p className="mt-3 text-sm text-purple-700">
          Заказ в пути. Завершение подтверждает заказчик после получения.
        </p>
      )}
    </div>
  );
}

export default DriverOrderCard;
