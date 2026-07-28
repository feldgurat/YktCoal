import driverApi from './driverApi';
import { APPLICATIONS } from './endpoints';

// Загружает один документ (jpeg/png/webp/pdf) в Driver-сервис.
// Возвращает имя сохранённого файла — его нужно подставлять в поля
// license_url / passport / registration_docs / insurance.
export async function uploadDoc(file) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await driverApi.post(APPLICATIONS.UPLOAD_DOC, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data.path;
}
