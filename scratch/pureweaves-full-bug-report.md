# Pure Weaves – Complete Bug Report & Solutions

**Website:** https://pureweaves.vercel.app/index.html  
**Audit Date:** June 2026  
**Total Issues Found:** 18

---

## 🔴 CRITICAL ERRORS (Fix Immediately)

---

### ❌ ERROR 1 — All Product Images Broken

**Problem:**  
Every `<img>` tag in the catalog, product modal, and featured section has an empty `src=""`. No product image loads anywhere on the site.

**Where it appears:**
- Product cards in catalog
- Product detail modal (`![Product Image](<>)`)
- Featured Designs section
- Customize Design modal (`![Saree Kuchu Design Preview](<>)`)

**Root Cause:** Product data is fetched from a backend (Python/SQLite) but the `image` field is either null, empty, or the path is wrong.

**Solution:**
```javascript
// In your product rendering function, add fallback:
function renderProductCard(product) {
  const img = document.createElement('img');
  
  // ✅ Fix: Use fallback if image is empty/null
  img.src = product.image && product.image.trim() !== '' 
    ? product.image 
    : '/assets/placeholder-kuchu.jpg';
  
  img.alt = product.name 
    ? `${product.name} – Pure Weaves handcrafted kuchu` 
    : 'Pure Weaves handcrafted saree kuchu';
  
  // ✅ Fix: Handle broken image links at runtime
  img.onerror = function() {
    this.src = '/assets/placeholder-kuchu.jpg';
    this.alt = 'Product image coming soon';
  };
}
```

```python
# In your Python backend, ensure image field is never null:
# backend/app.py or routes.py

@app.route('/api/products')
def get_products():
    products = db.execute('SELECT * FROM products').fetchall()
    result = []
    for p in products:
        result.append({
            'id': p['id'],
            'name': p['name'],
            'price': p['price'],
            # ✅ Fix: Default image if empty
            'image': p['image'] if p['image'] else '/assets/placeholder-kuchu.jpg',
            'category': p['category'],
        })
    return jsonify(result)
```

---

### ❌ ERROR 2 — All Prices Show ₹0

**Problem:**  
Every product shows `₹0` in product cards, the product detail modal (`### ₹0`), and the cart subtotal. Prices are not loading from the backend.

**Where it appears:**
- All 19 product cards
- Product detail popup
- Cart → Subtotal ₹0, Total ₹0

**Root Cause:** JS rendering runs before backend data loads, or the API response is failing silently.

**Solution:**
```javascript
// ✅ Fix: Add loading state + proper error handling for product fetch

async function loadProducts() {
  // Show skeleton loader while fetching
  showSkeletonCards(6);

  try {
    const response = await fetch('/api/products');
    
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    
    const products = await response.json();
    
    if (!products || products.length === 0) {
      showEmptyState('No products available right now.');
      return;
    }
    
    renderProducts(products);
    
  } catch (error) {
    console.error('Failed to load products:', error);
    showErrorBanner('Unable to load designs. Please refresh the page.');
  }
}

function renderProductCard(product) {
  // ✅ Fix: Never show ₹0 — show "Price on request" instead
  const priceDisplay = (product.price && product.price > 0)
    ? `₹${product.price.toLocaleString('en-IN')}`
    : 'Price on request';
  
  return `
    <div class="product-card">
      <p class="product-price">${priceDisplay}</p>
    </div>
  `;
}
```

---

### ❌ ERROR 3 — FAQ Section Completely Empty

**Problem:**  
The FAQ section renders the heading "Frequently Asked Questions" but has zero content inside — no questions, no answers, no accordion items.

**Root Cause:** FAQ content was never added to the HTML or a data source.

