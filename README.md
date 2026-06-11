# 🧵 Pure Weaves — Handcrafted Saree Kuchu & Bunches

> **A full-stack e-commerce web application** for a handcrafted saree accessories business based in Shivamogga, Karnataka.

---

## 🏪 Shop Information

| Detail | Info |
|---|---|
| **Shop Name** | Pure Weaves |
| **Owners** | Latha & Gangadhar |
| **Location** | Shivamogga, Karnataka |
| **WhatsApp** | +91 8088744654 |
| **Email** | pureweaves@gmail.com |
| **Instagram** | @pureweaves_sareesbunches |
| **Facebook** | facebook.com/pureweaves |

---

## 📁 Project Structure

```
Handcrafted-with-Love-Pure-Weaves/
│
├── app.py                    ← Standalone Flask backend (JWT-based API)
├── run.py                    ← App entry point (uses app/ package)
├── config.py                 ← Configuration class (DB, secret keys)
├── invoice_generator.py      ← PDF & Word invoice generator (fpdf2 + OpenXML)
├── requirements.txt          ← Python dependencies
├── pyproject.toml            ← Project metadata (for uv / Vercel deployment)
├── vercel.json               ← Vercel deployment configuration
├── netlify.toml              ← Netlify deployment & security headers
├── database.sql              ← MySQL database schema (legacy)
├── seed.py                   ← Database seeder script
│
├── app/                      ← Flask application package
│   ├── __init__.py           ← App factory (create_app), extensions setup
│   ├── models.py             ← SQLAlchemy database models
│   └── routes/
│       ├── auth.py           ← Login, Register, Logout, Forgot Password
│       ├── main.py           ← Catalog, Cart, Wishlist, Profile, Checkout
│       └── admin.py          ← Admin dashboard, Products, Users, Orders
│
├── app/templates/            ← Jinja2 HTML templates
│   ├── base.html             ← Base layout (navbar, flash messages)
│   ├── index.html            ← Home / Landing page
│   ├── login.html            ← Login page (email + username support)
│   ├── register.html         ← Registration (Gmail-only enforced)
│   ├── catalog.html          ← Product catalog with filters & sort
│   ├── cart.html             ← Shopping cart
│   ├── wishlist.html         ← Saved wishlist items
│   ├── profile.html          ← User profile & order history
│   ├── forgot_password.html  ← Password reset
│   └── admin/
│       ├── base.html         ← Admin layout
│       ├── dashboard.html    ← Stats overview
│       ├── products.html     ← Add/delete products
│       ├── users.html        ← User management
│       ├── orders.html       ← Order management
│       └── suggestions.html  ← Customer suggestions
│
├── app/static/               ← CSS, JS, images
├── index.html                ← Standalone frontend (no server needed)
├── admin.html                ← Standalone admin panel (no server needed)
├── login.html                ← Standalone login page
│
├── migrations/               ← Alembic DB migration files
├── instance/                 ← SQLite database (auto-created locally)
└── .venv/                    ← Python virtual environment
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites

- Python 3.12+
- pip or uv

### 2. Create Virtual Environment & Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install all packages
pip install -r requirements.txt
```

### 3. Run the App

```bash
python run.py
```

Open your browser at **http://localhost:5000**

> 💡 **No database setup needed!** SQLite is used automatically for local development. The `instance/app.db` file is created on first run.

---

## 📦 Python Dependencies

| Package | Version | Purpose |
|---|---|---|
| `flask` | 3.0.0 | Web framework |
| `flask-sqlalchemy` | 3.1.1 | ORM / database integration |
| `flask-bcrypt` | 1.0.1 | Secure password hashing |
| `flask-cors` | 4.0.0 | Cross-origin resource sharing |
| `flask-login` | 0.6.3 | User session management |
| `flask-migrate` | 4.1.0 | Database migrations (Alembic) |
| `pymysql` | 1.1.0 | MySQL connector |
| `pyjwt` | 2.8.0 | JSON Web Token auth |
| `python-dotenv` | 1.0.0 | Load `.env` secret keys |
| `email-validator` | 2.3.0 | Validate email addresses |
| `fpdf2` | 2.8.7 | PDF invoice generation |
| `openpyxl` | 3.1.5 | Excel report export |
| `sqlalchemy` | 2.0.50 | Database ORM core |
| `alembic` | 1.18.4 | Database migration engine |

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Models

| Model | Table | Description |
|---|---|---|
| `User` | `users` | Customer accounts (username, email, password, is_admin) |
| `Category` | `categories` | Product categories |
| `Product` | `products` | Kuchu designs (name, price, stock, image) |
| `Wishlist` | `wishlist` | Saved products per user |
| `CartItem` | `cart_items` | Shopping cart items |
| `Order` | `orders` | Customer orders |
| `OrderItem` | `order_items` | Line items within an order |
| `Suggestion` | `suggestions` | Customer feedback / suggestions |

