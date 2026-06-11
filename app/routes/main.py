from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user  # type: ignore[missing-import]
from app.models import Product, Category, Wishlist, CartItem, Order, OrderItem, Suggestion
from app import db
from typing import Any, List

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index() -> Any:
    featured_products = Product.query.filter_by(is_active=True).limit(8).all()
    return render_template('index.html', featured_products=featured_products)

@main_bp.route('/catalog')
def catalog() -> Any:
    # Catalog filtering and sorting
    query = Product.query.filter_by(is_active=True)
    
    category = request.args.get('category')
    if category and category != 'All':
        cat = Category.query.filter_by(name=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
            
    search = request.args.get('search')
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%'))
        
    sort = request.args.get('sort', 'default')
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'name_az':
        query = query.order_by(Product.name.asc())
        
    products = query.all()
    categories = Category.query.all()
    
    # Get user wishlist safely
    user_wishlist: List[int] = []
    if current_user.is_authenticated:
        wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
        user_wishlist = [w.product_id for w in wishlist_items]
        
    return render_template('catalog.html', products=products, categories=categories, wishlist=user_wishlist)

@main_bp.route('/wishlist', methods=['GET'])
@login_required
def wishlist() -> Any:
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    products = [item.product for item in wishlist_items]
    return render_template('wishlist.html', products=products)

@main_bp.route('/api/wishlist/toggle', methods=['POST'])
@login_required
def toggle_wishlist() -> Any:
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({"error": "Product ID required"}), 400
        
    wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({"status": "removed", "message": "Removed from wishlist"}), 200
    else:
        wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        return jsonify({"status": "added", "message": "Added to wishlist"}), 200

@main_bp.route('/cart', methods=['GET'])
@login_required
def cart() -> Any:
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal)

@main_bp.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart() -> Any:
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({"error": "Product ID required"}), 400
        
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(item)
        
    db.session.commit()
    return jsonify({"message": "Added to cart"}), 200

@main_bp.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart() -> Any:
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity')
    
    if quantity is None or item_id is None:
        return jsonify({"error": "Invalid data"}), 400
        
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404
        
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
        
    db.session.commit()
    return jsonify({"message": "Cart updated"}), 200

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile() -> Any:
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        if username:
            current_user.username = username
            db.session.commit()
            flash('Profile updated successfully', 'success')
            
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    
    return render_template('profile.html', user=current_user, orders=orders, wishlist_count=len(wishlist_items))

@main_bp.route('/checkout', methods=['POST'])
@login_required
def checkout() -> Any:
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400
        
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    order = Order(user_id=current_user.id, total_amount=total_amount)
    db.session.add(order)
    db.session.flush() # Get order ID
    
    for item in cart_items:
        order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.product.price)
        db.session.add(order_item)
        db.session.delete(item) # Remove from cart
        
    db.session.commit()
    return jsonify({"message": "Order placed successfully", "order_id": order.id}), 200

@main_bp.route('/suggestion', methods=['POST'])
def submit_suggestion() -> Any:
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', current_user.username if current_user.is_authenticated else '')
    message = data.get('message')
    
    if not username or not message:
        return jsonify({"error": "Username and message are required"}), 400
        
    suggestion = Suggestion(name=username, message=message)
    db.session.add(suggestion)
    db.session.commit()
    
    if request.is_json:
        return jsonify({"message": "Suggestion submitted"}), 200
    flash("Thank you for your feedback!", "success")
    return redirect(url_for('main.index'))
