import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import CreateOrderForm from '../components/CreateOrderForm';
import OrderCard from '../components/OrderCard';
import {
  fetchMyOrders,
  selectMyOrders,
  selectOrdersStatus,
} from '../store/orderSlice';

export const Orders = () => {
  const dispatch = useDispatch();
  const orders = useSelector(selectMyOrders);
  const ordersStatus = useSelector(selectOrdersStatus);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    dispatch(fetchMyOrders());
  }, [dispatch]);

  const handleOrderCreated = () => {
    setShowForm(false);
    dispatch(fetchMyOrders());
  };

  return (
    <div className="p-8 mx-20">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-dela text-3xl">Мои заявки</h1>
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="font-montserrat font-semibold text-white bg-blue-500
                     px-5 py-2.5 rounded-lg hover:bg-blue-600 transition-colors"
        >
          {showForm ? 'Скрыть форму' : '+ Новая заявка'}
        </button>
      </div>

      {showForm && (
        <div className="mb-8 max-w-2xl">
          <CreateOrderForm onCreated={handleOrderCreated} />
        </div>
      )}

      {ordersStatus === 'loading' && (
        <p className="font-montserrat text-gray-500">Загрузка заявок...</p>
      )}

      {ordersStatus === 'failed' && (
        <p className="font-montserrat text-red-500">
          Не удалось загрузить заявки. Проверьте, запущен ли сервис заказов.
        </p>
      )}

      {ordersStatus === 'succeeded' && orders.length === 0 && (
        <div className="text-center py-16">
          <p className="font-montserrat text-gray-400 text-lg">
            У вас пока нет заявок
          </p>
          {!showForm && (
            <button
              onClick={() => setShowForm(true)}
              className="mt-4 font-montserrat font-semibold text-blue-500 hover:underline"
            >
              Создать первую заявку
            </button>
          )}
        </div>
      )}

      {ordersStatus === 'succeeded' && orders.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {orders.map((order) => (
            <OrderCard key={order.id} order={order} />
          ))}
        </div>
      )}
    </div>
  );
};
