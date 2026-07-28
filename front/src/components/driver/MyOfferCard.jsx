import { useState } from 'react';
import { useDispatch } from 'react-redux';

import { withdrawOffer } from '../../store/driverSlice';

const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
    : '—';

function MyOfferCard({ offer }) {
  const dispatch = useDispatch();
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');

  const handleWithdraw = async () => {
    if (!window.confirm('Отозвать это предложение?')) return;
    setProcessing(true);
    setError('');
    try {
      await dispatch(withdrawOffer(offer.id)).unwrap();
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Не удалось отозвать');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-4 font-montserrat">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">
          Заказ #{offer.orderId?.slice(0, 8)}
        </span>
        <span
          className={`text-xs font-semibold px-2 py-0.5 rounded-full ${offer.statusColor}`}
        >
          {offer.statusLabel}
        </span>
      </div>

      <p className="text-sm">
        <span className="font-semibold">
          {offer.price.toLocaleString('ru-RU')} ₽
        </span>{' '}
        · доставка {formatDate(offer.deliveryDate)}
      </p>

      {offer.comment && (
        <p className="text-xs text-gray-500 mt-1">{offer.comment}</p>
      )}

      {error && <p className="text-xs text-red-600 mt-2">{error}</p>}

      {offer.status === 'pending' && (
        <button
          onClick={handleWithdraw}
          disabled={processing}
          className="mt-2 text-sm font-semibold text-red-500 hover:underline
                    disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {processing ? 'Отзыв...' : 'Отозвать'}
        </button>
      )}
    </div>
  );
}

export default MyOfferCard;