**Solution:**
```javascript
// ✅ Fix: Add FAQ data array and render accordion

const faqData = [
  {
    q: "How do I place an order?",
    a: "Add items to your cart and tap 'Place Order via WhatsApp'. Your cart details will be sent directly to us at +91 80887 44654."
  },
  {
    q: "Can I customize the colors?",
    a: "Yes! We accept custom color requests. Share your saree body and border colors via WhatsApp and we'll handcraft a matching kuchu."
  },
  {
    q: "How long does delivery take?",
    a: "Standard orders: 5–7 working days. Bridal/bulk orders: 10–14 working days. Delivery time will be confirmed on WhatsApp."
  },
  {
    q: "Do you ship outside Karnataka?",
    a: "Yes, we ship across India. Shipping charges will be discussed on WhatsApp based on your location."
  },
  {
    q: "What is your return policy?",
    a: "Since all items are handcrafted to order, we do not accept returns. However, if there is a defect, contact us within 48 hours of delivery."
  },
  {
    q: "Do you accept bulk orders?",
    a: "Yes! Bulk orders are welcome and receive special discounts. Contact us on WhatsApp for bulk pricing."
  },
  {
    q: "What materials are used?",
    a: "We use premium silk threads, gold beads, pearl spacers, and silver ring spacers — all handcrafted using traditional techniques."
  },
  {
    q: "How do I track my order?",
    a: "Order updates are shared via WhatsApp. You'll receive a message when your order is dispatched with tracking details."
  }
];

function renderFAQ() {
  const faqSection = document.querySelector('.faq-content');
  if (!faqSection) return;

  faqSection.innerHTML = faqData.map((item, i) => `
    <div class="faq-item">
      <button class="faq-question" onclick="toggleFAQ(${i})" aria-expanded="false">
        ${item.q}
        <span class="faq-icon">＋</span>
      </button>
      <div class="faq-answer" id="faq-${i}" style="display:none">
        <p>${item.a}</p>
      </div>
    </div>
  `).join('');
}

function toggleFAQ(index) {
  const answer = document.getElementById(`faq-${index}`);
  const isOpen = answer.style.display !== 'none';
  answer.style.display = isOpen ? 'none' : 'block';
}

document.addEventListener('DOMContentLoaded', renderFAQ);
```

---

### ❌ ERROR 4 — Reviews Show "5.0 ⭐" With Zero Reviews

**Problem:**  
The reviews modal hardcodes "Average Rating: 5.0 ⭐" but displays no actual customer reviews. A 5-star rating with zero reviews looks fake and untrustworthy.

**Root Cause:** Rating is hardcoded in HTML, not calculated from real data.

**Solution:**
```javascript
// ✅ Fix: Calculate rating dynamically, show empty state if no reviews

async function loadReviews() {
  try {
    const response = await fetch('/api/reviews');
    const reviews = await response.json();
    
    const reviewContainer = document.querySelector('.reviews-list');
    const ratingDisplay = document.querySelector('.average-rating');
    
    if (!reviews || reviews.length === 0) {
      // ✅ Fix: Show empty state instead of fake 5.0
      reviewContainer.innerHTML = `
        <div class="empty-reviews">
          <p>⭐ No reviews yet.</p>
          <p>Be the first to share your experience!</p>
        </div>
      `;
      ratingDisplay.style.display = 'none';
      return;
    }
    
    // ✅ Calculate real average
    const avg = (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1);
    ratingDisplay.textContent = `Average Rating: ${avg} ⭐ (${reviews.length} reviews)`;
    
    // Render review cards
    reviewContainer.innerHTML = reviews.map(r => `
      <div class="review-card">
        <div class="review-stars">${'⭐'.repeat(r.rating)}</div>
        <p class="review-text">"${r.comment}"</p>
        <p class="review-author">– ${r.name}, ${r.date}</p>
      </div>
    `).join('');
    
  } catch (error) {
    console.error('Failed to load reviews:', error);
  }
}
```

---

## 🟡 MEDIUM BUGS

---

### ⚠️ BUG 5 — Login & Logout Buttons Both Visible

**Problem:**  
Both `Login` and `Logout` buttons appear in the navbar simultaneously. There are two navbars in the HTML and both show both buttons with no auth-state check on load.

