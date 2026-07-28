import { useState } from 'react';
import { useDispatch } from 'react-redux';

import { createOffer, withdrawOffer } from '../../store/driverSlice';

const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
    : '—';

// Карточка доступного заказа для водителя: информация + подача предложения.
// myOffer — моё предложение по этому заказу (если уже подано).
function AvailableOrderCard({ order, resource, myOffer }) {
  const dispatch = useDispatch();

  const [showForm, setShowForm] = useState(false);
  const [price, setPrice] = useState('');
  const [deliveryDate, setDeliveryDate] = useState('');
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const hasPendingOffer = myOffer?.status === 'pending';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    const payload = {
      order_id: order.id,
      price: parseFloat(price),
      delivery_date: `${deliveryDate}T00:00:00`,
    };
    if (comment.trim()) payload.comment = comment.trim();

    try {
      await dispatch(createOffer(payload)).unwrap();
      setShowForm(false);
      setPrice('');
      setDeliveryDate('');
      setComment('');
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Ошибка при отправке');
    } finally {
      setSubmitting(false);
    }
  };

  const handleWithdraw = async () => {
    if (!window.confirm('Отозвать предложение по этому заказу?')) return;
    setSubmitting(true);
    setError('');
    try {
      await dispatch(withdrawOffer(myOffer.id)).unwrap();
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Не удалось отозвать');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-5 font-montserrat">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-gray-400">#{order.id?.slice(0, 8)}</span>
        <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-100 text-blue-800">
          Новый
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
          <span className="font-semibold">Справочная стоимость:</span>{' '}
          {order.cost != null ? order.cost.toLocaleString('ru-RU') : '—'} ₽
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

      {hasPendingOffer ? (
        <div className="mt-3 border-t border-gray-100 pt-3">
          <p className="text-sm">
            Ваше предложение:{' '}
            <span className="font-semibold">
              {myOffer.price.toLocaleString('ru-RU')} ₽
            </span>{' '}
            на {formatDate(myOffer.deliveryDate)}
          </p>
          <button
            onClick={handleWithdraw}
            disabled={submitting}
            className="mt-2 text-sm font-semibold text-red-500 hover:underline
                      disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Отзыв...' : 'Отозвать предложение'}
          </button>
        </div>
      ) : !showForm ? (
        <button
          onClick={() => setShowForm(true)}
          className="mt-3 text-sm font-semibold text-white bg-blue-500 px-4 py-2 rounded-lg
                    hover:bg-blue-600 transition-colors"
        >
          Предложить цену
        </button>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="mt-3 border-t border-gray-100 pt-3 flex flex-col gap-2"
        >
          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Ваша цена, ₽ <span className="text-red-500">*</span>
            </span>
            <input
              type="number"
              step="0.01"
              min="1"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
              className="w-full bg-gray-100 p-2 rounded-md border border-gray-300
                        focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </label>

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Дата доставки <span className="text-red-500">*</span>
            </span>
            <input
              type="date"
              value={deliveryDate}
              onChange={(e) => setDeliveryDate(e.target.value)}
              required
              className="w-full bg-gray-100 p-2 rounded-md border border-gray-300
                        focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </label>

          <label className="text-sm">
            <span className="font-semibold block mb-1">Комментарий</span>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              maxLength={500}
              rows={2}
              className="w-full bg-gray-100 p-2 rounded-md border border-gray-300
                        focus:outline-none focus:ring-2 focus:ring-blue-400 resize-y"
            />
          </label>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={submitting}
              className="text-sm font-semibold text-white bg-blue-500 px-4 py-2 rounded-lg
                        hover:bg-blue-600 transition-colors
                        disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Отправка...' : 'Отправить'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="text-sm font-semibold text-gray-500 hover:underline"
            >
              Отмена
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default AvailableOrderCard;
