from app import create_app, db, bcrypt
from app.models import User, Category, Product

app = create_app()

def seed_db() -> None:
    with app.app_context():
        # Create Admin
        if not User.query.filter_by(username='admin').first():
            hashed_pw = bcrypt.generate_password_hash('pureweaves2024').decode('utf-8')
            admin = User(username='admin', email='admin@pureweaves.com', password_hash=hashed_pw, is_admin=True)
            db.session.add(admin)

        # Create Categories
        cats = ['Kuchu', 'Kuchu Bunches', 'Bridal Collection', 'Bangles & Jewelry', 'Jewelry Sets', 'Blouse Work']
        cat_objects = {}
        for c in cats:
            if not Category.query.filter_by(name=c).first():
                new_cat = Category(name=c)
                db.session.add(new_cat)
                cat_objects[c] = new_cat

        db.session.commit()

        # Reload categories
        categories = Category.query.all()
        cat_map = {c.name: c for c in categories}

        # Create Products
        if not Product.query.first():
            products = [
                Product(name="Gold Locket Charm Kuchu", category_id=cat_map['Kuchu'].id, description="Traditional gold charm design.", price=450, image_path="https://via.placeholder.com/300?text=Gold+Locket", rating=4.8),
                Product(name="Pearl Diamond Kuchu", category_id=cat_map['Bridal Collection'].id, description="Exquisite pearl and diamond beads.", price=850, image_path="https://via.placeholder.com/300?text=Pearl+Diamond", rating=5.0),
                Product(name="Silk Thread Bangle Set", category_id=cat_map['Bangles & Jewelry'].id, description="Hand-wrapped silk thread bangles.", price=350, image_path="https://via.placeholder.com/300?text=Silk+Thread+Bangles", rating=4.5),
            ]
            for p in products:
                db.session.add(p)
                
            db.session.commit()
            print("Database seeded successfully with admin user and sample products.")
        else:
            print("Database already has products.")

if __name__ == '__main__':
    seed_db()