**Solution:**
```javascript
// ✅ Fix: Toggle auth buttons based on login state

function updateAuthUI() {
  const user = JSON.parse(localStorage.getItem('pw_user') || 'null');
  const loginBtns = document.querySelectorAll('.btn-login');
  const logoutBtns = document.querySelectorAll('.btn-logout');
  
  loginBtns.forEach(btn => btn.style.display = user ? 'none' : 'block');
  logoutBtns.forEach(btn => btn.style.display = user ? 'block' : 'none');
  
  // Update account section
  const guestLabel = document.querySelector('.account-name');
  if (guestLabel) {
    guestLabel.textContent = user ? user.name : 'Guest';
  }
}

// Call on every page load
document.addEventListener('DOMContentLoaded', updateAuthUI);
```

```html
<!-- ✅ Fix: Hide logout button by default in HTML -->
<button class="btn-login">Login</button>
<button class="btn-logout" style="display:none">Logout</button>
```

---

### ⚠️ BUG 6 — Canonical URL Points to Wrong Domain

**Problem:**  
The canonical tag and all OG/Twitter meta tags point to `https://pureweaves.netlify.app/` instead of the live Vercel domain. Google may index the wrong URL.

**Solution:**
```html
<!-- ❌ Wrong (current) -->
<link rel="canonical" href="https://pureweaves.netlify.app/" />
<meta property="og:url" content="https://pureweaves.netlify.app/" />
<meta property="og:image" content="https://pureweaves.netlify.app/og-image.svg" />
<meta name="twitter:image" content="https://pureweaves.netlify.app/og-image.svg" />

<!-- ✅ Fix: Update all to Vercel domain -->
<link rel="canonical" href="https://pureweaves.vercel.app/" />
<meta property="og:url" content="https://pureweaves.vercel.app/" />
<meta property="og:image" content="https://pureweaves.vercel.app/og-image.svg" />
<meta name="twitter:image" content="https://pureweaves.vercel.app/og-image.svg" />
```

---

### ⚠️ BUG 7 — "70+ Unique Designs" but Only 19 in Catalog

**Problem:**  
About section claims "70+ Unique Designs" but catalog shows only 19. Hardcoded numbers in two different places are out of sync.

**Solution:**
```javascript
// ✅ Fix: Derive count from actual product data dynamically

async function updateDesignCount() {
  try {
    const response = await fetch('/api/products');
    const products = await response.json();
    const count = products.length;
    
    // Update catalog header
    document.querySelector('.catalog-count').textContent = 
      `${count} Handcrafted Kuchu & Bunch Designs`;
    
    // Update About section stat
    document.querySelector('.stat-designs').textContent = `${count}+`;
    
    // Update "View All X Designs" link
    document.querySelector('.view-all-link').textContent = 
      `View All ${count} Designs →`;
      
  } catch(e) {
    console.error('Count update failed', e);
  }
}
```

---

### ⚠️ BUG 8 — Coupon Field: No Validation or Error Message

**Problem:**  
The cart has a coupon code "Apply" button but pressing it with an empty field or wrong code gives no feedback. Users are left wondering if it worked.

**Solution:**
```javascript
// ✅ Fix: Full coupon validation with user feedback

const VALID_COUPONS = {
  'PURE10': { type: 'percent', value: 10, label: '10% off' },
  'FIRST50': { type: 'flat', value: 50, label: '₹50 off' },
  'BULK20': { type: 'percent', value: 20, label: '20% off for bulk' }
};

function applyCoupon() {
  const input = document.querySelector('.coupon-input');
  const feedback = document.querySelector('.coupon-feedback');
  const code = input.value.trim().toUpperCase();
  
  // Clear previous feedback
  feedback.className = 'coupon-feedback';
  
  if (!code) {
    feedback.textContent = '⚠️ Please enter a coupon code.';
    feedback.classList.add('error');
    return;
  }
  
  if (VALID_COUPONS[code]) {
    const coupon = VALID_COUPONS[code];
    feedback.textContent = `✅ Coupon applied! ${coupon.label}`;
    feedback.classList.add('success');
    applyDiscount(coupon);
    input.disabled = true;
  } else {
    feedback.textContent = '❌ Invalid coupon code. Please try again.';
    feedback.classList.add('error');
    input.value = '';
    input.focus();
  }
}
```

