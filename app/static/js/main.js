// PureWeaves Main JS

function showToast(msg) {
  const container = document.createElement('div');
  container.className = 'toast show';
  container.textContent = msg;
  document.body.appendChild(container);
  
  setTimeout(() => {
    container.classList.remove('show');
    setTimeout(() => container.remove(), 300);
  }, 3000);
}

function addToCart(productId) {
  fetch('/api/cart/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ product_id: productId, quantity: 1 })
  })
  .then(response => {
    if (response.status === 401) {
      window.location.href = '/login';
      return;
    }
    return response.json();
  })
  .then(data => {
    if (data && data.message) {
      showToast('✅ ' + data.message);
      // Optional: Update cart badge dynamically
      const badge = document.getElementById('cartBadge');
      if (badge) {
        badge.textContent = parseInt(badge.textContent) + 1;
      }
    }
  })
  .catch(err => console.error(err));
}

function toggleWishlist(productId) {
  fetch('/api/wishlist/toggle', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ product_id: productId })
  })
  .then(response => {
    if (response.status === 401) {
      window.location.href = '/login';
      return;
    }
    return response.json();
  })
  .then(data => {
    if (data && data.status) {
      const btn = document.getElementById('wish_' + productId);
      if (btn) {
        if (data.status === 'added') {
          btn.classList.add('active');
          btn.textContent = '❤️';
          showToast('❤️ Added to wishlist!');
        } else {
          btn.classList.remove('active');
          btn.textContent = '🤍';
          showToast('💔 Removed from wishlist');
        }
      }
    }
  })
  .catch(err => console.error(err));
}

// Auto-hide flashed messages
setTimeout(() => {
  document.querySelectorAll('.toast').forEach(el => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 300);
  });
}, 4000);
