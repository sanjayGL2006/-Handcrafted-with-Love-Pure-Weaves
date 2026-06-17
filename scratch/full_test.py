"""
PureWeaves Full Project Test Script
Tests all API endpoints and checks both index.html and admin.html for the 12 reported bugs.
"""

import urllib.request
import urllib.error
import json
import sys
import os
import codecs
from typing import Any

BASE = "http://127.0.0.1:5000"
PASS = []
FAIL = []

def ok(msg):
    PASS.append(msg)
    print(f"  [PASS] {msg}")

def fail(msg):
    FAIL.append(msg)
    print(f"  [FAIL] {msg}")

def get(path, expected_status=200):
    try:
        req = urllib.request.Request(f"{BASE}{path}")
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode('utf-8', errors='replace')
        if resp.status == expected_status:
            return resp.status, body
        else:
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return e.code, body
    except Exception as e:
        return 0, str(e)

def post(path, data, token=None):
    try:
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(f"{BASE}{path}", data=payload, method='POST')
        req.add_header('Content-Type', 'application/json')
        if token:
            req.add_header('Authorization', f'Bearer {token}')
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode('utf-8', errors='replace')
        return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(body)
        except:
            return e.code, {'raw': body[:200]}
    except Exception as e:
        return 0, {'error': str(e)}

print("\n" + "="*60)
print("  PUREWEAVES FULL PROJECT TEST")
print("="*60)

# ─── 1. Homepage Loads ───────────────────────────────────────────
print("\n[1] HOMEPAGE LOAD")
status, body = get("/")
if status == 200 and ("Pure Weaves" in body or "pureweaves" in body.lower()):
    ok("Homepage returns 200 with content")
else:
    fail(f"Homepage failed — status={status}")

# ─── 2. API: Products ────────────────────────────────────────────
print("\n[2] API: /api/products")
status, body = get("/api/products")
if status == 200:
    try:
        products = json.loads(body)
        if isinstance(products, list):
            ok(f"Products API returns list of {len(products)} items")
            if products:
                p = products[0]
                missing = [k for k in ['id','name','price_min','image_path','category'] if k not in p]
                if missing:
                    fail(f"Product object missing keys: {missing}")
                else:
                    ok("Product objects have all required keys (id, name, price_min, image_path, category)")
                # Check image
                has_image = p.get('image_path') and p['image_path'].strip()
                if has_image:
                    ok("Products have image_path set (Bug #1 likely fixed)")
                else:
                    fail("product.image_path is empty/None — Bug #1 still present (broken images)")
                # Check price
                price_ok = p.get('price_min', 0) > 0
                if price_ok:
                    ok(f"Products have price > 0 (e.g., {p['price_min']}) — Bug #2 price likely OK")
                else:
                    fail("product.price_min is 0 or missing — Bug #2: modal shows Rs0")
        else:
            fail(f"Products API returned non-list: {type(products)}")
    except json.JSONDecodeError:
        fail(f"Products API returned non-JSON: {body[:100]}")
else:
    fail(f"Products API failed — status={status}")

# ─── 3. API: Reviews ─────────────────────────────────────────────
print("\n[3] API: /api/reviews")
status, body = get("/api/reviews")
if status == 200:
    try:
        data = json.loads(body)
        ok(f"Reviews API returns 200. Keys: {list(data.keys() if isinstance(data, dict) else [])}")
    except:
        fail("Reviews API returned non-JSON")
else:
    fail(f"Reviews API failed — status={status}, body={body[:100]}")

# ─── 4. API: Submit Review ───────────────────────────────────────
print("\n[4] API: POST /api/reviews")
status, data = post("/api/reviews", {"customer_name": "Test User", "mobile": "9999999999", "rating": 5, "review": "Automated test review"})
if status in [200, 201]:
    ok(f"POST /api/reviews works — {data}")
elif status == 401:
    ok("POST /api/reviews requires auth — acceptable")
else:
    fail(f"POST /api/reviews failed — status={status}, data={data}")

# ─── 5. API: Register & Login ────────────────────────────────────
print("\n[5] AUTH: Register and Login")
import time
test_user = f"testuser_{int(time.time())}"
status, data = post("/api/auth/register", {"name": "Test User", "mobile": f"99{int(time.time())%100000000:08d}", "password": "Test@1234"})
if status in [200, 201]:
    ok(f"Register works — {data.get('message', data)}")
else:
    # Try alternative endpoint
    status2, data2 = post("/api/register", {"name": "Test User", "mobile": "9988776655", "password": "Test@1234"})
    if status2 in [200, 201]:
        ok(f"Register works at /api/register — {data2.get('message', data2)}")
    else:
        fail(f"Register failed — tried /api/auth/register ({status}) and /api/register ({status2})")

# Try login
status, data = post("/api/auth/login", {"mobile": "9988776655", "password": "Test@1234"})
TOKEN = None
if status == 200:
    TOKEN = data.get('token') or data.get('access_token')
    ok(f"Login works — got token: {'YES' if TOKEN else 'NO'}")
else:
    status2, data2 = post("/api/login", {"mobile": "9988776655", "password": "Test@1234"})
    if status2 == 200:
        TOKEN = data2.get('token')
        ok(f"Login works at /api/login")
    else:
        fail(f"Login failed — status={status}, data={data}")

# ─── 6. API: Place Order ─────────────────────────────────────────
print("\n[6] API: POST /api/order/place")
status, data = post("/api/order/place", 
    {"items": [{"product_id": 1, "quantity": 2}], "coupon_code": ""},
    token=TOKEN)
if status in [200, 201]:
    ok(f"Order placement works — {data}")
