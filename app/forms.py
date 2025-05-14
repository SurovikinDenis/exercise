from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Email, EqualTo, Length, Optional
from .models.user import User

class RegistrationForm(FlaskForm):
    username = StringField('ФИО/Название компании', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Телефон', validators=[DataRequired()])
    status = SelectField('Тип пользователя',
                       choices=[('individual', 'Физическое лицо'), ('company', 'Юридическое лицо')],
                       validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class OrderForm(FlaskForm):
    # Отправитель
    sender_name = StringField('Имя отправителя', validators=[DataRequired()])
    sender_phone = StringField('Телефон отправителя', validators=[DataRequired()])
    sender_address = StringField('Адрес отправки', validators=[DataRequired()])

    # Получатель
    recipient_name = StringField('Имя получателя', validators=[DataRequired()])
    recipient_phone = StringField('Телефон получателя', validators=[DataRequired()])
    recipient_address = StringField('Адрес доставки', validators=[DataRequired()])

    # Габариты груза (в см)
    length = FloatField('Длина (см)', validators=[DataRequired(), NumberRange(min=1)])
    width = FloatField('Ширина (см)', validators=[DataRequired(), NumberRange(min=1)])
    height = FloatField('Высота (см)', validators=[DataRequired(), NumberRange(min=1)])

    # Весовые характеристики
    actual_weight = FloatField('Фактический вес (кг)', validators=[DataRequired(), NumberRange(min=0.1)])

    # Описание
    description = TextAreaField('Описание груза')
    submit = SubmitField('Создать заказ')

class OrderStatusForm(FlaskForm):
    status = SelectField('Статус заказа',
                       choices=[('created', 'Создан'),
                                ('in_progress', 'В обработке'),
                                ('shipped', 'Отправлен'),
                                ('delivered', 'Доставлен'),
                                ('cancelled', 'Отменен')],
                       validators=[DataRequired()])
    submit = SubmitField('Обновить статус')

class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Телефон', validators=[DataRequired()])
    submit = SubmitField('Обновить профиль')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите новый пароль',
                                   validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Изменить пароль')

class UserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Телефон', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[Optional(), Length(min=6)])
    is_admin = BooleanField('Администратор')
