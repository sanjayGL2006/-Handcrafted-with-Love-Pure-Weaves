# basilisk: file-disabled[BSK-E0011]
# ============================================================
#  Pure Weaves - Backend (Python Flask)
#  File: index.py
#  Description: Complete e-commerce backend with:
#    - User Authentication (Google only)
#    - Product Management
#    - Cart & Orders
#    - Admin Panel
#    - Coupon System
#    - Security Features
# ============================================================

from flask import Flask, request, jsonify, session, redirect, make_response, render_template_string, send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # type: ignore
from flask_cors import CORS  # type: ignore
from functools import wraps
from typing import Any, Callable, Union, Tuple, Dict, List
import random, datetime, os, jwt, time, io

RouteResponse = Union[Response, Tuple[Response, int]]

app = Flask(__name__)

# ─── SECURITY CONFIG ─────────────────────────────────────────
app.config['SECRET_KEY']           = os.environ.get('SECRET_KEY', 'PureWeaves@Shivamogga#2024!SecureKey')

# Copy SQLite DB to /tmp for write access in Vercel serverless environment
if os.environ.get('VERCEL') == '1':
    import shutil
    try:
        os.makedirs('/tmp', exist_ok=True)
        original_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'pureweaves.db')
        writable_db = '/tmp/pureweaves.db'
        if os.path.exists(original_db) and not os.path.exists(writable_db):
            shutil.copy2(original_db, writable_db)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/pureweaves.db'
    except Exception as e:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pureweaves.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///pureweaves.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_EXPIRY_HOURS']     = 24
app.config['MAX_LOGIN_ATTEMPTS']   = 5

db    = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ─── DATABASE MODELS ──────────────────────────────────────────

class User(db.Model):
    """User table - stores all customer information"""
    __tablename__ = 'users'
    __allow_unmapped__ = True
    id: Any            = db.Column(db.Integer, primary_key=True)
    name: Any          = db.Column(db.String(100), nullable=False)
    mobile: Any        = db.Column(db.String(15), unique=True, nullable=True)
    email: Any         = db.Column(db.String(120), unique=True, nullable=True)
    google_id: Any     = db.Column(db.String(200), unique=True, nullable=True)
    password_hash: Any = db.Column(db.String(200), nullable=True)
    is_admin: Any      = db.Column(db.Boolean, default=False)
    is_active: Any     = db.Column(db.Boolean, default=True)
    login_attempts: Any = db.Column(db.Integer, default=0)
    created_at: Any    = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    orders: Any        = db.relationship('Order', backref='user', lazy=True)
    cart_items: Any    = db.relationship('CartItem', backref='user', lazy=True)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class Product(db.Model):
    """Product table - stores all kuchu/bunch designs"""
    __tablename__ = 'products'
    __allow_unmapped__ = True
    id: Any          = db.Column(db.Integer, primary_key=True)
    name: Any        = db.Column(db.String(200), nullable=False)
    code: Any        = db.Column(db.String(50), unique=True, nullable=True)
    category: Any    = db.Column(db.String(100), nullable=False)
    description: Any = db.Column(db.Text, nullable=False)
    price_min: Any   = db.Column(db.Float, nullable=False)
    price_max: Any   = db.Column(db.Float, nullable=False)
    price: Any       = db.Column(db.Float, nullable=True)
    image_path: Any  = db.Column(db.String(500), nullable=True)
    is_active: Any   = db.Column(db.Boolean, default=True)
    stock: Any       = db.Column(db.Integer, default=100)
    quantity: Any    = db.Column(db.Integer, default=100)
    created_at: Any  = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    cart_items: Any  = db.relationship('CartItem', backref='product', lazy=True)
    order_items: Any = db.relationship('OrderItem', backref='product', lazy=True)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        if self.price is None:
            try:
                self.price = float(self.price_min)
            except:
                self.price = 0.0
        if self.quantity is None:
            try:
                self.quantity = int(self.stock)
            except:
                self.quantity = 100


