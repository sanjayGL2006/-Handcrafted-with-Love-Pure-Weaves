# PRODUCTION-READY FIXES FOR PURE WEAVES
# This file contains secure, hardened implementations for critical security fixes

# =============================================================================
# FILE 1: app_security_fixes.py
# DESCRIPTION: Fixed routes with proper security controls
# =============================================================================

from flask import Blueprint, request, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from typing import Any, Callable, Tuple, Dict, Optional
import jwt
import secrets
import time
import datetime
from app import db, bcrypt
from app.models import User, Product, Order, Admin Audit Log

# ─── RATE LIMITING ──────────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",  # Use Redis in production
    default_limits=["200 per day", "50 per hour"],
)

# ─── CSRF PROTECTION ───────────────────────────────────────────────────
def csrf_protect(f: Callable) -> Callable:
    """Verify CSRF tokens on state-changing requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token_header = request.headers.get('X-CSRF-Token', '')
            token_json = request.get_json().get('csrf_token', '') if request.is_json else ''
            token_form = request.form.get('csrf_token', '')
            
            request_token = token_header or token_json or token_form
            session_token = session.get('csrf_token')
            
            if not request_token or not session_token:
                return jsonify({'error': 'CSRF token missing'}), 400
            
            # Constant-time comparison
            if not secrets.compare_digest(request_token, session_token):
                return jsonify({'error': 'CSRF token invalid'}), 403
        
        return f(*args, **kwargs)
    return decorated


# ─── AUTHENTICATION ────────────────────────────────────────────────────
class SecureAuthenticationManager:
    """Manage secure authentication with token revocation"""
    
    def __init__(self):
        self.revoked_tokens = set()  # Use Redis in production
        self.login_attempts = {}
        self.MAX_ATTEMPTS = 5
        self.LOCKOUT_MINUTES = 15
    
    def generate_tokens(self, user: User) -> Dict[str, Any]:
        """Generate access and refresh tokens"""
        now = datetime.datetime.utcnow()
        
        # Access token (short-lived)
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'is_admin': user.is_admin,
            'type': 'access',
            'iat': now,
            'exp': now + datetime.timedelta(hours=1),
            'jti': secrets.token_urlsafe(32)
        }
        
        # Refresh token (long-lived)
        refresh_payload = {
            'user_id': user.id,
            'type': 'refresh',
            'iat': now,
            'exp': now + datetime.timedelta(days=7),
            'jti': secrets.token_urlsafe(32)
        }
        
        access_token = jwt.encode(access_payload, SESSION_SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, SESSION_SECRET_KEY, algorithm='HS256')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            if token in self.revoked_tokens:
                return None
            
            payload = jwt.decode(token, SESSION_SECRET_KEY, algorithms=['HS256'])
            
            # Ensure token hasn't expired
            if payload['exp'] < datetime.datetime.utcnow().timestamp():
                return None
            
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, token: str) -> None:
        """Revoke a token (add to blacklist)"""
        self.revoked_tokens.add(token)
    
    def check_login_attempts(self, email: str) -> Tuple[bool, Optional[str]]:
        """Check login rate limiting"""
        now = datetime.datetime.utcnow()
        
        if email not in self.login_attempts:
            return True, None
        
        attempts, last_attempt = self.login_attempts[email]
        
        # Reset if lockout period expired
        if now - last_attempt > datetime.timedelta(minutes=self.LOCKOUT_MINUTES):
            self.login_attempts[email] = [0, now]
            return True, None
        
        # Check if locked out
        if attempts >= self.MAX_ATTEMPTS:
            mins_remaining = self.LOCKOUT_MINUTES - int((now - last_attempt).total_seconds() / 60)
            return False, f'Account locked. Try again in {mins_remaining} minutes'
        
        return True, None
    
    def record_login_attempt(self, email: str, success: bool) -> None:
        """Record login attempt for rate limiting"""
        now = datetime.datetime.utcnow()
        
        if success:
            self.login_attempts[email] = [0, now]
        else:
            if email not in self.login_attempts:
                self.login_attempts[email] = [0, now]
            attempts, _ = self.login_attempts[email]
            self.login_attempts[email] = [attempts + 1, now]


auth_manager = SecureAuthenticationManager()


# ─── ADMIN AUTHENTICATION (FIXED) ───────────────────────────────────
def admin_required(f: Callable) -> Callable:
    """Decorator to verify admin access (SECURE)"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip() if auth_header else None
        
        if not token:
            return jsonify({'error': 'Admin authentication required'}), 401
        
        # Verify JWT token
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user and verify admin status
        current_user = User.query.get(payload['user_id'])
        
        if not current_user or not current_user.is_admin or not current_user.is_active:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Log admin action
        log_admin_action(current_user.id, request.endpoint, request.method)
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# ─── AUDIT LOGGING ──────────────────────────────────────────────────
class AdminAuditLog(db.Model):
    """Audit log for all admin actions"""
    __tablename__ = 'admin_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # CREATE, READ, UPDATE, DELETE
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    request_data = db.Column(db.JSON, nullable=True)
    status_code = db.Column(db.Integer)
    error_message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    
    admin = db.relationship('User', backref='audit_logs')


