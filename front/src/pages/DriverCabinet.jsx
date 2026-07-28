import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';

import AvailableOrderCard from '../components/driver/AvailableOrderCard';
import DriverOrderCard from '../components/driver/DriverOrderCard';
import MyOfferCard from '../components/driver/MyOfferCard';
import VehiclesSection from '../components/driver/VehiclesSection';
import { selectIsDriver } from '../store/authSlice';
import { fetchResources, selectResources } from '../store/orderSlice';
import {
  fetchAvailableOrders,
  fetchMyDriverOrders,
  fetchMyOffers,
  selectAvailableOrders,
  selectAvailableStatus,
  selectDriverOrders,
  selectDriverOrdersStatus,
  selectMyOffers,
  selectMyOffersStatus,
} from '../store/driverSlice';

const TABS = [
  { key: 'available', label: 'Доступные заказы' },
  { key: 'mine', label: 'Мои заказы' },
  { key: 'offers', label: 'Мои предложения' },
  { key: 'vehicles', label: 'Моя техника' },
];

export default function DriverCabinet() {
  const dispatch = useDispatch();
  const isDriver = useSelector(selectIsDriver);

  const resources = useSelector(selectResources);
  const available = useSelector(selectAvailableOrders);
  const availableStatus = useSelector(selectAvailableStatus);
  const driverOrders = useSelector(selectDriverOrders);
  const driverOrdersStatus = useSelector(selectDriverOrdersStatus);
  const myOffers = useSelector(selectMyOffers);
  const myOffersStatus = useSelector(selectMyOffersStatus);

  const [tab, setTab] = useState('available');

  useEffect(() => {
    if (!isDriver) return;
    dispatch(fetchResources());
    dispatch(fetchAvailableOrders());
    dispatch(fetchMyDriverOrders());
    dispatch(fetchMyOffers());
  }, [dispatch, isDriver]);

  if (!isDriver) {
    return (
      <div className="p-8 mx-20 font-montserrat">
        <h1 className="font-dela text-3xl mb-4">Кабинет водителя</h1>
        <p className="text-gray-600">
          Раздел доступен только водителям.{' '}
          <Link
            to="/become-driver"
            className="text-blue-500 font-semibold underline hover:no-underline"
          >
            Подайте заявку
          </Link>
          , чтобы получить доступ.
        </p>
      </div>
    );
  }

  const resourceById = (id) => resources.find((r) => r.id === id);
  // Мои активные предложения по заказам — чтобы не подавать дважды.
  const offerByOrderId = new Map(
    myOffers
      .filter((o) => o.status === 'pending')
      .map((o) => [o.orderId, o]),
  );

  // Актуальные назначенные заказы — сверху, завершённые/отменённые — ниже.
  const activeDriverOrders = driverOrders.filter((o) =>
    ['accepted', 'in_process'].includes(o.status),
  );
  const pastDriverOrders = driverOrders.filter(
    (o) => !['accepted', 'in_process'].includes(o.status),
  );

  return (
    <div className="p-8 mx-20 font-montserrat">
      <h1 className="font-dela text-3xl mb-6">Кабинет водителя</h1>

      <div className="flex gap-2 mb-6 flex-wrap">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-colors ${
              tab === key
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'available' && (
        <>
          {availableStatus === 'loading' && (
            <p className="text-gray-500">Загрузка заказов...</p>
          )}
          {availableStatus === 'failed' && (
            <p className="text-red-500">Не удалось загрузить заказы.</p>
          )}
          {availableStatus === 'succeeded' && available.length === 0 && (
            <p className="text-gray-400">Свободных заказов пока нет.</p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {available.map((order) => (
              <AvailableOrderCard
                key={order.id}
                order={order}
                resource={resourceById(order.resourceId)}
                myOffer={offerByOrderId.get(order.id)}
              />
            ))}
          </div>
        </>
      )}

      {tab === 'mine' && (
        <>
          {driverOrdersStatus === 'loading' && (
            <p className="text-gray-500">Загрузка...</p>
          )}
          {driverOrdersStatus === 'failed' && (
            <p className="text-red-500">Не удалось загрузить ваши заказы.</p>
          )}
          {driverOrdersStatus === 'succeeded' && driverOrders.length === 0 && (
            <p className="text-gray-400">
              У вас пока нет назначенных заказов. Подайте предложение на
              доступный заказ.
            </p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[...activeDriverOrders, ...pastDriverOrders].map((order) => (
              <DriverOrderCard
                key={order.id}
                order={order}
                resource={resourceById(order.resourceId)}
              />
            ))}
          </div>
        </>
      )}

      {tab === 'offers' && (
        <>
          {myOffersStatus === 'loading' && (
            <p className="text-gray-500">Загрузка предложений...</p>
          )}
          {myOffersStatus === 'failed' && (
            <p className="text-red-500">Не удалось загрузить предложения.</p>
          )}
          {myOffersStatus === 'succeeded' && myOffers.length === 0 && (
            <p className="text-gray-400">Вы ещё не подавали предложений.</p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {myOffers.map((offer) => (
              <MyOfferCard key={offer.id} offer={offer} />
            ))}
          </div>
        </>
      )}

      {tab === 'vehicles' && <VehiclesSection />}
    </div>
  );
}
