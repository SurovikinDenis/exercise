from datetime import datetime

from sqlalchemy.event import listens_for

from ..extensions import db


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(300))
    status = db.Column(db.String(20), default='created')

    # Отправитель
    sender_name = db.Column(db.String(100), nullable=False)
    sender_phone = db.Column(db.String(20), nullable=False)
    sender_address = db.Column(db.String(200), nullable=False)

    # Получатель
    recipient_name = db.Column(db.String(100), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    recipient_address = db.Column(db.String(200), nullable=False)

    # Габариты груза (в см)
    length = db.Column(db.Float, nullable=False)  # X (длина)
    width = db.Column(db.Float, nullable=False)  # Y (ширина)
    height = db.Column(db.Float, nullable=False)  # Z (высота)

    # Весовые характеристики
    actual_weight = db.Column(db.Float, nullable=False)  # Фактический вес (кг)
    volumetric_weight = db.Column(db.Float)  # Объемный вес (расчетный)
    chargeable_weight = db.Column(db.Float)

    def can_delete(self, user):
        """Проверяет, может ли пользователь удалить этот заказ"""
        return user.id == self.user_id or user.status == 'admin'

    def can_edit(self, user):
        """Проверяет, может ли пользователь редактировать заказ"""
        return user.id == self.user_id or user.status == 'admin'

    @classmethod
    def get_editable_fields(cls):
        """Возвращает список полей, доступных для редактирования"""
        return [
            'sender_name', 'sender_phone', 'sender_address',
            'recipient_name', 'recipient_phone', 'recipient_address',
            'length', 'width', 'height', 'actual_weight', 'description'
        ]

    def calculate_volumetric(self):
        """Рассчитывает и возвращает все весовые характеристики"""
        # Рассчитываем объемный вес (X*Y*Z в см / 5000)
        self.volumetric_weight = round((self.length * self.width * self.height) / 5000, 2)

        # Определяем вес для оплаты (максимум из двух)
        self.chargeable_weight = max(self.actual_weight, self.volumetric_weight)

        # Возвращаем словарь с расчетами для удобства
        return {
            'volumetric': self.volumetric_weight,
            'actual': self.actual_weight,
            'chargeable': self.chargeable_weight
        }

    def get_weight_info(self):
        """Возвращает форматированную строку с весовыми характеристиками"""
        return (
            f"Фактический вес: {self.actual_weight} кг\n"
            f"Объемный вес: {self.volumetric_weight} кг\n"
            f"Вес для оплаты: {self.chargeable_weight} кг"
        )


# Автоматический расчет при изменении габаритов или веса
@listens_for(Order, 'before_insert')
@listens_for(Order, 'before_update')
def calculate_weights(mapper, connection, target):
    if any(hasattr(target, attr) for attr in ['length', 'width', 'height', 'actual_weight']):
        target.calculate_volumetric()



