from flask_login import UserMixin

from ..extensions import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(40), unique=True, nullable=False)
    status = db.Column(db.String(50), default='individual', nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True,
                             foreign_keys='Order.user_id', cascade='all, delete-orphan')

    def can_edit(self, user):
        return user.id == self.id or user.is_admin

    def is_administrator(self):
        return self.is_admin