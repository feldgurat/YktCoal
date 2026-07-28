import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { cancelOrder, completeOrder, selectResources } from '../store/orderSlice';
import OfferList from './OfferList';

const CANCELLABLE = ['new', 'accepted'];

function OrderCard({ order }) {
  const dispatch = useDispatch();
  const resources = useSelector(selectResources);
  const [cancelling, setCancelling] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [error, setError] = useState('');
  const [showOffers, setShowOffers] = useState(false);

  const resource = resources.find((r) => r.id === order.resourceId);
  const resourceName = resource?.name || '—';
  const unit = resource?.unit || 'т';

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

  const handleComplete = async () => {
    if (!window.confirm('Подтвердить, что заказ доставлен?')) return;

    setCompleting(true);
    setError('');
    try {
      await dispatch(completeOrder(order.id)).unwrap();
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Не удалось подтвердить');
    } finally {
      setCompleting(false);
    }
  };

  const createdDate = order.createdAt
    ? new Date(order.createdAt).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '—';

  const deliveryDate = order.requestedDeliveryDate
    ? new Date(order.requestedDeliveryDate).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
    : null;

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
          <span className="font-semibold">Ресурс:</span> {resourceName}
        </p>
        <p>
          <span className="font-semibold">Объём:</span> {order.volume} {unit}
        </p>

        {order.finalPrice != null ? (
          <p>
            <span className="font-semibold">Итоговая цена:</span>{' '}
            <span className="text-green-700 font-bold">
              {order.finalPrice.toLocaleString('ru-RU')} ₽
            </span>
          </p>
        ) : (
          <p>
            <span className="font-semibold">Ориентировочная стоимость:</span>{' '}
            <span className="text-gray-700">
              {order.cost != null ? order.cost.toLocaleString('ru-RU') : '—'} ₽
            </span>
            <span className="text-xs text-gray-400 ml-1">
              (итоговую цену предложат водители)
            </span>
          </p>
        )}

        <p>
          <span className="font-semibold">Адрес:</span> {order.destAddress}
        </p>
        {deliveryDate && (
          <p>
            <span className="font-semibold">Дата доставки:</span> {deliveryDate}
          </p>
        )}
        {order.comment && (
          <p>
            <span className="font-semibold">Комментарий:</span> {order.comment}
          </p>
        )}
        <p className="text-xs text-gray-400 mt-1">Создано: {createdDate}</p>
      </div>

      {error && <p className="text-xs text-red-600 mt-2">{error}</p>}

      <div className="flex items-center gap-3 mt-3">
        <button
          onClick={() => setShowOffers((prev) => !prev)}
          className="text-sm font-semibold text-blue-500 hover:underline"
        >
          {showOffers ? 'Скрыть предложения' : 'Предложения'}
        </button>

        {order.status === 'in_process' && (
          <button
            onClick={handleComplete}
            disabled={completing}
            className="text-sm font-semibold text-green-600 hover:underline
                      disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {completing ? 'Подтверждение...' : 'Подтвердить получение'}
          </button>
        )}

        {CANCELLABLE.includes(order.status) && (
          <button
            onClick={handleCancel}
            disabled={cancelling}
            className="text-sm font-semibold text-red-500 hover:underline
                      disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {cancelling ? 'Отмена...' : 'Отменить'}
          </button>
        )}
      </div>

      {showOffers && <OfferList orderId={order.id} orderStatus={order.status} />}
    </div>
  );
}

export default OrderCard;
