from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import login_user, logout_user, current_user, login_required

from ..models.zakaz import Order
from ..models.user import User
from ..extensions import db, bcrypt
from ..forms import RegistrationForm, LoginForm, ProfileForm, ChangePasswordForm

user = Blueprint('user', __name__)


@user.route('/')
@login_required
def home():
    orders = current_user.orders
    return render_template('user/dashboard.html', active_tab='home', orders=orders)


@user.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html', active_tab='profile')


@user.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/orders.html', active_tab='orders', orders=orders)


@user.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if profile_form.validate_on_submit():
        profile_form.populate_obj(current_user)
        db.session.commit()
        flash('Профиль успешно обновлен!', 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/settings.html',
                           active_tab='settings',
                           profile_form=profile_form,
                           password_form=password_form)


@user.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            telephone=form.telephone.data,
            status=form.status.data,
            password=hashed_password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f"Поздравляем {form.username.data}! Вы успешно зарегистрировались!", "success")
            return redirect(url_for('user.login'))
        except Exception as e:
            print(str(e))
            db.session.rollback()
            flash("При регистрации произошла ошибка!" , "danger")
    return render_template('user/register.html', form=form)


@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Перенаправляем админа в админку, обычных пользователей - на home
        return redirect(url_for('admin.dashboard')) if current_user.is_admin else redirect(url_for('user.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')

            # Проверяем, является ли пользователь администратором
            if user.is_admin:
                flash(f"Добро пожаловать в панель администратора, {user.username}!", "success")
                return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
            else:
                flash(f"Добро пожаловать, {user.username}!", "success")
                return redirect(next_page) if next_page else redirect(url_for('user.home'))
        else:
            flash("Ошибка входа. Пожалуйста, проверьте email и пароль!", "danger")
    return render_template('user/login.html', form=form)


@user.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user.login'))