> **app.py** (standalone mode) has additional models: `Coupon`, `Customer`, `Review`, `Bill`, `BillItem` for the full billing system.

---

## 🔗 API Routes

### Authentication (`/`)
| Method | Route | Description |
|---|---|---|
| `GET/POST` | `/login` | Login with email or username |
| `GET/POST` | `/register` | Register (Gmail addresses only) |
| `GET` | `/logout` | Logout current user |
| `GET/POST` | `/forgot-password` | Password reset flow |

### Main (`/`)
| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Home page (featured products) |
| `GET` | `/catalog` | Product catalog (filter by category, search, sort) |
| `GET` | `/wishlist` | User's saved wishlist |
| `POST` | `/api/wishlist/toggle` | Add / remove product from wishlist |
| `GET` | `/cart` | Shopping cart |
| `POST` | `/api/cart/add` | Add product to cart |
| `POST` | `/api/cart/update` | Update cart item quantity |
| `POST` | `/checkout` | Place order from cart |
| `GET/POST` | `/profile` | View/update user profile |
| `POST` | `/suggestion` | Submit customer suggestion |

### Admin (`/admin/`)
| Method | Route | Description |
|---|---|---|
| `GET` | `/admin/` | Admin dashboard (stats) |
| `GET/POST` | `/admin/products` | List & add products |
| `POST` | `/admin/products/delete/<id>` | Delete a product |
| `GET` | `/admin/users` | List all users |
| `GET` | `/admin/orders` | View all orders |
| `POST` | `/admin/orders/update/<id>` | Update order status |
| `GET` | `/admin/suggestions` | View customer suggestions |
| `POST` | `/admin/suggestions/delete/<id>` | Delete a suggestion |

### Standalone API (`app.py` — `/api/...`)
| Method | Route | Description |
|---|---|---|
| `POST` | `/api/auth/google` | Google OAuth login |
| `POST` | `/api/auth/register` | Register with email/password |
| `POST` | `/api/auth/login` | Login with email/password |
| `GET` | `/api/products` | Get all active products |
| `GET` | `/api/cart` | Get user cart |
| `POST` | `/api/cart/add` | Add to cart |
| `DELETE` | `/api/cart/remove/<id>` | Remove cart item |
| `POST` | `/api/coupon/validate` | Validate coupon code |
| `POST` | `/api/order/place` | Place order |
| `GET` | `/api/admin/stats` | Dashboard statistics |
| `GET` | `/api/admin/orders` | All orders |
| `GET` | `/api/admin/users` | All users |
| `POST` | `/api/admin/product/add` | Add product |
| `POST` | `/api/admin/product/edit/<id>` | Edit product |
| `DELETE` | `/api/admin/product/delete/<id>` | Delete product |
| `GET` | `/api/admin/coupons` | List coupons |
| `POST` | `/api/admin/coupon/create` | Create coupon |
| `GET/POST` | `/api/admin/customers` | Customer management |
| `GET/POST` | `/api/admin/bills` | Billing / invoicing |
| `GET` | `/api/admin/bills/pdf/<id>` | Download PDF invoice |
| `GET` | `/api/admin/bills/docx/<id>` | Download Word invoice |
| `GET` | `/api/admin/reports` | Revenue analytics |
| `GET` | `/api/admin/reports/export/<format>` | Export CSV / Excel |
| `GET` | `/api/reviews` | Get product reviews |
| `POST` | `/api/reviews` | Submit a review |
| `GET` | `/api/admin/suggestions` | View all suggestions |

---

## 🧾 Invoice Generator

The `invoice_generator.py` module creates professional branded invoices:

- **PDF** (`generate_pdf_invoice`) — via `fpdf2`
  - Maroon branded header with company info
  - Customer details & invoice metadata
  - Itemized product table with alternating row colors
  - Financial summary (subtotal, GST 5%, discount, grand total)
  - Branded footer with social links

- **Word / DOCX** (`generate_docx_invoice`) — via raw OpenXML/ZIP
  - No `lxml` or `python-docx` dependency
  - Fully compatible with Microsoft Word & LibreOffice
  - Styled with brand colors and table formatting

---

## 🔒 Security Features

