import sys
import os
sys.path.append(os.path.abspath('.'))

from index import app, Product

with app.app_context():
    p = Product.query.filter_by(is_active=True).first()
    if p:
        p_id = p.id
        p_price = p.price_min
        print(f"Using active product ID: {p_id}, price: {p_price}")
    else:
        p_id = 1
        p_price = 100
        print("No active product found, using default ID: 1")

payload = {
    "customer_id": None,
    "customer_name": "Test Customer",
    "mobile": "1234567890",
    "email": "test@example.com",
    "address": "Test Address",
    "items": [
        {
            "product_id": p_id,
            "quantity": 1,
            "price": p_price
        }
    ],
    "coupon_code": ""
}

with app.test_client() as client:
    res = client.post('/api/admin/bills/add', json=payload, headers={'X-Admin-Secret': 'pureweaves2024'})
    print("Status Code:", res.status_code)
    print("Data:", res.get_json())
