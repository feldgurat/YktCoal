// src/components/CreateOrderForm.jsx
import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import 'ol/ol.css';
import { Map, View, Feature } from 'ol';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import OSM from 'ol/source/OSM';
import Point from 'ol/geom/Point';
import { Style, Icon } from 'ol/style';
import { fromLonLat, toLonLat } from 'ol/proj';

import markerIcon from '../assets/marker.png';
import {
  createOrder,
  fetchResources,
  resetCreateStatus,
  selectCreateError,
  selectCreateStatus,
  selectResources,
  selectResourcesStatus,
} from '../store/orderSlice';

function CreateOrderForm({ onCreated }) {
  const dispatch = useDispatch();

  const resources = useSelector(selectResources);
  const resourcesStatus = useSelector(selectResourcesStatus);
  const createStatus = useSelector(selectCreateStatus);
  const createError = useSelector(selectCreateError);

  // ── Форма ──────────────────────────────────────────────────
  const [resourceId, setResourceId] = useState('');
  const [volume, setVolume] = useState('');
  const [destAddress, setDestAddress] = useState('');
  const [deliveryDate, setDeliveryDate] = useState('');
  const [comment, setComment] = useState('');
  const [coords, setCoords] = useState(null); // [lon, lat]

  // ── Карта ──────────────────────────────────────────────────
  const mapRef = useRef(null);
  const markerRef = useRef(new Feature());

  useEffect(() => {
    if (resourcesStatus === 'idle') {
      dispatch(fetchResources());
    }
  }, [dispatch, resourcesStatus]);

  // Инициализация карты
  useEffect(() => {
    if (!mapRef.current) return;

    markerRef.current.setStyle(
      new Style({
        image: new Icon({
          anchor: [0.5, 1],
          scale: 0.05,
          src: markerIcon,
        }),
      }),
    );

    const vectorSource = new VectorSource({
      features: [markerRef.current],
    });

    const map = new Map({
      target: mapRef.current,
      layers: [
        new TileLayer({ source: new OSM() }),
        new VectorLayer({ source: vectorSource }),
      ],
      view: new View({
        center: fromLonLat([129.7322, 62.0339]),
        zoom: 12,
      }),
    });

    map.on('click', (event) => {
      markerRef.current.setGeometry(new Point(event.coordinate));
      const lonLat = toLonLat(event.coordinate);
      setCoords(lonLat);
    });

    return () => map.setTarget(null);
  }, []);

  // Сброс формы после успешного создания
  useEffect(() => {
    if (createStatus === 'succeeded') {
      setResourceId('');
      setVolume('');
      setDestAddress('');
      setDeliveryDate('');
      setComment('');
      setCoords(null);
      markerRef.current.setGeometry(null);

      onCreated?.();

      // Через 3 секунды сбрасываем статус, чтобы можно было создать новую
      const timer = setTimeout(() => dispatch(resetCreateStatus()), 3000);
      return () => clearTimeout(timer);
    }
  }, [createStatus, dispatch, onCreated]);

  // ── Вычисляемая стоимость ──────────────────────────────────
  const selectedResource = resources.find((r) => r.id === resourceId);
  const estimatedCost =
    selectedResource && volume
      ? Math.round(parseFloat(volume) * selectedResource.price_per_unit)
      : null;

  // ── Отправка ───────────────────────────────────────────────
  const handleSubmit = (e) => {
    e.preventDefault();

    const payload = {
      dest_address: destAddress,
      resource_id: resourceId,
      volume: parseFloat(volume),
    };

    if (coords) {
      payload.longitude = coords[0];
      payload.latitude = coords[1];
    }
    if (deliveryDate) {
      payload.delivery_date = deliveryDate;
    }
    if (comment.trim()) {
      payload.comment = comment.trim();
    }

    dispatch(createOrder(payload));
  };

  const isSubmitting = createStatus === 'loading';

  return (
    <div className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-6">
      <h2 className="font-dela text-2xl mb-6">Новая заявка</h2>

      {createStatus === 'succeeded' && (
        <div className="mb-4 p-3 bg-green-50 border border-green-300 rounded-md text-green-800 font-montserrat text-sm">
          Заявка успешно создана!
        </div>
      )}

      {createError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-300 rounded-md text-red-700 font-montserrat text-sm">
          {createError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        {/* Тип угля */}
        <div>
          <label className="font-montserrat font-semibold text-sm block mb-1">
            Тип угля <span className="text-red-500">*</span>
          </label>
          <select
            value={resourceId}
            onChange={(e) => setResourceId(e.target.value)}
            required
            disabled={resourcesStatus === 'loading'}
            className="w-full font-montserrat bg-gray-100 p-2.5 rounded-md border border-gray-300
                       focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          >
            <option value="">
              {resourcesStatus === 'loading'
                ? 'Загрузка...'
                : 'Выберите тип угля'}
            </option>
            {resources
              .filter((r) => r.is_active)
              .map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} — {r.price_per_unit.toLocaleString('ru-RU')} ₽/{r.unit}
                </option>
              ))}
          </select>
        </div>

        {/* Объём */}
        <div>
          <label className="font-montserrat font-semibold text-sm block mb-1">
            Объём ({selectedResource?.unit || 'тонна'}){' '}
            <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            step="0.1"
            min="0.1"
            value={volume}
            onChange={(e) => setVolume(e.target.value)}
            placeholder="Например: 2.5"
            required
            className="w-full font-montserrat bg-gray-100 p-2.5 rounded-md border border-gray-300
                       focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          />
          {estimatedCost !== null && estimatedCost > 0 && (
            <p className="mt-1 text-sm text-gray-600 font-montserrat">
              Ориентировочная стоимость:{' '}
              <span className="font-bold text-black">
                {estimatedCost.toLocaleString('ru-RU')} ₽
              </span>
            </p>
          )}
        </div>

        {/* Адрес доставки */}
        <div>
          <label className="font-montserrat font-semibold text-sm block mb-1">
            Адрес доставки <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={destAddress}
            onChange={(e) => setDestAddress(e.target.value)}
            placeholder="Ул. Ленина, д. 10"
            required
            className="w-full font-montserrat bg-gray-100 p-2.5 rounded-md border border-gray-300
                       focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          />
        </div>

        {/* Карта */}
        <div>
          <label className="font-montserrat font-semibold text-sm block mb-1">
            Укажите точку на карте
          </label>
          <div
            ref={mapRef}
            className="w-full h-[300px] rounded-md border border-gray-300 shadow-sm"
          />
          {coords && (
            <p className="mt-1 text-xs text-gray-500 font-montserrat">
              Координаты: {coords[1].toFixed(5)}, {coords[0].toFixed(5)}
            </p>
          )}
        </div>

        {/* Дата доставки */}
        <div>
          <label className="font-montserrat font-semibold text-sm block mb-1">
            Желаемая дата доставки
          </label>
          <input
            type="date"
            value={deliveryDate}
            onChange={(e) => setDeliveryDate(e.target.value)}
            className="w-full font-montserrat bg-gray-100 p-2.5 rounded-md border border-gray-300
                       focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          />
        </div>

        {/* Комментарий */}
        <div>
          <label className="font-montserrat font-semibold text-sm block mb-1">
            Комментарий
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Дополнительные пожелания..."
            maxLength={1000}
            rows={3}
            className="w-full font-montserrat bg-gray-100 p-2.5 rounded-md border border-gray-300
                       focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-y"
          />
        </div>

        {/* Кнопка */}
        <button
          type="submit"
          disabled={isSubmitting || !resourceId || !volume || !destAddress}
          className="w-full font-montserrat font-semibold text-white bg-blue-500
                     py-3 rounded-lg hover:bg-blue-600 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Отправка...' : 'Создать заявку'}
        </button>
      </form>
    </div>
  );
}

export default CreateOrderForm;
