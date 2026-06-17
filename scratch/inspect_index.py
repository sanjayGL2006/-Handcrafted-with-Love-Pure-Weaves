import re
import codecs

with codecs.open('index.html', 'r', 'utf-8') as f:
    lines = f.readlines()

def search_lines(query, padding=2):
    for i, line in enumerate(lines):
        if query in line:
            print(f"--- Found '{query}' at line {i+1} ---")
            for j in range(max(0, i-padding), min(len(lines), i+padding+1)):
                print(f"{j+1}: {lines[j].rstrip()}")

print("Searching for img.src...")
search_lines("img.src =")

print("Searching for product.price...")
search_lines("modalPrice.textContent")

print("Searching for admin.html auth...")
with codecs.open('admin.html', 'r', 'utf-8') as f:
    admin_lines = f.readlines()
    print("Admin lines 1-10:")
    for i in range(10):
        print(f"{i+1}: {admin_lines[i].rstrip()}")

print("Searching for cart.push...")
search_lines("cart.push")

print("Searching for wishlist...")
search_lines("let wishlist = []")

print("Searching for whatsapp...")
search_lines("whatsapp-order-btn")
search_lines("window.open('https://wa.me")

print("Searching for review-form...")
search_lines("#review-form")

print("Searching for save-profile-btn...")
search_lines("#save-profile-btn")

print("Searching for customize-add-btn...")
search_lines("#customize-add-btn")

print("Searching for bottom nav active...")
search_lines("sections=['home'")

print("Searching for faq...")
search_lines('id="faq"')