class CartItem(db.Model):
    """Cart table - stores items in customer cart"""
    __tablename__ = 'cart_items'
    __allow_unmapped__ = True
    id: Any         = db.Column(db.Integer, primary_key=True)
    user_id: Any    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id: Any = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity: Any   = db.Column(db.Integer, default=1)
    added_at: Any   = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class Order(db.Model):
    """Order table - stores all customer orders"""
    __tablename__ = 'orders'
    __allow_unmapped__ = True
    id: Any           = db.Column(db.Integer, primary_key=True)
    user_id: Any      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount: Any = db.Column(db.Float, nullable=False)
    coupon_code: Any  = db.Column(db.String(50), nullable=True)
    discount: Any     = db.Column(db.Float, default=0)
    status: Any       = db.Column(db.String(50), default='pending')
    whatsapp_sent: Any = db.Column(db.Boolean, default=False)
    created_at: Any   = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    items: Any        = db.relationship('OrderItem', backref='order', lazy=True)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class OrderItem(db.Model):
    """Order items - each product in an order"""
    __tablename__ = 'order_items'
    __allow_unmapped__ = True
    id: Any         = db.Column(db.Integer, primary_key=True)
    order_id: Any   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id: Any = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity: Any   = db.Column(db.Integer, nullable=False)
    price: Any      = db.Column(db.Float, nullable=False)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class Coupon(db.Model):
    """Coupon table - discount codes created by admin"""
    __tablename__ = 'coupons'
    __allow_unmapped__ = True
    id: Any              = db.Column(db.Integer, primary_key=True)
    code: Any            = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent: Any = db.Column(db.Float, nullable=False)
    max_uses: Any        = db.Column(db.Integer, default=100)
    used_count: Any      = db.Column(db.Integer, default=0)
    expires_at: Any      = db.Column(db.DateTime, nullable=False)
    is_active: Any       = db.Column(db.Boolean, default=True)
    created_at: Any      = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class Suggestion(db.Model):
    """Suggestion/Feedback from website visitors"""
    __tablename__ = 'suggestions'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    name: Any = db.Column(db.String(120), nullable=False)
    email: Any = db.Column(db.String(200), nullable=True)
    message: Any = db.Column(db.Text, nullable=False)
    created_at: Any = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class Customer(db.Model):
    """Customer table for Billing System"""
    __tablename__ = 'customers'
    __allow_unmapped__ = True
    id: Any          = db.Column(db.Integer, primary_key=True)
    name: Any        = db.Column(db.String(100), nullable=False)
    mobile: Any      = db.Column(db.String(15), unique=True, nullable=False)
    email: Any       = db.Column(db.String(120), nullable=True)
    address: Any     = db.Column(db.Text, nullable=True)
    registration_date: Any = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    bills: Any       = db.relationship('Bill', backref='customer', lazy=True)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class Review(db.Model):
    """Review feedback table"""
    __tablename__ = 'reviews'
    __allow_unmapped__ = True
    id: Any            = db.Column(db.Integer, primary_key=True)
    customer_name: Any = db.Column(db.String(100), nullable=False)
    mobile: Any        = db.Column(db.String(15), nullable=False)
    rating: Any        = db.Column(db.Integer, nullable=False)
    review: Any        = db.Column(db.Text, nullable=False)
    created_at: Any    = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class Bill(db.Model):
    """Invoice / Billing transaction"""
    __tablename__ = 'bills'
    __allow_unmapped__ = True
    id: Any             = db.Column(db.Integer, primary_key=True)
    invoice_number: Any = db.Column(db.String(50), unique=True, nullable=False)
    customer_id: Any    = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    subtotal: Any       = db.Column(db.Float, nullable=False)
    tax: Any            = db.Column(db.Float, nullable=False)
    discount: Any       = db.Column(db.Float, default=0.0)
    total: Any          = db.Column(db.Float, nullable=False)
    created_at: Any     = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    items: Any          = db.relationship('BillItem', backref='bill', lazy=True, cascade="all, delete-orphan")

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class BillItem(db.Model):
    """Line items inside a bill"""
    __tablename__ = 'bill_items'
    __allow_unmapped__ = True
    id: Any         = db.Column(db.Integer, primary_key=True)
    bill_id: Any    = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    product_id: Any = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity: Any   = db.Column(db.Integer, nullable=False)
    price: Any      = db.Column(db.Float, nullable=False)
    product: Any    = db.relationship('Product', lazy=True)

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


# ─── HELPER FUNCTIONS ─────────────────────────────────────────

RATE_LIMIT_RECORDS: Dict[Tuple[Any, str], List[float]] = {}

def rate_limit(limit: int = 10, period: int = 60) -> Callable[..., Any]:
    """Simple in-memory rate-limiter decorator"""
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ip and ',' in ip:
                ip = ip.split(',')[0].strip()
            endpoint = request.endpoint or f.__name__
            key = (ip, endpoint)
            now = time.time()
            timestamps = RATE_LIMIT_RECORDS.get(key, [])
            timestamps = [t for t in timestamps if now - t < period]
            if len(timestamps) >= limit:
                return jsonify({'error': 'Too many requests. Please try again later.'}), 429
            timestamps.append(now)
            RATE_LIMIT_RECORDS[key] = timestamps
            return f(*args, **kwargs)
        return decorated
    return decorator

def generate_token(user_id: int) -> str:
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRY_HOURS'])
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f: Callable[..., RouteResponse]) -> Callable[..., RouteResponse]:
    """Decorator to protect routes that need login"""
    @wraps(f)
    def decorated(*args: object, **kwargs: object) -> RouteResponse:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Login required'}), 401
        try:
            data    = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user or not current_user.is_active:
                return jsonify({'error': 'Invalid user'}), 401
        except:
            return jsonify({'error': 'Invalid or expired token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f: Callable[..., RouteResponse]) -> Callable[..., RouteResponse]:
    """Decorator to protect admin-only routes"""
    @wraps(f)
    def decorated(*args: object, **kwargs: object) -> RouteResponse:
        admin_secret = request.headers.get('X-Admin-Secret', '')
        expected_secret = os.environ.get('ADMIN_PANEL_SECRET', 'pureweaves2024')
        if admin_secret and admin_secret == expected_secret:
            current_user = User.query.filter_by(is_admin=True).first()
            if not current_user:
                current_user = User(name="Admin", email="admin@pureweaves.com", is_admin=True)
            return f(current_user, *args, **kwargs)

        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Login required'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user or not current_user.is_active or not current_user.is_admin:
                return jsonify({'error': 'Admin access required'}), 403
        except:
            return jsonify({'error': 'Invalid or expired token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# ─── AUTH ROUTES ─────────────────────────────────────────────

@app.route('/api/auth/google', methods=['POST'])
def google_login() -> RouteResponse:
    """
    Google OAuth login
    POST /api/auth/google
    Body: { "google_id": "...", "email": "...", "name": "..." }
    """
    data = request.json or {}
    google_id = data.get('google_id')
    email     = data.get('email')
    name      = data.get('name')
    if not google_id or not email:
        return jsonify({'error': 'Invalid Google account data'}), 400
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
            if name and not user.name:
                user.name = name
            db.session.commit()
        else:
            if not name:
                name = email.split('@')[0] if email else 'Google User'
            user = User(name=name, email=email, google_id=google_id)
            db.session.add(user)
            db.session.commit()
    token = generate_token(user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'email': user.email}}), 200


@app.route('/api/auth/register', methods=['POST'])
@rate_limit(limit=5, period=60)
def register() -> RouteResponse:
    """
    Register with email/password
    POST /api/auth/register
    Body: { "name": "...", "email": "...", "password": "...", "confirm_password": "..." }
    """
    data = request.json or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    if not name or not email or not password or not confirm_password:
        return jsonify({'error': 'Name, email and password required'}), 400
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=name, email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    token = generate_token(user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'email': user.email}}), 201


