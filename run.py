from app import create_app, db

import os

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Optional: Initialize database here or via flask db upgrade
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