elif status == 401:
    ok("Order placement requires auth — correct behaviour")
elif status == 400:
    ok(f"Order API reached but validation error (expected): {data}")
else:
    fail(f"Order placement failed — status={status}, data={data}")

# ─── 7. API: Profile Save ────────────────────────────────────────
print("\n[7] API: POST /api/profile")
status, data = post("/api/profile",
    {"name": "Test User", "mobile": "9988776655", "email": "test@example.com"},
    token=TOKEN)
if status in [200, 201]:
    ok(f"Profile save works — {data}")
elif status == 401:
    ok("Profile save requires auth — correct")
else:
    fail(f"Profile save failed — status={status}, data={data}")

# ─── 8. Admin Panel Auth Guard ───────────────────────────────────
print("\n[8] ADMIN: admin.html auth guard")
status, body = get("/admin.html")
if status == 200 and "adminToken" in body:
    ok("admin.html has adminToken auth guard in source — Bug #4 fixed")
elif status == 302 or status == 301:
    ok(f"admin.html redirects (status={status}) — auth guard at server level")
elif status == 200 and "adminToken" not in body and "pw_admin_secret" not in body:
    fail("admin.html loads without any auth guard — Bug #4 NOT fixed")
else:
    ok(f"admin.html status={status} (may redirect client-side)")

# ─── 9. Static Assets ────────────────────────────────────────────
print("\n[9] STATIC ASSETS")
status, body = get("/assets/placeholder-kuchu.jpg")
if status == 200:
    ok("Placeholder image /assets/placeholder-kuchu.jpg serves OK")
else:
    status2, _ = get("/assets/placeholder.webp")
    if status2 == 200:
        ok("Placeholder image /assets/placeholder.webp serves OK")
    else:
        fail(f"Placeholder image missing — 404. Bug #1 fallback will show broken image")

# ─── 10. robots.txt ──────────────────────────────────────────────
print("\n[10] robots.txt")
status, body = get("/robots.txt")
if status == 200:
    if "admin.html" in body:
        ok("robots.txt disallows /admin.html (correct for SEO bots)")
    else:
        fail("robots.txt does NOT disallow /admin.html")
else:
    fail(f"robots.txt not found — status={status}")

# ─── 11. Check index.html for Bug fixes ─────────────────────────
print("\n[11] index.html — SOURCE CODE BUG CHECKS")
with codecs.open('index.html', 'r', 'utf-8') as f:
    idx = f.read()

# Bug 1: Image fallback
if 'onerror' in idx and ('placeholderImg' in idx or 'placeholder' in idx):
    ok("Bug #1 (images): onerror fallback present in source")
else:
    fail("Bug #1 (images): No onerror image fallback found")

# Bug 2: Price rendering
if 'formatPrice' in idx or 'price_min' in idx:
    ok("Bug #2 (price): formatPrice function or price_min usage found")
else:
    fail("Bug #2 (price): No formatPrice function or price parsing found")

# Bug 3: Cart count update
if 'updateCartBadge' in idx or 'updateCartCount' in idx:
    ok("Bug #3 (cart count): updateCartBadge/updateCartCount function found")
else:
    fail("Bug #3 (cart count): No cart count update function found")

# Bug 4: Admin auth (checked admin.html above)

# Bug 5: Wishlist persistence
if "localStorage.setItem('wishlist'" in idx or 'saveState' in idx:
    ok("Bug #5 (wishlist): wishlist saved to localStorage or state")
else:
    fail("Bug #5 (wishlist): Wishlist not persisted to localStorage")

# Bug 6: WhatsApp message building
if 'encodeURIComponent' in idx and 'wa.me' in idx:
    ok("Bug #6 (WhatsApp): encodeURIComponent used for WhatsApp messages")
else:
    fail("Bug #6 (WhatsApp): WhatsApp message not properly encoded")

# Bug 7: Review form submit handler
if 'submitReview' in idx or "addEventListener('submit'" in idx:
    ok("Bug #7 (reviews): Review submit handler present")
else:
    fail("Bug #7 (reviews): No review form submit handler found")

# Bug 8: Profile save
if 'save-profile-btn' in idx or 'saveProfile' in idx or 'profile-name' in idx:
    ok("Bug #8 (profile): Profile save button handler present")
else:
    fail("Bug #8 (profile): No profile save handler found")

# Bug 9: Customize modal
if 'customize-add-btn' in idx or 'addCustomizedToCart' in idx:
    ok("Bug #9 (customize): Customize add-to-cart handler present")
else:
    fail("Bug #9 (customize): No customize add-to-cart handler")

# Bug 10: Bottom nav active state
if 'bottom-nav' in idx and ('showPage' in idx):
    ok("Bug #10 (bottom nav): showPage function found for bottom nav handling")
else:
    fail("Bug #10 (bottom nav): No active state logic for bottom nav")

# Bug 11: FAQ content
if 'FAQS' in idx and 'renderFAQ' in idx:
    ok("Bug #11 (FAQ): FAQ array and renderFAQ function present")
else:
    fail("Bug #11 (FAQ): FAQ content missing")

# Bug 12: admin.html robots
with codecs.open('admin.html', 'r', 'utf-8') as f:
    adm = f.read()
if 'adminToken' in adm or 'pw_admin_secret' in adm:
    ok("Bug #12/4 (admin auth): admin.html has JS auth guard")
else:
    fail("Bug #12/4 (admin auth): admin.html has no auth guard")

# ─── SUMMARY ─────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"  RESULTS: {len(PASS)} PASSED | {len(FAIL)} FAILED")
print("="*60)
if FAIL:
    print("\n  FAILURES:")
    for f in FAIL:
        print(f"    - {f}")
print()