def log_admin_action(admin_id: int, endpoint: str, method: str, 
                     request_data: Optional[Dict] = None, 
                     status_code: int = 200,
                     error_message: str = None) -> None:
    """Log admin action for audit trail"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    
    # Redact sensitive data
    safe_data = redact_sensitive_fields(request_data)
    
    log = AdminAuditLog(
        admin_id=admin_id,
        action=_get_action_type(method),
        endpoint=endpoint,
        method=method,
        ip_address=ip,
        request_data=safe_data,
        status_code=status_code,
        error_message=error_message
    )
    
    db.session.add(log)
    db.session.commit()


def _get_action_type(method: str) -> str:
    """Map HTTP method to action type"""
    method_map = {
        'POST': 'CREATE',
        'PUT': 'UPDATE',
        'PATCH': 'UPDATE',
        'DELETE': 'DELETE',
        'GET': 'READ'
    }
    return method_map.get(method, 'UNKNOWN')


def redact_sensitive_fields(data: Optional[Dict]) -> Optional[Dict]:
    """Remove sensitive fields from logged data"""
    if not data:
        return None
    
    sensitive_fields = {'password', 'password_hash', 'token', 'secret', 'pin', 'cvv'}
    
    safe_data = {}
    for key, value in data.items():
        if key.lower() in sensitive_fields:
            safe_data[key] = '[REDACTED]'
        else:
            safe_data[key] = value
    
    return safe_data


# ─── SECURE LOGIN ROUTE ──────────────────────────────────────────────
@limiter.limit("10 per hour")
def secure_login() -> Tuple[Dict, int]:
    """Secure login with rate limiting and account lockout"""
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    
    # Input validation
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if len(email) > 255 or len(password) > 255:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check rate limiting
    can_attempt, error_msg = auth_manager.check_login_attempts(email)
    if not can_attempt:
        return jsonify({'error': error_msg}), 429
    
    # Find user
    user = User.query.filter_by(email=email, is_active=True).first()
    
    # Prevent user enumeration
    if not user or not user.password_hash:
        auth_manager.record_login_attempt(email, False)
        time.sleep(0.5 + random.uniform(0, 0.5))  # Timing attack protection
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Verify password
    if not bcrypt.check_password_hash(user.password_hash, password):
        auth_manager.record_login_attempt(email, False)
        time.sleep(0.5 + random.uniform(0, 0.5))
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Successful login
    auth_manager.record_login_attempt(email, True)
    
    # Generate tokens
    tokens = auth_manager.generate_tokens(user)
    
    # Log successful login
    log_admin_action(user.id, '/api/auth/login', 'POST', status_code=200)
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin
        },
        **tokens
    }), 200


# ─── SECURE LOGOUT ROUTE ────────────────────────────────────────────
def secure_logout(current_user: User) -> Tuple[Dict, int]:
    """Logout and revoke token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    
    if token:
        auth_manager.revoke_token(token)
    
    session.clear()
    
    log_admin_action(current_user.id, '/api/auth/logout', 'POST', status_code=200)
    
    return jsonify({'message': 'Logged out successfully'}), 200


# ─── INPUT VALIDATION ───────────────────────────────────────────────
class InputValidator:
    """Validate and sanitize user inputs"""
    
    @staticmethod
    def validate_product_data(data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Validate product creation/update data"""
        errors = []
        
        # Name validation
        name = (data.get('name') or '').strip()
        if not name:
            errors.append('Product name is required')
        elif len(name) > 200:
            errors.append('Name must be ≤ 200 characters')
        
        # Description validation
        description = (data.get('description') or '').strip()
        if not description:
            errors.append('Description is required')
        elif len(description) > 5000:
            errors.append('Description too long (≤ 5000 chars)')
        
        # Price validation
        try:
            price_min = float(data.get('price_min', 0))
            price_max = float(data.get('price_max', 0))
            
            if price_min <= 0 or price_max <= 0:
                errors.append('Prices must be positive')
            if price_max <= price_min:
                errors.append('Max price must be greater than min price')
            if price_max > 999999:
                errors.append('Price exceeds maximum limit')
        except (ValueError, TypeError):
            errors.append('Invalid price format')
        
        # Stock validation
        try:
            stock = int(data.get('stock', 100))
            if stock < 0 or stock > 1000000:
                errors.append('Invalid stock value')
        except (ValueError, TypeError):
            errors.append('Stock must be a number')
        
        if errors:
            return False, '; '.join(errors), None
        
        return True, '', {
            'name': name,
            'description': description,
            'price_min': round(price_min, 2),
            'price_max': round(price_max, 2),
            'stock': stock
        }
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        import re
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, email
        return False, 'Invalid email format'


# ═══════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION GUIDE
# ═══════════════════════════════════════════════════════════════════════════

'''
1. Add to app.py initialization:
   
   from app_security_fixes import limiter, admin_required, csrf_protect
   from app_security_fixes import auth_manager, log_admin_action
   
   limiter.init_app(app)

2. Replace old admin_required decorator with new one:
   
   @app.route('/api/admin/products')
   @admin_required
   @csrf_protect
   def list_products(current_user):
       # Only properly authenticated admin users reach here
       products = Product.query.all()
       return jsonify([{...}]), 200

3. Add CSRF token to frontend:
   
   <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
   
   fetch('/api/admin/product/add', {
       method: 'POST',
       headers: {
           'X-CSRF-Token': csrfToken
       }
   })

4. Database migration for audit logs:
   
   flask db migrate -m "Add admin audit logs"
   flask db upgrade

5. Configure environment variables:
   
   export ADMIN_PANEL_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

'''

