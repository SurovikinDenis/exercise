from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user, logout_user, login_user

from ..forms import UserForm, OrderStatusForm
from ..models.zakaz import Order
from ..models.user import User
from ..extensions import db, bcrypt

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Доступ запрещён: требуются права администратора', 'danger')
            return redirect(url_for('user.home'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html',
                         users=users,
                         orders=None,
                         active_tab='users')


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            telephone=form.telephone.data,
            password=hashed_password,
            is_admin=form.is_admin.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Пользователь успешно создан', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/user_form.html', form=form, title='Создание пользователя')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.telephone = form.telephone.data
        user.is_admin = form.is_admin.data
        if form.password.data:
            user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Данные пользователя обновлены', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/user_form.html', form=form, title='Редактирование пользователя')

@admin_bp.route('/orders')
@admin_required
def list_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/dashboard.html',
                         users=None,
                         orders=orders,
                         active_tab='orders')

@admin_bp.route('/orders/<int:order_id>')
@admin_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderStatusForm(obj=order)

    if form.validate_on_submit():
        # Логирование изменения статуса
        if order.status != form.status.data:
            flash(f'Статус заказа #{order.id} изменен: {order.status} → {form.status.data}', 'info')

        form.populate_obj(order)
        db.session.commit()
        flash('Заказ успешно обновлен', 'success')
        return redirect(url_for('admin.view_order', order_id=order.id))

    return render_template('admin/order_form.html', form=form, order=order)


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if current_user.id == user_id:
        flash("Вы не можете удалить самого себя!", 'danger')
        return redirect(url_for('admin.dashboard'))

    user = User.query.get_or_404(user_id)

    # Логирование перед удалением (опционально)
    order_count = len(user.orders)
    flash_message = f'Пользователь {user.username} и его {order_count} заказов удалены'

    try:
        db.session.delete(user)
        db.session.commit()
        flash(flash_message, 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении: {str(e)}', 'danger')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/user/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    if current_user.id == user_id:
        flash("You can't change your own admin status!", 'danger')
        return redirect(url_for('admin.dashboard'))

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()

    # Принудительно обновляем сессию если редактируем текущего пользователя
    if user.id == current_user.id:
        logout_user()
        login_user(user)

    flash(f'Admin status updated for {user.username}', 'success')
    return redirect(url_for('admin.dashboard'))