@app.route('/api/auth/login', methods=['POST'])
@rate_limit(limit=5, period=60)
def login() -> RouteResponse:
    """
    Login with email/password
    POST /api/auth/login
    Body: { "email": "...", "password": "..." }
    """
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash:
        return jsonify({'error': 'Invalid credentials'}), 401
    # Basic lockout
    if user.login_attempts and user.login_attempts >= app.config.get('MAX_LOGIN_ATTEMPTS', 5):
        return jsonify({'error': 'Account locked due to too many failed attempts'}), 403
    if not bcrypt.check_password_hash(user.password_hash, password):
        user.login_attempts = (user.login_attempts or 0) + 1
        db.session.commit()
        return jsonify({'error': 'Invalid credentials'}), 401
    # Successful login
    user.login_attempts = 0
    db.session.commit()
    token = generate_token(user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'email': user.email}}), 200

@app.route('/logout')
def logout() -> RouteResponse:
    session.clear()
    response = make_response(redirect('/login.html?logout=true'))
    response.delete_cookie('session', path='/')
    return response

# ─── PRODUCT ROUTES ──────────────────────────────────────────

@app.route('/api/products', methods=['GET'])
def get_products() -> RouteResponse:
    """Get all active products, optionally filter by category"""
    category = request.args.get('category')
    query    = Product.query.filter_by(is_active=True)
    if category and category != 'All':
        query = query.filter_by(category=category)
    products = query.all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'category': p.category,
        'description': p.description, 'price_min': p.price_min,
        'price_max': p.price_max,
        'image_path': p.image_path if (p.image_path and p.image_path.strip() != '') else f"/app/static/images/product_{p.id}.jpg",
        'stock': p.stock
    } for p in products]), 200

# ─── CART ROUTES ─────────────────────────────────────────────

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user: User) -> RouteResponse:
    """Get current user's cart items"""
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': i.id, 'product_id': i.product_id,
        'name': i.product.name, 'price_min': i.product.price_min,
        'quantity': i.quantity,
        'image_path': i.product.image_path if (i.product.image_path and i.product.image_path.strip() != '') else f"/app/static/images/product_{i.product.id}.jpg"
    } for i in items]), 200

@app.route('/api/cart/add', methods=['POST'])
@token_required
def add_to_cart(current_user: User) -> RouteResponse:
    """Add item to cart"""
    product_id = request.json.get('product_id')
    quantity   = request.json.get('quantity', 1)
    product    = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    existing = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Added to cart'}), 200

@app.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@token_required
def remove_from_cart(current_user: User, item_id: int) -> RouteResponse:
    """Remove item from cart"""
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Removed from cart'}), 200

# ─── COUPON ROUTES ───────────────────────────────────────────

@app.route('/api/coupon/validate', methods=['POST'])
@token_required
def validate_coupon(current_user: User) -> RouteResponse:
    """Validate a coupon code"""
    code   = request.json.get('code', '').upper().strip()
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    if not coupon:
        return jsonify({'error': 'Invalid coupon code'}), 400
    if datetime.datetime.utcnow() > coupon.expires_at:
        return jsonify({'error': 'Coupon has expired'}), 400
    if coupon.used_count >= coupon.max_uses:
        return jsonify({'error': 'Coupon usage limit reached'}), 400
    return jsonify({'discount_percent': coupon.discount_percent, 'code': coupon.code}), 200

# ─── ORDER ROUTES ────────────────────────────────────────────

@app.route('/api/order/place', methods=['POST'])
@token_required
@rate_limit(limit=5, period=60)
def place_order(current_user: User) -> RouteResponse:
    """Place an order"""
    data = request.json or {}
    coupon_code = data.get('coupon_code', '')
    items_list = data.get('items', [])
    
    db_items = []
    if items_list:
        for item in items_list:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            product = Product.query.get(product_id)
            if product:
                if product.stock < quantity:
                    return jsonify({'error': f'Product "{product.name}" is out of stock or has insufficient stock'}), 400
                db_items.append({'product': product, 'quantity': quantity})
    else:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for ci in cart_items:
            if ci.product.stock < ci.quantity:
                return jsonify({'error': f'Product "{ci.product.name}" is out of stock or has insufficient stock'}), 400
            db_items.append({'product': ci.product, 'quantity': ci.quantity})
            
    if not db_items:
        return jsonify({'error': 'Cart is empty'}), 400
        
    total = sum(i['product'].price_min * i['quantity'] for i in db_items)
    discount = 0
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code.upper(), is_active=True).first()
        if coupon:
            if datetime.datetime.utcnow() > coupon.expires_at:
                return jsonify({'error': 'Coupon has expired'}), 400
            if coupon.used_count >= coupon.max_uses:
                return jsonify({'error': 'Coupon usage limit reached'}), 400
            discount = total * (coupon.discount_percent / 100)
            coupon.used_count += 1
            
    order = Order(user_id=current_user.id, total_amount=total - discount,
                  coupon_code=coupon_code, discount=discount)
    db.session.add(order)
    db.session.flush()
    
    for item in db_items:
        p = item['product']
        q = item['quantity']
        p.stock = max(0, p.stock - q)
        
        order_item = OrderItem(order_id=order.id, product_id=p.id,
                               quantity=q, price=p.price_min)
        db.session.add(order_item)
        
    if not items_list:
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
    db.session.commit()
    return jsonify({'message': 'Order placed!', 'order_id': order.id, 'total': total - discount}), 200