| Feature | Details |
|---|---|
| **Password Hashing** | Bcrypt with salt — passwords never stored in plaintext |
| **JWT Authentication** | Tokens expire after 24 hours |
| **Gmail-Only Registration** | Email validator enforces `@gmail.com` |
| **Rate Limiting** | Max 5 login/register attempts per 60 seconds |
| **Account Lockout** | Locked after 5 consecutive failed login attempts |
| **CORS Policy** | Only `/api/*` routes accept cross-origin requests |
| **Security Headers** | X-Frame-Options, X-XSS-Protection, X-Content-Type-Options, CSP |
| **SQL Injection Protection** | SQLAlchemy ORM — no raw SQL queries |
| **Admin Protection** | Separate `is_admin` flag + admin secret header |
| **Session Management** | Flask-Login handles secure sessions |
| **Stock Validation** | Orders rejected if insufficient stock |

---

## ☁️ Deployment

### Vercel (Recommended — Free)

The project is pre-configured for Vercel:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

The `vercel.json` routes all traffic to `run.py` using `@vercel/python`.

> ⚠️ **Important:** Vercel uses an ephemeral filesystem — SQLite data resets on each deployment. Set `DATABASE_URL` in Vercel Environment Variables to use a persistent database.

**Recommended Free Databases:**
- [Neon](https://neon.tech) — PostgreSQL (`postgresql://...`)
- [PlanetScale](https://planetscale.com) — MySQL (`mysql+pymysql://...`)
- [Supabase](https://supabase.com) — PostgreSQL

Set in Vercel dashboard → Settings → Environment Variables:
```
DATABASE_URL=postgresql://user:pass@host/dbname
SECRET_KEY=your-secure-random-key
ADMIN_PANEL_SECRET=your-admin-secret
```

### Render (Free — Python)

1. Go to [render.com](https://render.com) → New Web Service
2. Connect GitHub repository
3. Set **Build Command:** `pip install -r requirements.txt`
4. Set **Start Command:** `python run.py`
5. Add environment variables

### Netlify (Frontend Only)

The standalone `index.html` / `admin.html` can be deployed to Netlify directly (no server needed). The `netlify.toml` is pre-configured with security headers and API proxy redirects.

---

## 🗄️ Database Setup (MySQL — Production)

To use MySQL instead of SQLite:

1. Create a MySQL database:
```sql
CREATE DATABASE pureweaves_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Set `DATABASE_URL` in your environment:
```
DATABASE_URL=mysql+pymysql://root:password@localhost/pureweaves_db
```

3. Run migrations:
```bash
flask db upgrade
```

Or use the schema file:
```bash
mysql -u root -p pureweaves_db < database.sql
```

---

## 🧪 Testing

### Run the development server
```bash
python run.py
```

### Manual Test Checklist

- [ ] `GET /login` → Login page loads (200)
- [ ] `POST /login` JSON → Returns `{"message": "Logged in successfully"}` on success
- [ ] `POST /login` JSON wrong password → Returns `{"error": "..."}` (401)
- [ ] `GET /register` → Register page loads (200)
- [ ] `POST /register` non-Gmail → Returns `{"error": "Only Gmail addresses are allowed"}` (400)
- [ ] `GET /catalog` → Products listed (200) — works logged in AND out
- [ ] `POST /api/wishlist/toggle` → Adds/removes from wishlist (200)
- [ ] `GET /catalog` with wishlist items → No crash (200) ✅ *Bug fixed*
- [ ] `GET /wishlist` → Shows saved products (200)
- [ ] `GET /cart` → Requires login (302 → /login)
- [ ] `GET /admin/` → Requires admin login (302)
- [ ] `GET /admin/products` → Admin products page (200 when admin logged in)
- [ ] `GET /api/admin/bills/pdf/<id>` → Downloads PDF invoice
- [ ] `GET /api/admin/reports/export/csv` → Downloads CSV report
- [ ] `GET /api/admin/reports/export/excel` → Downloads XLSX report

---

## 💻 Technologies Used

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| **Backend** | Python 3.12+, Flask 3.0 |
| **ORM** | SQLAlchemy 2.0 + Flask-SQLAlchemy |
| **Auth** | Flask-Login (sessions) + PyJWT (API tokens) + Google OAuth |
| **Database** | SQLite (local dev) / MySQL or PostgreSQL (production) |
| **Migrations** | Flask-Migrate (Alembic) |
| **PDF Generation** | fpdf2 |
| **Word Generation** | Raw OpenXML/ZIP (no lxml dependency) |
| **Excel Export** | openpyxl |
| **Password Security** | Flask-Bcrypt |
| **Email Validation** | email-validator |
| **Deployment** | Vercel (`vercel.json`) / Netlify (`netlify.toml`) / Render |
| **Version Control** | Git + GitHub |
| **IDE** | VS Code |

---

## 📚 Python Concepts Used (BCA Reference)

```python
# Decorators
@app.route('/catalog')
@login_required
def catalog(): ...

# ORM Queries
products = Product.query.filter_by(is_active=True).all()
wishlist  = Wishlist.query.filter_by(user_id=current_user.id).all()

# Blueprints (modular routing)
auth_bp  = Blueprint('auth', __name__)
main_bp  = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__)

# App Factory Pattern
def create_app(config_class=Config):
    app = Flask(__name__)
    db.init_app(app)
    app.register_blueprint(auth_bp)
    return app

# Context managers
with app.app_context():
    db.create_all()

---

## 🔧 Recent Fixes (2026-06-11)

Summary of changes made to resolve a 500/404 login issue and improve deployment:

- Cleaned and replaced the root `login.html` (removed duplicate/invalid markup, added accessibility attributes, ensured input `name` attributes and proper form `action`).
- Split inline styles and scripts into `/assets/login.css` and `/assets/login.js` for better caching, maintainability and to avoid duplicated code.
- Hardened frontend JS: added `safeFetch` with timeout, null-safety checks, improved Firebase init handling and fallbacks, and robust redirect logic.
- Added a `csrf_token` hidden input placeholder in the login form — populate this server-side when enabling CSRF protection.
- Added a `/login.html` alias in the Flask auth blueprint so static requests to `/login.html` do not 404 when templates are rendered from Flask.
- Updated `vercel.json` to support static builds and optional Python API routes; added environment variable placeholders and security headers.
- Fixed broken nesting and duplicate DOCTYPE/head/body issues that caused parsing errors in some environments.

### How to verify locally

1. Start the app locally:

```bash
python run.py
```

2. Visit the login page:

```
http://127.0.0.1:5000/login.html
```

3. Test flows:
- Google sign-in (requires proper Firebase config in `/env-config.js` or Vercel env vars)
- Email/password login: POST `/api/auth/login` (JSON) or use the form

4. Check console and server logs for any errors; local server prints traceback on exceptions.

### Vercel deployment notes

- Set the following Environment Variables in the Vercel project settings (do NOT commit them to the repo):
  - `DATABASE_URL` (use Postgres/MySQL for production)
  - `SECRET_KEY`
  - `FIREBASE_API_KEY`, `FIREBASE_AUTH_DOMAIN`, etc. (if using Firebase)
  - `ADMIN_PANEL_SECRET` (optional)

- Vercel's filesystem is ephemeral: do not rely on SQLite for production. Use a managed DB and set `DATABASE_URL`.

---

If you want, I can now:
- add the same asset separation and fixes to `register.html` and `index.html`,
- create a git branch and open a PR with these changes, or
- deploy to a Vercel preview (you'll need to add env vars in your Vercel dashboard).


# f-strings
invoice_number = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}"

# Exception handling
try:
    valid = validate_email(email)
except EmailNotValidError as e:
    return jsonify({"error": str(e)}), 400

# JWT
token = jwt.encode({'user_id': user.id, 'exp': expires}, SECRET_KEY, algorithm='HS256')
data  = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

# Password hashing
hash_ = bcrypt.generate_password_hash(password).decode('utf-8')
ok    = bcrypt.check_password_hash(hash_, password)
```

---

## 🎨 Frontend Features

- **Responsive Design** — Mobile-first, works on all screen sizes
- **Google Fonts** — Premium typography
- **Dark/Light Mode** — CSS custom properties
- **Product Catalog** — Filter by category, search by name/description, sort by price
- **Wishlist** — Heart toggle with visual feedback
- **Shopping Cart** — Quantity update, remove items, subtotal calculation
- **Coupon System** — Real-time validation and discount application
- **WhatsApp Order** — Pre-filled order message sent directly to shop owner
- **Review System** — Star ratings and text reviews
- **Admin Dashboard** — Full CRUD for products, customers, coupons, billing
- **Invoice Generation** — Download PDF or Word invoices from admin panel
- **Revenue Reports** — Daily / Weekly / Monthly / Yearly analytics with chart data
- **CSV & Excel Export** — Download billing reports

---

## 🔧 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-very-secure-random-secret-key
DATABASE_URL=sqlite:///app.db
ADMIN_PANEL_SECRET=your-admin-panel-secret
```

For production on Vercel/Render, set these in the platform's Environment Variables dashboard.

---

## 📤 Deploy to GitHub

```bash
git init
git add .
git commit -m "Pure Weaves - full stack e-commerce app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pure-weaves.git
git push -u origin main
```

---

*Built with ❤️ for Pure Weaves, Shivamogga — Good luck, Sanju! 🎓*  
*This project is perfect for your BCA portfolio.*