```css
/* ✅ Add feedback styles */
.coupon-feedback.success { color: #2e7d32; font-size: 0.85rem; margin-top: 4px; }
.coupon-feedback.error   { color: #c62828; font-size: 0.85rem; margin-top: 4px; }
```

---

### ⚠️ BUG 9 — Product Modal Always Shows ₹0 and Empty Image

**Problem:**  
When clicking any product, the detail modal shows `### ₹0` and a broken image `![Product Image](<>)` regardless of which product was clicked.

**Solution:**
```javascript
// ✅ Fix: Properly bind all product data to modal

function openProductModal(product) {
  const modal = document.getElementById('productModal');
  
  // Image
  const img = modal.querySelector('.modal-product-image');
  img.src = product.image || '/assets/placeholder-kuchu.jpg';
  img.alt = product.name || 'Pure Weaves product';
  img.onerror = () => { img.src = '/assets/placeholder-kuchu.jpg'; };
  
  // Name & Category
  modal.querySelector('.modal-product-name').textContent = product.name || 'Handcrafted Design';
  modal.querySelector('.modal-product-category').textContent = product.category || 'Kuchu';
  
  // Price — never show ₹0
  const price = product.price > 0
    ? `₹${product.price.toLocaleString('en-IN')}`
    : 'Price on request';
  modal.querySelector('.modal-product-price').textContent = price;
  
  // Stock
  const stockEl = modal.querySelector('.modal-stock-status');
  stockEl.textContent = product.stock > 0 ? '✅ In Stock' : '❌ Out of Stock';
  stockEl.style.color = product.stock > 0 ? '#2e7d32' : '#c62828';
  
  // Store product id for add-to-cart
  modal.dataset.productId = product.id;
  
  modal.style.display = 'flex';
}
```

---

## 🟢 MINOR ISSUES

---

### 🔹 BUG 10 — "Pull to Refresh" Visible on Desktop

**Problem:** The `🍃 Pull to refresh...` text renders on desktop screens where pull-to-refresh doesn't apply.

**Solution:**
```css
/* ✅ Fix: Mobile-only visibility */
.pull-to-refresh { display: none; }

@media (max-width: 768px) {
  .pull-to-refresh { display: block; }
}
```

---

### 🔹 BUG 11 — No Loading Skeleton for Products

**Problem:** While products load, the catalog shows a blank area. On slow connections this looks like a crash.

**Solution:**
```javascript
// ✅ Fix: Skeleton loader while products fetch

function showSkeletonCards(count = 6) {
  const grid = document.querySelector('.products-grid');
  grid.innerHTML = Array(count).fill(`
    <div class="skeleton-card">
      <div class="skeleton-img"></div>
      <div class="skeleton-line short"></div>
      <div class="skeleton-line long"></div>
      <div class="skeleton-line price"></div>
    </div>
  `).join('');
}
```

```css
/* ✅ Shimmer animation */
.skeleton-img  { height: 200px; border-radius: 8px; }
.skeleton-line { height: 14px; border-radius: 4px; margin: 8px 0; }
.skeleton-line.short { width: 60%; }
.skeleton-line.long  { width: 90%; }
.skeleton-line.price { width: 40%; }

.skeleton-card {
  background: #fff;
  border-radius: 12px;
  padding: 12px;
  animation: shimmer 1.4s infinite linear;
  background: linear-gradient(90deg, #f3e8ec 25%, #ecdde1 50%, #f3e8ec 75%);
  background-size: 200% 100%;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

### 🔹 BUG 12 — No Out-of-Stock Visual on Products

**Problem:** All 19 products show "In Stock" regardless of real inventory. No sold-out visual exists.

**Solution:**
```javascript
// ✅ Fix: Render out-of-stock state

