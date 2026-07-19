// Единственное место на фронте, где живёт форма ответов Order-сервиса.
// Компоненты и стор работают только с нормализованными объектами отсюда.

export const ORDER_STATUS = {
  new: { label: 'Новый', color: 'bg-blue-100 text-blue-800' },
  accepted: { label: 'Принят', color: 'bg-yellow-100 text-yellow-800' },
  in_process: { label: 'В пути', color: 'bg-purple-100 text-purple-800' },
  completed: { label: 'Выполнен', color: 'bg-green-100 text-green-800' },
  cancelled: { label: 'Отменён', color: 'bg-gray-100 text-gray-600' },
};

export const OFFER_STATUS = {
  pending: { label: 'Ожидает', color: 'bg-amber-100 text-amber-800' },
  accepted: { label: 'Принято', color: 'bg-green-100 text-green-800' },
  rejected: { label: 'Отклонено', color: 'bg-red-100 text-red-700' },
  withdrawn: { label: 'Отозвано', color: 'bg-gray-100 text-gray-600' },
};

const num = (v) => (v === null || v === undefined ? null : Number(v));

export function mapResource(dto) {
  return {
    id: dto.id,
    name: dto.name,
    price: num(dto.price),
    unit: dto.unit ?? 'т',
    isActive: dto.is_active,
  };
}

export function mapOrder(dto) {
  const meta = ORDER_STATUS[dto.status] ?? {
    label: dto.status,
    color: 'bg-gray-100 text-gray-800',
  };
  return {
    id: dto.id,
    userId: dto.user_id,
    acceptedDriverId: dto.accepted_driver_id,
    resourceId: dto.resource_id,
    destAddress: dto.dest_address,
    volume: num(dto.volume),
    cost: num(dto.cost),
    finalPrice: num(dto.final_price),
    requestedDeliveryDate: dto.requested_delivery_date,
    orderDate: dto.order_date,
    status: dto.status,
    statusLabel: meta.label,
    statusColor: meta.color,
    comment: dto.comment,
    latitude: num(dto.latitude),
    longitude: num(dto.longitude),
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
  };
}

export function mapOffer(dto) {
  const meta = OFFER_STATUS[dto.status] ?? {
    label: dto.status,
    color: 'bg-gray-100 text-gray-800',
  };
  return {
    id: dto.id,
    orderId: dto.order_id,
    driverUserId: dto.driver_user_id,
    price: num(dto.price),
    comment: dto.comment,
    deliveryDate: dto.delivery_date,
    status: dto.status,
    statusLabel: meta.label,
    statusColor: meta.color,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
  };
}
