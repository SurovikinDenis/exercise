from flask import Blueprint, render_template, redirect, flash, url_for, abort
from flask_login import login_required, current_user

from ..forms import OrderForm
from ..models.zakaz import Order
from ..extensions import db

order = Blueprint('order', __name__)


@order.route('/post/create', methods=['GET', 'POST'])
@login_required
def create():
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(
            sender_name=form.sender_name.data,
            sender_phone=form.sender_phone.data,
            sender_address=form.sender_address.data,
            recipient_name=form.recipient_name.data,
            recipient_phone=form.recipient_phone.data,
            recipient_address=form.recipient_address.data,
            length=form.length.data,
            width=form.width.data,
            height=form.height.data,
            actual_weight=form.actual_weight.data,
            description=form.description.data,
            user_id=current_user.id
        )
        order.calculate_volumetric()
        db.session.add(order)
        db.session.commit()
        flash('Заказ оформлен!', 'success')
        return redirect(url_for('user.home'))
    return render_template('post/create.html', form=form)


@order.route('/post/delete/<int:order_id>', methods=['POST'])
@login_required
def delete(order_id):
    order_to_delete = Order.query.get_or_404(order_id)

    if not order_to_delete.can_delete(current_user):
        abort(403)  # Запрет если не владелец и не админ

    db.session.delete(order_to_delete)
    db.session.commit()
    flash('Заказ успешно удален!', 'success')
    return redirect(url_for('user.home'))


@order.route('/detail/<int:order_id>', methods=['GET', 'POST'])
@login_required
def detail(order_id):
    order = Order.query.get_or_404(order_id)

    # Проверка прав
    if not order.can_edit(current_user):
        abort(403)

    form = OrderForm(obj=order)

    if form.validate_on_submit():
        form.populate_obj(order)
        order.calculate_volumetric()  # Пересчет весов
        db.session.commit()
        flash('Заказ успешно обновлен!', 'success')
        return redirect(url_for('order.detail', order_id=order.id))

    return render_template('post/detail.html', form=form, order=order)
