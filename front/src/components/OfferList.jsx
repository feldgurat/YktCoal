import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  acceptOffer,
  fetchOrderOffers,
  rejectOffer,
  selectOffersByOrder,
} from '../store/orderSlice';

const OFFER_STATUS_COLORS = {
  1: 'bg-amber-100 text-amber-800',   
  2: 'bg-green-100 text-green-800',   
  3: 'bg-red-100 text-red-700',       
  4: 'bg-gray-100 text-gray-600',     
};

function OfferList({ orderId, orderStatus }) {
  const dispatch = useDispatch();
  const { status, offers, error } = useSelector(selectOffersByOrder(orderId));
  const [actionError, setActionError] = useState('');
  const [processingId, setProcessingId] = useState(null);

  useEffect(() => {
    if (status === 'idle') {
      dispatch(fetchOrderOffers(orderId));
    }
  }, [dispatch, orderId, status]);

  const handleAccept = async (offerId) => {
    setProcessingId(offerId);
    setActionError('');
    try {
      await dispatch(acceptOffer({ offerId, orderId })).unwrap();
    } catch (err) {
      setActionError(typeof err === 'string' ? err : 'Ошибка при принятии');
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (offerId) => {
    setProcessingId(offerId);
    setActionError('');
    try {
      await dispatch(rejectOffer({ offerId, orderId })).unwrap();
    } catch (err) {
      setActionError(typeof err === 'string' ? err : 'Ошибка при отклонении');
    } finally {
      setProcessingId(null);
    }
  };

  if (status === 'loading') {
    return (
      <p className="text-xs text-gray-400 mt-2 font-montserrat">
        Загрузка предложений...
      </p>
    );
  }

  if (error) {
    return (
      <p className="text-xs text-red-500 mt-2 font-montserrat">{error}</p>
    );
  }

  if (offers.length === 0) {
    return (
      <p className="text-xs text-gray-400 mt-3 font-montserrat italic">
        Пока нет предложений от водителей
      </p>
    );
  }

  const canManage = orderStatus === 1;

  return (
    <div className="mt-3 border-t border-gray-100 pt-3">
      <p className="font-montserrat font-semibold text-xs text-gray-500 mb-2">
        Предложения водителей ({offers.length})
      </p>

      {actionError && (
        <p className="text-xs text-red-600 mb-2 font-montserrat">{actionError}</p>
      )}

      <div className="flex flex-col gap-2">
        {offers.map((offer) => {
          const statusColor =
            OFFER_STATUS_COLORS[offer.status] || 'bg-gray-100 text-gray-800';
          const isPending = offer.status === 1;
          const isProcessing = processingId === offer.id;

          return (
            <div
              key={offer.id}
              className="bg-gray-50 rounded-md p-3 border border-gray-200 font-montserrat"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-sm">
                  {offer.price.toLocaleString('ru-RU')} ₽
                </span>
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full ${statusColor}`}
                >
                  {offer.status_label}
                </span>
              </div>

              {offer.delivery_date && (
                <p className="text-xs text-gray-600">
                  Доставка: {offer.delivery_date}
                </p>
              )}

              {offer.comment && (
                <p className="text-xs text-gray-500 mt-1">{offer.comment}</p>
              )}

              {isPending && canManage && (
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => handleAccept(offer.id)}
                    disabled={isProcessing}
                    className="text-xs font-semibold text-white bg-green-500 px-3 py-1 rounded
                              hover:bg-green-600 transition-colors
                              disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? '...' : 'Принять'}
                  </button>
                  <button
                    onClick={() => handleReject(offer.id)}
                    disabled={isProcessing}
                    className="text-xs font-semibold text-red-600 bg-red-50 px-3 py-1 rounded
                              border border-red-200 hover:bg-red-100 transition-colors
                              disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? '...' : 'Отклонить'}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default OfferList;
