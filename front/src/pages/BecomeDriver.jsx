import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { uploadDoc } from '../api/uploads';
import { selectIsDriver } from '../store/authSlice';
import {
  fetchMyApplications,
  selectApplications,
  selectApplicationsStatus,
  submitApplication,
} from '../store/driverSlice';

const emptyVehicle = () => ({
  brand: '',
  model: '',
  regNumber: '',
  capacity: '',
  docsFile: null,
  insuranceFile: null,
});

const formatDate = (iso) =>
  iso
    ? new Date(iso).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '—';

const inputCls =
  'w-full bg-gray-100 p-2 rounded-md border border-gray-300 ' +
  'focus:outline-none focus:ring-2 focus:ring-blue-400';

export default function BecomeDriver() {
  const dispatch = useDispatch();
  const isDriver = useSelector(selectIsDriver);
  const applications = useSelector(selectApplications);
  const applicationsStatus = useSelector(selectApplicationsStatus);

  const [licenseFile, setLicenseFile] = useState(null);
  const [passportFile, setPassportFile] = useState(null);
  const [vehicles, setVehicles] = useState([emptyVehicle()]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    dispatch(fetchMyApplications());
  }, [dispatch]);

  const hasPending = applications.some((a) => a.status === 'pending');

  const setVehicleField = (idx, field, value) => {
    setVehicles((prev) =>
      prev.map((v, i) => (i === idx ? { ...v, [field]: value } : v)),
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const [licensePath, passportPath] = await Promise.all([
        uploadDoc(licenseFile),
        uploadDoc(passportFile),
      ]);

      const vehiclesPayload = await Promise.all(
        vehicles.map(async (v) => {
          const [docsPath, insurancePath] = await Promise.all([
            uploadDoc(v.docsFile),
            uploadDoc(v.insuranceFile),
          ]);
          return {
            brand: v.brand,
            model: v.model,
            reg_number: v.regNumber,
            capacity: parseInt(v.capacity, 10),
            registration_docs: docsPath,
            insurance: insurancePath,
          };
        }),
      );

      await dispatch(
        submitApplication({
          license_url: licensePath,
          passport: passportPath,
          vehicles: vehiclesPayload,
        }),
      ).unwrap();

      setLicenseFile(null);
      setPassportFile(null);
      setVehicles([emptyVehicle()]);
    } catch (err) {
      setError(
        typeof err === 'string'
          ? err
          : err.response?.data?.detail || 'Не удалось отправить заявку',
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-8 mx-20 font-montserrat">
      <h1 className="font-dela text-3xl mb-2">Стать водителем</h1>
      <p className="text-gray-500 mb-6 max-w-2xl">
        Заполните заявку: загрузите документы и укажите вашу технику. После
        одобрения администратором вам станет доступен кабинет водителя.
      </p>

      {/* ── Мои заявки ── */}
      {applicationsStatus === 'loading' && (
        <p className="text-gray-500 mb-4">Загрузка заявок...</p>
      )}

      {applications.length > 0 && (
        <div className="mb-8 max-w-2xl flex flex-col gap-3">
          <h2 className="font-semibold text-lg">Мои заявки</h2>
          {applications.map((app) => (
            <div
              key={app.id}
              className="bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-4"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  от {formatDate(app.submissionDate)}
                </span>
                <span
                  className={`text-xs font-semibold px-2.5 py-1 rounded-full ${app.statusColor}`}
                >
                  {app.statusLabel}
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                Машин в заявке: {app.vehicles.length}
              </p>
              {app.status === 'rejected' && app.rejectionReason && (
                <p className="text-sm text-red-600 mt-1">
                  Причина отказа: {app.rejectionReason}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {isDriver ? (
        <div className="max-w-2xl bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-800">
            Вы уже водитель — заявка одобрена. Перейдите в кабинет водителя,
            чтобы брать заказы.
          </p>
        </div>
      ) : hasPending ? (
        <div className="max-w-2xl bg-amber-50 border border-amber-200 rounded-lg p-4">
          <p className="text-amber-800">
            Ваша заявка на рассмотрении. Дождитесь решения администратора.
          </p>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="max-w-2xl bg-white shadow-[0_4px_4px_rgba(0,0,0,0.25)] rounded-lg p-6 flex flex-col gap-5"
        >
          {error && (
            <div className="p-3 bg-red-50 border border-red-300 rounded-md text-red-700 text-sm">
              {error}
            </div>
          )}

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Водительское удостоверение (фото или PDF){' '}
              <span className="text-red-500">*</span>
            </span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={(e) => setLicenseFile(e.target.files?.[0] ?? null)}
              required
              className="text-sm"
            />
          </label>

          <label className="text-sm">
            <span className="font-semibold block mb-1">
              Паспорт (фото или PDF) <span className="text-red-500">*</span>
            </span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={(e) => setPassportFile(e.target.files?.[0] ?? null)}
              required
              className="text-sm"
            />
          </label>

          <div className="flex flex-col gap-4">
            <h2 className="font-semibold">Техника (минимум одна машина)</h2>

            {vehicles.map((v, idx) => (
              <fieldset
                key={idx}
                className="border border-gray-200 rounded-lg p-4 flex flex-col gap-3"
              >
                <div className="flex items-center justify-between">
                  <legend className="font-semibold text-sm px-1">
                    Машина {idx + 1}
                  </legend>
                  {vehicles.length > 1 && (
                    <button
                      type="button"
                      onClick={() =>
                        setVehicles((prev) => prev.filter((_, i) => i !== idx))
                      }
                      className="text-sm font-semibold text-red-500 hover:underline"
                    >
                      Убрать
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <label className="text-sm">
                    <span className="font-semibold block mb-1">
                      Марка <span className="text-red-500">*</span>
                    </span>
                    <input
                      type="text"
                      value={v.brand}
                      onChange={(e) =>
                        setVehicleField(idx, 'brand', e.target.value)
                      }
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
                      value={v.model}
                      onChange={(e) =>
                        setVehicleField(idx, 'model', e.target.value)
                      }
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
                      value={v.regNumber}
                      onChange={(e) =>
                        setVehicleField(idx, 'regNumber', e.target.value)
                      }
                      required
                      className={inputCls}
                    />
                  </label>

                  <label className="text-sm">
                    <span className="font-semibold block mb-1">
                      Грузоподъёмность, т{' '}
                      <span className="text-red-500">*</span>
                    </span>
                    <input
                      type="number"
                      min="1"
                      value={v.capacity}
                      onChange={(e) =>
                        setVehicleField(idx, 'capacity', e.target.value)
                      }
                      required
                      className={inputCls}
                    />
                  </label>
                </div>

                <label className="text-sm">
                  <span className="font-semibold block mb-1">
                    ПТС / СТС (фото или PDF){' '}
                    <span className="text-red-500">*</span>
                  </span>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp,application/pdf"
                    onChange={(e) =>
                      setVehicleField(
                        idx,
                        'docsFile',
                        e.target.files?.[0] ?? null,
                      )
                    }
                    required
                    className="text-sm"
                  />
                </label>

                <label className="text-sm">
                  <span className="font-semibold block mb-1">
                    Страховка (фото или PDF){' '}
                    <span className="text-red-500">*</span>
                  </span>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp,application/pdf"
                    onChange={(e) =>
                      setVehicleField(
                        idx,
                        'insuranceFile',
                        e.target.files?.[0] ?? null,
                      )
                    }
                    required
                    className="text-sm"
                  />
                </label>
              </fieldset>
            ))}

            <button
              type="button"
              onClick={() => setVehicles((prev) => [...prev, emptyVehicle()])}
              className="self-start text-sm font-semibold text-blue-500 hover:underline"
            >
              + Ещё машина
            </button>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full font-semibold text-white bg-blue-500 py-3 rounded-lg
                      hover:bg-blue-600 transition-colors
                      disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Отправка...' : 'Отправить заявку'}
          </button>
        </form>
      )}
    </div>
  );
}
