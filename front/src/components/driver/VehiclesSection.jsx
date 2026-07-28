import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { uploadDoc } from '../../api/uploads';
import {
  addVehicle,
  deleteVehicle,
  fetchMyVehicles,
  selectVehicles,
  selectVehiclesStatus,
} from '../../store/driverSlice';

// Список машин водителя + добавление новой (с загрузкой ПТС/СТС и страховки).
function VehiclesSection() {
  const dispatch = useDispatch();
  const vehicles = useSelector(selectVehicles);
  const status = useSelector(selectVehiclesStatus);

  const [showForm, setShowForm] = useState(false);
  const [brand, setBrand] = useState('');
  const [model, setModel] = useState('');
  const [regNumber, setRegNumber] = useState('');
  const [capacity, setCapacity] = useState('');
  const [docsFile, setDocsFile] = useState(null);
  const [insuranceFile, setInsuranceFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (status === 'idle') {
      dispatch(fetchMyVehicles());
    }
  }, [dispatch, status]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const [docsPath, insurancePath] = await Promise.all([
        uploadDoc(docsFile),
        uploadDoc(insuranceFile),
      ]);

      await dispatch(
        addVehicle({
          brand,
          model,
          reg_number: regNumber,
          capacity: parseInt(capacity, 10),
          registration_docs: docsPath,
          insurance: insurancePath,
        }),
      ).unwrap();

      setShowForm(false);
      setBrand('');
      setModel('');
      setRegNumber('');
      setCapacity('');
      setDocsFile(null);
      setInsuranceFile(null);
    } catch (err) {
      setError(
        typeof err === 'string'
          ? err
          : err.response?.data?.detail || 'Не удалось добавить машину',
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (vehicleId) => {
    if (!window.confirm('Удалить эту машину?')) return;
    try {
      await dispatch(deleteVehicle(vehicleId)).unwrap();
    } catch (err) {
      setError(typeof err === 'string' ? err : 'Не удалось удалить');
    }
  };

  const inputCls =
    'w-full bg-gray-100 p-2 rounded-md border border-gray-300 ' +
    'focus:outline-none focus:ring-2 focus:ring-blue-400';

  return (
    <div className="font-montserrat">
      {status === 'loading' && (
        <p className="text-gray-500">Загрузка техники...</p>
      )}
      {status === 'failed' && (
        <p className="text-red-500">Не удалось загрузить список техники.</p>
      )}

      {status === 'succeeded' && vehicles.length === 0 && (
        <p className="text-gray-400 mb-4">У вас пока нет добавленной техники.</p>
      )}

      {vehicles.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {vehicles.map((v) => (
            <div
              key={v.id}
              className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-4"
            >
              <p className="font-semibold">
                {v.brand} {v.model}
              </p>
              <p className="text-sm text-gray-600">Госномер: {v.regNumber}</p>
              <p className="text-sm text-gray-600">
                Грузоподъёмность: {v.capacity} т
              </p>
              <button
                onClick={() => handleDelete(v.id)}
                className="mt-2 text-sm font-semibold text-red-500 hover:underline"
              >
                Удалить
              </button>
            </div>
          ))}
        </div>
      )}

      {error && <p className="text-sm text-red-600 mb-3">{error}</p>}

      {!showForm ? (
        <button
          onClick={() => setShowForm(true)}
          className="font-semibold text-white bg-blue-500 px-4 py-2 rounded-lg
                    hover:bg-blue-600 transition-colors"
        >
          + Добавить машину
        </button>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-5 max-w-lg flex flex-col gap-3"
        >
          <h3 className="font-semibold">Новая машина</h3>

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Марка <span className="text-red-500">*</span>
            </span>
            <input
              type="text"
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              required
              className={inputCls}
            />
          </label>

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Модель <span className="text-red-500">*</span>
            </span>
            <input
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              required
              className={inputCls}
            />
          </label>

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Госномер <span className="text-red-500">*</span>
            </span>
            <input
              type="text"
              value={regNumber}
              onChange={(e) => setRegNumber(e.target.value)}
              required
              className={inputCls}
            />
          </label>

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Грузоподъёмность, т <span className="text-red-500">*</span>
            </span>
            <input
              type="number"
              min="1"
              value={capacity}
              onChange={(e) => setCapacity(e.target.value)}
              required
              className={inputCls}
            />
          </label>

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              ПТС / СТС (фото или PDF) <span className="text-red-500">*</span>
            </span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={(e) => setDocsFile(e.target.files?.[0] ?? null)}
              required
              className="text-sm"
            />
          </label>

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Страховка (фото или PDF) <span className="text-red-500">*</span>
            </span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={(e) => setInsuranceFile(e.target.files?.[0] ?? null)}
              required
              className="text-sm"
            />
          </label>

          <div className="flex items-center gap-3 mt-1">
            <button
              type="submit"
              disabled={submitting}
              className="font-semibold text-white bg-blue-500 px-4 py-2 rounded-lg
                        hover:bg-blue-600 transition-colors
                        disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Сохранение...' : 'Добавить'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="font-semibold text-gray-500 hover:underline"
            >
              Отмена
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default VehiclesSection;
