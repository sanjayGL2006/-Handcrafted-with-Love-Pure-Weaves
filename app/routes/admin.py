from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from typing import Any
from flask_login import login_required, current_user  # type: ignore[missing-import]
from app.models import Product, Category, User, Order, Suggestion
from app import db
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f: Any) -> None:  # type: ignore[unknown-name]
    @wraps(f)
    def decorated_function(*args, **kwargs) -> None:  # type: ignore[BSK-E0004]
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function  # type: ignore[BSK-E0013]

@admin_bp.route('/')
@login_required
@admin_required
def dashboard() -> None:
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0.0
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    suggestions = Suggestion.query.order_by(Suggestion.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                          total_users=total_users, 
                          total_products=total_products, 
                          total_orders=total_orders, 
                          total_revenue=total_revenue,
                          recent_orders=recent_orders,
                          suggestions=suggestions)

@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_products() -> None:
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        category_id = data.get('category_id')
        description = data.get('description')
        price = data.get('price')
        
        product = Product(name=name, category_id=category_id, description=description, price=float(price))  # type: ignore[unexpected-keyword]
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('admin.manage_products'))
        
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id: Any) -> None:  # type: ignore[unknown-name]
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted', 'success')
    return redirect(url_for('admin.manage_products'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users() -> None:
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/suggestions')
@login_required
@admin_required
def manage_suggestions() -> None:
    suggestions = Suggestion.query.all()
    return render_template('admin/suggestions.html', suggestions=suggestions)

@admin_bp.route('/suggestions/delete/<int:suggestion_id>', methods=['POST'])
@login_required
@admin_required
def delete_suggestion(suggestion_id: Any) -> None:  # type: ignore[unknown-name]
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    db.session.delete(suggestion)
    db.session.commit()
    flash('Suggestion deleted', 'success')
    return redirect(url_for('admin.manage_suggestions'))

@admin_bp.route('/orders')
@login_required
@admin_required
def manage_orders() -> None:
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/orders/update/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order(order_id: Any) -> None:  # type: ignore[unknown-name]
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    if status:
        order.status = status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {status}', 'success')
    return redirect(url_for('admin.manage_orders'))
