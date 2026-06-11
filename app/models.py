import datetime
from typing import Any
from app import db, login_manager
from flask_login import UserMixin  # type: ignore[missing-import]

@login_manager.user_loader
def load_user(user_id: Any) -> None:
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    username: Any = db.Column(db.String(100), nullable=False)
    email: Any = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: Any = db.Column(db.String(200), nullable=False)
    is_admin: Any = db.Column(db.Boolean, default=False)
    is_active: Any = db.Column(db.Boolean, default=True)
    created_at: Any = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    orders: Any = db.relationship('Order', backref='user', lazy=True)
    cart_items: Any = db.relationship('CartItem', backref='user', lazy=True)
    wishlist: Any = db.relationship('Wishlist', backref='user', lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

class Category(db.Model):
    __tablename__ = 'categories'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    name: Any = db.Column(db.String(100), unique=True, nullable=False)
    description: Any = db.Column(db.Text, nullable=True)
    
    products: Any = db.relationship('Product', backref='category_rel', lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

class Product(db.Model):
    __tablename__ = 'products'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    name: Any = db.Column(db.String(200), nullable=False)
    category_id: Any = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    description: Any = db.Column(db.Text, nullable=False)
    price: Any = db.Column(db.Float, nullable=False) # Simplified from price_min/max based on standard ecommerce
    image_path: Any = db.Column(db.String(500), nullable=True)
    is_active: Any = db.Column(db.Boolean, default=True)
    stock: Any = db.Column(db.Integer, default=100)
    rating: Any = db.Column(db.Float, default=0.0) # Added as per requirement
    created_at: Any = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    cart_items: Any = db.relationship('CartItem', backref='product', lazy=True)
    order_items: Any = db.relationship('OrderItem', backref='product', lazy=True)
    wishlisted_by: Any = db.relationship('Wishlist', backref='product', lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id: Any = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    added_at: Any = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id: Any = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity: Any = db.Column(db.Integer, default=1)
    added_at: Any = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

class Order(db.Model):
    __tablename__ = 'orders'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    user_id: Any = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount: Any = db.Column(db.Float, nullable=False)
    status: Any = db.Column(db.String(50), default='pending')
    created_at: Any = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    items: Any = db.relationship('OrderItem', backref='order', lazy=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    order_id: Any = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id: Any = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity: Any = db.Column(db.Integer, nullable=False)
    price: Any = db.Column(db.Float, nullable=False)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

class Suggestion(db.Model):
    __tablename__ = 'suggestions'
    __allow_unmapped__ = True
    id: Any = db.Column(db.Integer, primary_key=True)
    name: Any = db.Column(db.String(120), nullable=False)
    message: Any = db.Column(db.Text, nullable=False)
    created_at: Any = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