function renderProductCard(product) {
  const isOutOfStock = !product.stock || product.stock <= 0;

  return `
    <div class="product-card ${isOutOfStock ? 'out-of-stock' : ''}">
      <div class="img-wrapper">
        <img src="${product.image || '/assets/placeholder-kuchu.jpg'}" 
             alt="${product.name}" />
        ${isOutOfStock ? '<span class="oos-badge">Sold Out</span>' : ''}
      </div>
      <h3>${product.name}</h3>
      <p class="price">${product.price > 0 ? '₹' + product.price : 'Price on request'}</p>
      <button ${isOutOfStock ? 'disabled' : ''} onclick="addToCart(${product.id})">
        ${isOutOfStock ? 'Out of Stock' : '🛒 Add to Cart'}
      </button>
    </div>
  `;
}
```

```css
/* ✅ Out-of-stock styles */
.out-of-stock img    { filter: grayscale(70%); opacity: 0.7; }
.out-of-stock button { background: #ccc; cursor: not-allowed; }
.oos-badge {
  position: absolute; top: 8px; left: 8px;
  background: #c62828; color: #fff;
  padding: 3px 10px; border-radius: 12px; font-size: 0.75rem;
}
```

---

### 🔹 BUG 13 — Privacy Policy Link Goes Nowhere

**Problem:**  
The footer has a "Privacy Policy" link but no `/privacy` page exists on the site. Clicking it leads to a 404 or blank page. This is also a legal requirement in India (IT Act).

**Solution:**
```html
<!-- ✅ Option A: Create /privacy.html page -->
<a href="/privacy.html">Privacy Policy</a>

<!-- ✅ Option B: Open a modal with privacy content -->
<a href="#" onclick="openModal('privacyModal')">Privacy Policy</a>
```

Minimum Privacy Policy content:
```
1. We collect: name, mobile number, WhatsApp chat history for order purposes.
2. We do not sell your data to third parties.
3. Orders placed via WhatsApp are stored for business records only.
4. Contact: +91 80887 44654 for data deletion requests.
```

---

### 🔹 BUG 14 — "Contact Us" Footer Link Goes Nowhere

**Problem:** "Contact Us" is listed in the footer's Information section but there is no `/contact` page or anchor scroll target.

**Solution:**
```html
<!-- ✅ Fix: Point to WhatsApp directly -->
<a href="https://wa.me/918088744654" target="_blank">Contact Us</a>

<!-- OR scroll to footer contact info -->
<a href="#footer-contact">Contact Us</a>
```

---

### 🔹 BUG 15 — Multiple H1 Tags on One Page

**Problem:**  
The page uses `<h1>` for "Pure Weaves" (hero), "Our Collection", "Your Cart", and "My Wishlist" — that's 4 H1s. Only one H1 is allowed per page for SEO.

**Solution:**
```html
<!-- ✅ Fix: Only one H1 in the hero -->
<h1>Pure Weaves – Handcrafted Saree Kuchu & Bunches</h1>

<!-- All other sections use H2 -->
<h2>Our Collection</h2>
<h2>Your Cart</h2>
<h2>My Wishlist</h2>
<h2>My Account</h2>
```

---

### 🔹 BUG 16 — Cart Total Does Not Update in Real Time

**Problem:**  
Cart shows `Subtotal ₹0`, `Discount -₹0`, `Total ₹0` even after adding products. The total is not recalculated when items are added.

**Solution:**
```javascript
// ✅ Fix: Recalculate cart total every time cart changes

function updateCartSummary() {
  const cart = JSON.parse(localStorage.getItem('pw_cart') || '[]');
  
  const subtotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
  const discount = getAppliedDiscount(subtotal);
  const total = subtotal - discount;
  
  document.querySelector('.cart-subtotal').textContent = `₹${subtotal.toLocaleString('en-IN')}`;
  document.querySelector('.cart-discount').textContent = `-₹${discount.toLocaleString('en-IN')}`;
  document.querySelector('.cart-total').textContent = `₹${total.toLocaleString('en-IN')}`;
  
  // Update cart badge in navbar
  document.querySelectorAll('.cart-count').forEach(el => {
    el.textContent = cart.reduce((sum, i) => sum + i.qty, 0);
  });
}

// Call after every add/remove
function addToCart(product) {
  const cart = JSON.parse(localStorage.getItem('pw_cart') || '[]');
  const existing = cart.find(i => i.id === product.id);
  if (existing) existing.qty++;
  else cart.push({ ...product, qty: 1 });
  localStorage.setItem('pw_cart', JSON.stringify(cart));
  updateCartSummary(); // ← ✅ Recalculate immediately
}
```

---

### 🔹 BUG 17 — Profile Form Has No Save Confirmation

**Problem:**  
The "Save Profile" button in My Account has no success message after saving. Users don't know if it worked.

**Solution:**
```javascript
// ✅ Fix: Show feedback after save

function saveProfile() {
  const name   = document.querySelector('#profile-name').value.trim();
  const mobile = document.querySelector('#profile-mobile').value.trim();
  const email  = document.querySelector('#profile-email').value.trim();
  
  if (!name || !mobile) {
    showToast('⚠️ Name and mobile are required.', 'error');
    return;
  }
  
  localStorage.setItem('pw_user', JSON.stringify({ name, mobile, email }));
  updateAuthUI();
  showToast('✅ Profile saved successfully!', 'success');
}

function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
```

---

### 🔹 BUG 18 — Wishlist Not Persisted Across Sessions

**Problem:**  
Wishlist items are stored only in memory (JS variables). When the user refreshes or closes the tab, the wishlist is lost.

**Solution:**
```javascript
// ✅ Fix: Persist wishlist to localStorage

function toggleWishlist(productId) {
  let wishlist = JSON.parse(localStorage.getItem('pw_wishlist') || '[]');
  const idx = wishlist.indexOf(productId);
  
  if (idx === -1) {
    wishlist.push(productId);
    showToast('❤️ Added to wishlist!');
  } else {
    wishlist.splice(idx, 1);
    showToast('💔 Removed from wishlist.');
  }
  
  localStorage.setItem('pw_wishlist', JSON.stringify(wishlist));
  updateWishlistUI(wishlist);
}

// On page load, restore wishlist hearts
function restoreWishlistUI() {
  const wishlist = JSON.parse(localStorage.getItem('pw_wishlist') || '[]');
  wishlist.forEach(id => {
    const heartBtn = document.querySelector(`[data-product-id="${id}"] .heart-btn`);
    if (heartBtn) heartBtn.classList.add('active');
  });
}

document.addEventListener('DOMContentLoaded', restoreWishlistUI);
```

---

## 📊 Summary Table

| # | Bug | Severity | Area | Status |
|---|-----|----------|------|--------|
| 1 | Product images broken (`src=""`) | 🔴 Critical | Catalog | Fix backend + JS fallback |
| 2 | All prices show ₹0 | 🔴 Critical | Catalog/Cart | Fix API fetch + error handling |
| 3 | FAQ section empty | 🔴 Critical | Content | Add JS FAQ data + accordion |
| 4 | Reviews show 5.0 with no data | 🔴 Critical | Reviews | Calculate dynamically |
| 5 | Login + Logout both visible | 🟡 Medium | Auth UI | Check localStorage on load |
| 6 | Canonical URL = wrong domain | 🟡 Medium | SEO | Update to Vercel URL |
| 7 | "70+ designs" vs 19 shown | 🟡 Medium | Content | Derive count from API |
| 8 | Coupon field: no validation | 🟡 Medium | Cart | Add JS validation |
| 9 | Product modal shows ₹0 + no image | 🟡 Medium | Modal | Fix openProductModal() |
| 10 | Pull-to-refresh on desktop | 🟢 Minor | UI | CSS media query |
| 11 | No loading skeleton | 🟢 Minor | UX | Shimmer cards |
| 12 | No out-of-stock state | 🟢 Minor | Inventory | Stock check in render |
| 13 | Privacy Policy links to 404 | 🟢 Minor | Legal | Create page or modal |
| 14 | Contact Us links to nothing | 🟢 Minor | Navigation | Link to WhatsApp |
| 15 | Multiple H1 tags (4 total) | 🟢 Minor | SEO | One H1 in hero only |
| 16 | Cart total doesn't update live | 🟢 Minor | Cart | updateCartSummary() |
| 17 | Profile save: no confirmation | 🟢 Minor | UX | Show toast message |
| 18 | Wishlist lost on refresh | 🟢 Minor | UX | Persist to localStorage |

---

**Total:** 4 Critical · 5 Medium · 9 Minor = **18 Bugs**

*Bug Report by Claude · June 2026*
