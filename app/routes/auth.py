from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user  # type: ignore[missing-import]
from app.models import User
from app import db, bcrypt
from email_validator import validate_email, EmailNotValidError  # type: ignore[missing-import]

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login() -> None:
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Assume it can be a JSON request or form request
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email')
        username = data.get('username') # The prompt asked for Gmail/Username
        password = data.get('password')
        
        # Support either username or email
        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        elif username:
            user = User.query.filter_by(username=username).first()
        elif data.get('login'): # Generic field for either
            login_val = data.get('login')
            user = User.query.filter((User.email == login_val) | (User.username == login_val)).first()
            
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            if request.is_json:
                return jsonify({"message": "Logged in successfully", "redirect": url_for('main.index')}), 200  # type: ignore[BSK-E0013]
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            if request.is_json:
                return jsonify({"error": "Invalid email/username or password"}), 401  # type: ignore[BSK-E0013]
            flash('Invalid login credentials', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register() -> None:
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not username or not email or not password or not confirm_password:
            if request.is_json:
                return jsonify({"error": "All fields are required"}), 400  # type: ignore[BSK-E0013]
            flash("All fields are required", "danger")
            return render_template('register.html')
            
        if password != confirm_password:
            if request.is_json:
                return jsonify({"error": "Passwords do not match"}), 400  # type: ignore[BSK-E0013]
            flash("Passwords do not match", "danger")
            return render_template('register.html')
            
        try:
            valid = validate_email(email)
            email = valid.email
            if not email.endswith('@gmail.com'):
                if request.is_json:
                    return jsonify({"error": "Only Gmail addresses are allowed"}), 400  # type: ignore[BSK-E0013]
                flash("Only Gmail addresses are allowed", "danger")
                return render_template('register.html')
        except EmailNotValidError as e:
            if request.is_json:
                return jsonify({"error": str(e)}), 400  # type: ignore[BSK-E0013]
            flash(str(e), "danger")
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({"error": "Email is already registered"}), 400  # type: ignore[BSK-E0013]
            flash("Email already registered", "danger")
            return render_template('register.html')
            
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({"error": "Username is already taken"}), 400  # type: ignore[BSK-E0013]
            flash("Username already taken", "danger")
            return render_template('register.html')
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        if request.is_json:
            return jsonify({"message": "Registration successful", "redirect": url_for('main.index')}), 201  # type: ignore[BSK-E0013]
        flash('Registration successful!', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout() -> None:
    logout_user()
    if request.is_json:
        return jsonify({"message": "Logged out"}), 200  # type: ignore[BSK-E0013]
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password() -> None:
    # To be fully implemented with an email sending service
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        
        user = User.query.filter_by(email=email).first()
        if user:
            # Here we would generate a token and send an email
            msg = "If an account with that email exists, a reset link has been sent."
            if request.is_json:
                return jsonify({"message": msg}), 200  # type: ignore[BSK-E0013]
            flash(msg, 'info')
        else:
            if request.is_json:
                return jsonify({"error": "Email not found"}), 404  # type: ignore[BSK-E0013]
            flash('Email not found.', 'danger')
            
    return render_template('forgot_password.html')