# ─── ADMIN ROUTES ────────────────────────────────────────────

@app.route('/api/admin/product/add', methods=['POST'])
@admin_required
def add_product(current_user: User) -> RouteResponse:
    """Admin: Add new design/product"""
    data    = request.json
    product = Product(
        name=data['name'], category=data['category'],
        description=data['description'], price_min=data['price_min'],
        price_max=data['price_max'], image_path=data.get('image_path', ''),
        stock=data.get('stock', 100)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Design added!', 'id': product.id}), 201

@app.route('/api/admin/coupon/create', methods=['POST'])
@admin_required
def create_coupon(current_user: User) -> RouteResponse:
    """Admin: Create new coupon code"""
    data   = request.json
    coupon = Coupon(
        code=data['code'].upper(), discount_percent=data['discount_percent'],
        max_uses=data.get('max_uses', 100),
        expires_at=datetime.datetime.strptime(data['expires_at'], '%Y-%m-%d')
    )
    db.session.add(coupon)
    db.session.commit()
    return jsonify({'message': f'Coupon {coupon.code} created!'}), 201

@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def get_all_orders(current_user: User) -> RouteResponse:
    """Admin: View all orders"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([{
        'id': o.id,
        'user_id': o.user.id,
        'user': o.user.name,
        'mobile': o.user.mobile,
        'total': o.total_amount,
        'status': o.status,
        'coupon': o.coupon_code,
        'discount': o.discount,
        'created_at': o.created_at.strftime('%d-%m-%Y %H:%M'),
        'items': [{
            'id': item.id,
            'product_id': item.product_id,
            'name': item.product.name,
            'qty': item.quantity,
            'price': item.price
        } for item in o.items]
    } for o in orders]), 200

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_stats(current_user: User) -> RouteResponse:
    """Admin: Dashboard statistics"""
    return jsonify({
        'total_users':    User.query.count(),
        'total_orders':   Order.query.count(),
        'total_products': Product.query.filter_by(is_active=True).count(),
        'total_revenue':  db.session.query(db.func.sum(Order.total_amount)).scalar() or 0,
        'active_coupons': Coupon.query.filter_by(is_active=True).count()
    }), 200

@app.route('/api/admin/users', methods=['GET'])
def get_all_users() -> RouteResponse:
    """Admin: User listing for dashboard"""
    admin_secret = request.headers.get('X-Admin-Secret', '')
    expected_secret = os.environ.get('ADMIN_PANEL_SECRET', 'pureweaves2024')
    if admin_secret != expected_secret:
        return jsonify({'error': 'Admin access required'}), 403
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'mobile': u.mobile,
        'password_hash': u.password_hash,
        'created_at': u.created_at.strftime('%d-%m-%Y %H:%M'),
        'is_admin': u.is_admin
    } for u in users]), 200

@app.route('/api/admin/suggestions', methods=['GET'])
@admin_required
def get_all_suggestions(current_user: User) -> RouteResponse:
    """Admin: View all customer suggestions"""
    suggestions = Suggestion.query.order_by(Suggestion.created_at.desc()).all()
    return jsonify([{
        'id': s.id, 'name': s.name,
        'message': s.message, 'created_at': s.created_at.strftime('%d-%m-%Y %H:%M')
    } for s in suggestions]), 200


# ─── EXTRA ADMIN ENDPOINTS FOR CLIENT-SIDE DASHBOARD ───────────────────

@app.route('/api/admin/login', methods=['POST'])
def admin_login() -> RouteResponse:
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
        
    user = User.query.filter((User.email == username) | (User.name == username)).first()
    if username == 'admin':
        if user and bcrypt.check_password_hash(user.password_hash, password):
            secret = os.environ.get('ADMIN_PANEL_SECRET', 'pureweaves2024')
            return jsonify({'secret': secret}), 200
            
    if user and user.is_admin and bcrypt.check_password_hash(user.password_hash, password):
        secret = os.environ.get('ADMIN_PANEL_SECRET', 'pureweaves2024')
        return jsonify({'secret': secret}), 200
        
    return jsonify({'error': 'Invalid admin credentials'}), 401


@app.route('/api/admin/product/edit/<int:prod_id>', methods=['POST'])
@admin_required
def edit_product(current_user: User, prod_id: int) -> RouteResponse:
    data = request.json or {}
    product = Product.query.get(prod_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    product.name = data.get('name', product.name)
    product.category = data.get('category', product.category)
    product.description = data.get('description', product.description)
    
    if 'price_min' in data:
        product.price_min = float(data['price_min'])
        product.price = float(data['price_min'])
    if 'price_max' in data:
        product.price_max = float(data['price_max'])
    if 'quantity' in data:
        product.quantity = int(data['quantity'])
        product.stock = int(data['quantity'])
    if 'stock' in data:
        product.stock = int(data['stock'])
        product.quantity = int(data['stock'])
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])
    if 'image_path' in data:
        product.image_path = data['image_path']
        
    db.session.commit()
    return jsonify({'message': 'Product updated successfully!'}), 200


@app.route('/api/admin/product/delete/<int:prod_id>', methods=['DELETE'])
@admin_required
def delete_product(current_user: User, prod_id: int) -> RouteResponse:
    product = Product.query.get(prod_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
        
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully!'}), 200


@app.route('/api/admin/customer/add', methods=['POST'])
@admin_required
def add_customer_alias(current_user: User) -> RouteResponse:
    data = request.json or {}
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    
    if not name or not mobile:
        return jsonify({'error': 'Customer name and mobile number are required'}), 400
        
    existing = Customer.query.filter_by(mobile=mobile).first()
    if existing:
        return jsonify({'error': 'A customer with this mobile number already exists'}), 400
        
    c = Customer(name=name, mobile=mobile, email=email, address=address)
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'Customer added!', 'customer': {
        'id': c.id, 'name': c.name, 'mobile': c.mobile
    }}), 201


@app.route('/api/admin/customer/edit/<int:cust_id>', methods=['POST'])
@admin_required
def edit_customer_alias(current_user: User, cust_id: int) -> RouteResponse:
    c = Customer.query.get(cust_id)
    if not c:
        return jsonify({'error': 'Customer not found'}), 404
    data = request.json or {}
    c.name = data.get('name', c.name).strip()
    c.mobile = data.get('mobile', c.mobile).strip()
    c.email = data.get('email', c.email).strip()
    c.address = data.get('address', c.address).strip()
    
    if not c.name or not c.mobile:
        return jsonify({'error': 'Customer name and mobile number are required'}), 400
        
    db.session.commit()
    return jsonify({'message': 'Customer updated successfully!'}), 200


@app.route('/api/admin/customer/delete/<int:cust_id>', methods=['DELETE'])
@admin_required
def delete_customer_alias(current_user: User, cust_id: int) -> RouteResponse:
    c = Customer.query.get(cust_id)
    if not c:
        return jsonify({'error': 'Customer not found'}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully!'}), 200


@app.route('/api/admin/reviews', methods=['GET'])
@admin_required
def get_admin_reviews(current_user: User) -> RouteResponse:
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return jsonify([{
        'id': r.id,
        'customer_name': r.customer_name,
        'mobile': r.mobile,
        'rating': r.rating,
        'review': r.review,
        'created_at': r.created_at.strftime('%d-%m-%Y %H:%M')
    } for r in reviews]), 200


@app.route('/api/admin/coupons', methods=['GET'])
@admin_required
def get_admin_coupons(current_user: User) -> RouteResponse:
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return jsonify([{
        'id': c.id,
        'code': c.code,
        'discount': c.discount_percent,
        'max_uses': c.max_uses,
        'used_count': c.used_count,
        'expiry': c.expires_at.strftime('%Y-%m-%d'),
        'is_active': c.is_active,
        'description': f"{c.discount_percent}% off discount coupon"
    } for c in coupons]), 200


import json
SETTINGS_FILE = 'settings.json'

@app.route('/api/admin/settings', methods=['POST'])
@admin_required
def save_settings(current_user: User) -> RouteResponse:
    data = request.json or {}
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return jsonify({'message': 'Settings saved successfully!'}), 200


@app.route('/api/admin/change-password', methods=['POST'])
@admin_required
def change_admin_password(current_user: User) -> RouteResponse:
    data = request.json or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password are required'}), 400
        
    admin_user = User.query.filter_by(is_admin=True).first()
    if not admin_user:
        return jsonify({'error': 'Admin user not found'}), 404
        
    if not bcrypt.check_password_hash(admin_user.password_hash, current_password):
        return jsonify({'error': 'Incorrect current password'}), 400
        
    admin_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    return jsonify({'message': 'Password changed successfully!'}), 200


@app.route('/api/admin/clear-logs', methods=['POST'])
@admin_required
def clear_logs(current_user: User) -> RouteResponse:
    try:
        BillItem.query.delete()
        Bill.query.delete()
        db.session.commit()
        return jsonify({'message': 'Logs cleared successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/bills/add', methods=['POST'])
def handle_bills_add() -> None:
    return handle_bills()


# ─── SUGGESTION ROUTES ────────────────────────────────────────

@app.route('/api/suggestions', methods=['POST'])
@rate_limit(limit=5, period=60)
def submit_suggestion() -> RouteResponse:
    """Submit a customer suggestion (public endpoint)"""
    data = request.json
    if not data.get('name') or not data.get('message'):
        return jsonify({'error': 'Name and message are required'}), 400
    suggestion = Suggestion(
        name=data['name'],
        message=data['message']
    )
    db.session.add(suggestion)
    db.session.commit()
    return jsonify({'message': 'Thank you for your suggestion!', 'success': True}), 201


# ─── REVIEWS & CUSTOMER FEEDBACK ROUTES ───────────────────────

@app.route('/api/reviews', methods=['POST'])
def submit_review() -> None:
    data = request.json or {}
    customer_name = data.get('customer_name')
    mobile = data.get('mobile')
    rating = data.get('rating')
    review_msg = data.get('review')
    
    if not customer_name or not mobile or not rating or not review_msg:
        return jsonify({'error': 'All fields are required'}), 400  # type: ignore[BSK-E0013]
    try:
        rating_int = int(rating)
        if not (1 <= rating_int <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5 stars'}), 400
    except:
        return jsonify({'error': 'Invalid rating'}), 400
        
    rev = Review(customer_name=customer_name, mobile=mobile, rating=rating_int, review=review_msg)
    db.session.add(rev)
    db.session.commit()
    return jsonify({'message': 'Thank you for your review!', 'success': True}), 201


@app.route('/api/reviews', methods=['GET'])
def get_reviews() -> None:
    q = request.args.get('search', '').strip()
    rating_filter = request.args.get('rating')
    
    query = Review.query
    if q:
        query = query.filter(db.or_(Review.customer_name.like(f'%{q}%'), Review.review.like(f'%{q}%')))
    if rating_filter and rating_filter != 'all':
        try:
            query = query.filter_by(rating=int(rating_filter))
        except:
            pass
            
    reviews = query.order_by(Review.created_at.desc()).all()
    avg_rating = db.session.query(db.func.avg(Review.rating)).scalar() or 0.0
    
    return jsonify({
        'reviews': [{
            'id': r.id,
            'customer_name': r.customer_name,
            'mobile': r.mobile,
            'rating': r.rating,
            'review': r.review,
            'created_at': r.created_at.strftime('%d-%m-%Y %H:%M')
        } for r in reviews],
        'average_rating': round(avg_rating, 2)
    }), 200


@app.route('/api/admin/reviews/delete/<int:review_id>', methods=['DELETE'])
@admin_required
def delete_review(current_user: User, review_id: int) -> None:
    rev = Review.query.get(review_id)
    if not rev:
        return jsonify({'error': 'Review not found'}), 404
    db.session.delete(rev)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully', 'success': True}), 200


# ─── CUSTOMERS MANAGEMENT ROUTES ──────────────────────────────

@app.route('/api/admin/customers', methods=['GET', 'POST'])
@admin_required
def handle_customers(current_user: User) -> RouteResponse:
    if request.method == 'GET':
        q = request.args.get('search', '').strip().lower()
        query = Customer.query
        if q:
            query = query.filter(db.or_(
                Customer.name.like(f'%{q}%'),
                Customer.mobile.like(f'%{q}%'),
                Customer.email.like(f'%{q}%')
            ))
        custs = query.order_by(Customer.registration_date.desc()).all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'mobile': c.mobile,
            'email': c.email or '',
            'address': c.address or '',
            'registration_date': c.registration_date.strftime('%d-%m-%Y %H:%M') if c.registration_date else '',
            'purchase_history': [{
                'invoice_number': b.invoice_number,
                'total': b.total,
                'date': b.created_at.strftime('%d-%m-%Y') if b.created_at else ''
            } for b in c.bills]
        } for c in custs]), 200

    elif request.method == 'POST':
        data = request.json or {}
        name = data.get('name', '').strip()
        mobile = data.get('mobile', '').strip()
        email = data.get('email', '').strip()
        address = data.get('address', '').strip()
        
        if not name or not mobile:
            return jsonify({'error': 'Customer name and mobile number are required'}), 400
        
        existing = Customer.query.filter_by(mobile=mobile).first()
        if existing:
            return jsonify({'error': 'A customer with this mobile number already exists'}), 400
            
        c = Customer(name=name, mobile=mobile, email=email, address=address)
        db.session.add(c)
        db.session.commit()
        return jsonify({'message': 'Customer added!', 'customer': {
            'id': c.id, 'name': c.name, 'mobile': c.mobile
        }}), 201


@app.route('/api/admin/customers/<int:cust_id>', methods=['PUT', 'DELETE'])
@admin_required
def handle_customer_detail(current_user: User, cust_id: int) -> None:
    c = Customer.query.get(cust_id)
    if not c:
        return jsonify({'error': 'Customer not found'}), 404
        
    if request.method == 'PUT':
        data = request.json or {}
        c.name = data.get('name', c.name).strip()
        c.mobile = data.get('mobile', c.mobile).strip()
        c.email = data.get('email', c.email).strip()
        c.address = data.get('address', c.address).strip()
        
        if not c.name or not c.mobile:
            return jsonify({'error': 'Customer name and mobile number are required'}), 400
            
        db.session.commit()
        return jsonify({'message': 'Customer updated successfully!'}), 200
        
    elif request.method == 'DELETE':
        db.session.delete(c)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully!'}), 200


# ─── BILLING SYSTEM ROUTES ────────────────────────────────────

@app.route('/api/admin/bills', methods=['GET', 'POST'])
def handle_bills() -> None:
    if request.method == 'GET':
        bills = Bill.query.order_by(Bill.created_at.desc()).all()
        return jsonify([{
            'id': b.id,
            'invoice_number': b.invoice_number,
            'customer_name': b.customer.name,
            'customer_mobile': b.customer.mobile,
            'customer_id': b.customer_id,
            'subtotal': b.subtotal,
            'tax': b.tax,
            'discount': b.discount,
            'total': b.total,
            'created_at': b.created_at.strftime('%d-%m-%Y %H:%M'),
            'items': [{
                'product_id': item.product_id,
                'name': item.product.name,
                'qty': item.quantity,
                'price': item.price
            } for item in b.items]
        } for b in bills]), 200

    elif request.method == 'POST':
        data = request.json or {}
        customer_id = data.get('customer_id')
        items = data.get('items', [])
        coupon_code = data.get('coupon_code', '').strip().upper()
        
        if not customer_id and data.get('customer_name'):
            mobile = data.get('customer_mobile', '0000000000')
            cust = Customer.query.filter_by(mobile=mobile).first()
            if not cust:
                cust = Customer(
                    name=data.get('customer_name'),
                    mobile=mobile,
                    email=data.get('customer_email'),
                    address=data.get('customer_address')
                )
                db.session.add(cust)
                db.session.flush()
            customer_id = cust.id
            
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Invalid customer'}), 400
        if not items:
            return jsonify({'error': 'No products selected'}), 400
            
        subtotal = 0.0
        db_items = []
        
        for i in items:
            p_id = i.get('product_id')
            qty = int(i.get('quantity', 1))
            product = Product.query.get(p_id)
            if not product:
                return jsonify({'error': f'Product ID {p_id} not found'}), 400
                
            current_stock = product.quantity if product.quantity is not None else product.stock
            if current_stock < qty:
                return jsonify({'error': f'Product "{product.name}" has insufficient stock ({current_stock} remaining)'}), 400
                
            price = product.price if product.price is not None else product.price_min
            subtotal += price * qty
            db_items.append({'product': product, 'quantity': qty, 'price': price})
            
        discount = 0.0
        if coupon_code:
            coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
            if coupon:
                if datetime.datetime.utcnow() <= coupon.expires_at and coupon.used_count < coupon.max_uses:
                    discount = subtotal * (coupon.discount_percent / 100.0)
                    coupon.used_count += 1
                    
        tax = (subtotal - discount) * 0.05
        total = (subtotal - discount) + tax
        
        invoice_number = 'INV' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(10, 99))
        
        bill = Bill(
            invoice_number=invoice_number,
            customer_id=customer_id,
            subtotal=subtotal,
            tax=tax,
            discount=discount,
            total=total
        )
        db.session.add(bill)
        db.session.flush()
        
        for db_i in db_items:
            product = db_i['product']
            qty = db_i['quantity']
            
            if product.quantity is not None:
                product.quantity = max(0, product.quantity - qty)
            if product.stock is not None:
                product.stock = max(0, product.stock - qty)
                
            b_item = BillItem(
                bill_id=bill.id,
                product_id=product.id,
                quantity=qty,
                price=db_i['price']
            )
            db.session.add(b_item)
            
        db.session.commit()
        return jsonify({
            'message': 'Bill generated successfully!',
            'bill_id': bill.id,
            'invoice_number': bill.invoice_number,
            'total': bill.total
        }), 201


@app.route('/api/admin/bills/pdf/<int:bill_id>', methods=['GET'])
def get_bill_pdf(bill_id: int) -> None:
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
        
    items = [{
        'name': item.product.name,
        'qty': item.quantity,
        'price': item.price
    } for item in bill.items]
    
    customer = {
        'name': bill.customer.name,
        'mobile': bill.customer.mobile,
        'email': bill.customer.email,
        'address': bill.customer.address
    }
    
    try:
        from invoice_generator import generate_pdf_invoice
    except Exception as _e:
        return jsonify({'error':'Invoice generation dependency error','detail':str(_e)}),500

    pdf_bytes = generate_pdf_invoice(
        invoice_no=bill.invoice_number,
        date=bill.created_at.strftime('%d-%m-%Y'),
        customer=customer,
        items=items,
        subtotal=bill.subtotal,
        tax=bill.tax,
        discount=bill.discount,
        total=bill.total
    )
    
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Invoice_{bill.invoice_number}.pdf'
    return response


@app.route('/api/admin/bills/docx/<int:bill_id>', methods=['GET'])
def get_bill_docx(bill_id: int) -> None:
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
        
    items = [{
        'name': item.product.name,
        'qty': item.quantity,
        'price': item.price
    } for item in bill.items]
    
    customer = {
        'name': bill.customer.name,
        'mobile': bill.customer.mobile,
        'email': bill.customer.email,
        'address': bill.customer.address
    }
    
    try:
        from invoice_generator import generate_docx_invoice
    except Exception as _e:
        return jsonify({'error':'Invoice generation dependency error','detail':str(_e)}),500

    docx_bytes = generate_docx_invoice(
        invoice_no=bill.invoice_number,
        date=bill.created_at.strftime('%d-%m-%Y'),
        customer=customer,
        items=items,
        subtotal=bill.subtotal,
        tax=bill.tax,
        discount=bill.discount,
        total=bill.total
    )
    
    response = make_response(docx_bytes)
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    response.headers['Content-Disposition'] = f'attachment; filename=Invoice_{bill.invoice_number}.docx'
    return response


# Health check and improved error handling

@app.route('/api/_health', methods=['GET'])
def _health_check() -> RouteResponse:
    return jsonify({'status':'ok'}), 200


@app.errorhandler(Exception)
def _handle_global_error(e: Exception) -> RouteResponse:
    # Log to stdout so Vercel captures the stacktrace in logs
    import traceback, sys
    traceback.print_exc(file=sys.stdout)
    return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500


# ─── REPORTS & ANALYTICS ROUTES ────────────────────────────────

@app.route('/api/admin/reports', methods=['GET'])
def get_reports() -> None:
    now = datetime.datetime.now()
    today_start = datetime.datetime(now.year, now.month, now.day)
    
    daily_bills = Bill.query.filter(Bill.created_at >= today_start).all()
    daily_revenue = sum(b.total for b in daily_bills)
    
    week_start = today_start - datetime.timedelta(days=7)
    weekly_bills = Bill.query.filter(Bill.created_at >= week_start).all()
    weekly_revenue = sum(b.total for b in weekly_bills)
    
    month_start = datetime.datetime(now.year, now.month, 1)
    monthly_bills = Bill.query.filter(Bill.created_at >= month_start).all()
    monthly_revenue = sum(b.total for b in monthly_bills)
    
    year_start = datetime.datetime(now.year, 1, 1)
    yearly_bills = Bill.query.filter(Bill.created_at >= year_start).all()
    yearly_revenue = sum(b.total for b in yearly_bills)
    
    total_reviews = Review.query.count()
    avg_rating = db.session.query(db.func.avg(Review.rating)).scalar() or 0.0
    
    all_prods = Product.query.filter_by(is_active=True).all()
    low_stock = []
    for p in all_prods:
        qty = p.quantity if p.quantity is not None else p.stock
        if qty < 5:
            low_stock.append({
                'id': p.id,
                'name': p.name,
                'code': p.code or f"CODE{p.id}",
                'qty': qty
            })
            
    # Recent transaction logs for reports
    bills = Bill.query.order_by(Bill.created_at.desc()).limit(50).all()
    billing_logs = [{
        'id': b.id,
        'customer': b.customer.name,
        'total': b.total,
        'date': b.created_at.strftime('%d-%m-%Y')
    } for b in bills]
    
    # Calculate revenue trends for the last 7 days (rolling chart metrics)
    labels = []
    values = []
    for i in range(6, -1, -1):
        day_date = today_start - datetime.timedelta(days=i)
        day_end = day_date + datetime.timedelta(days=1)
        day_revenue = db.session.query(db.func.sum(Bill.total)).filter(Bill.created_at >= day_date, Bill.created_at < day_end).scalar() or 0.0
        labels.append(day_date.strftime('%a'))
        values.append(round(day_revenue, 2))
    chart_data = {'labels': labels, 'values': values}
            
    return jsonify({
        'daily': {
            'revenue': round(daily_revenue, 2),
            'bills_count': len(daily_bills)
        },
        'weekly': {
            'revenue': round(weekly_revenue, 2),
            'bills_count': len(weekly_bills)
        },
        'monthly': {
            'revenue': round(monthly_revenue, 2),
            'bills_count': len(monthly_bills)
        },
        'yearly': {
            'revenue': round(yearly_revenue, 2),
            'bills_count': len(yearly_bills)
        },
        'analytics': {
            'total_customers': Customer.query.count(),
            'total_revenue': round(db.session.query(db.func.sum(Bill.total)).scalar() or 0.0, 2),
            'total_bills': Bill.query.count(),
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'total_products': Product.query.filter_by(is_active=True).count()
        },
        'low_stock_alerts': low_stock,
        'billing_logs': billing_logs,
        'chart_data': chart_data
    }), 200


@app.route('/api/admin/reports/export/<string:format_type>', methods=['GET'])
def export_reports(format_type: Any) -> None:
    bills = Bill.query.order_by(Bill.created_at.desc()).all()
    
    if format_type == 'csv':
        output = io.StringIO()
        output.write("Invoice Number,Customer Name,Customer Mobile,Subtotal,Tax,Discount,Total,Date\n")
        for b in bills:
            output.write(f"{b.invoice_number},{b.customer.name},{b.customer.mobile},{b.subtotal:.2f},{b.tax:.2f},{b.discount:.2f},{b.total:.2f},{b.created_at.strftime('%d-%m-%Y %H:%M')}\n")
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=PureWeaves_Billing_Report.csv'
        return response
        
    elif format_type == 'excel':
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Billing Report"
        
        headers = ["Invoice Number", "Customer Name", "Customer Mobile", "Subtotal", "Tax", "Discount", "Total", "Date"]
        ws.append(headers)
        
        for b in bills:
            ws.append([
                b.invoice_number,
                b.customer.name,
                b.customer.mobile,
                b.subtotal,
                b.tax,
                b.discount,
                b.total,
                b.created_at.strftime('%d-%m-%Y %H:%M')
            ])
            
        file_stream = io.BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        
        response = make_response(file_stream.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=PureWeaves_Billing_Report.xlsx'
        return response
        
    return jsonify({'error': 'Invalid export format'}), 400


# ─── SECURITY HEADERS & EXPLICIT SERVES ───────────────────────

@app.route('/robots.txt')
def serve_robots() -> Response:
    return send_from_directory('.', 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def serve_sitemap() -> Response:
    return send_from_directory('.', 'sitemap.xml', mimetype='application/xml')

@app.after_request
def add_security_headers(response: Response) -> Response:
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://www.gstatic.com https://identitytoolkit.googleapis.com https://accounts.google.com; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.gstatic.com https://apis.google.com https://accounts.google.com https://cdn.jsdelivr.net; "
        "frame-src 'self' https://pureweaves-63804.firebaseapp.com https://accounts.google.com; "
        "connect-src 'self' https://*.googleapis.com https://identitytoolkit.googleapis.com https://securetoken.googleapis.com;"
    )
    return response

# ─── RUN ─────────────────────────────────────────────────────

# Serve frontend static files from project root so login/index work from same origin
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path: str) -> RouteResponse:
    if path == '' or path == 'index.html':
        return send_from_directory('.', 'index.html')
    if path in ['robots.txt', 'sitemap.xml']:
        return redirect('/' + path)
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("[OK] Database tables created successfully!")
        print("[OK] Pure Weaves backend running at http://localhost:5000")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
