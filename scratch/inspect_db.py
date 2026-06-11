import sys
import os

# Ensure the parent directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import app, db, Customer, Bill
    with app.app_context():
        print("Successfully imported and created app context.")
        print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
        
        # Check customer details
        customers = Customer.query.all()
        print(f"Total customers: {len(customers)}")
        for i, c in enumerate(customers[:10]):
            print(f"[{i}] ID: {c.id}, Name: {c.name}, Mobile: {c.mobile}, Registration Date: {c.registration_date}")
            try:
                print(f"    Formatted Date: {c.registration_date.strftime('%d-%m-%Y %H:%M') if c.registration_date else 'None'}")
            except Exception as ex:
                print(f"    [ERROR Formatting Date]: {ex}")
                
            try:
                # Check bills
                bills = c.bills
                print(f"    Bills Count: {len(bills)}")
                for b in bills:
                    print(f"      Bill ID: {b.id}, Invoice: {b.invoice_number}, Total: {b.total}, Created At: {b.created_at}")
                    print(f"        Formatted Created At: {b.created_at.strftime('%d-%m-%Y') if b.created_at else 'None'}")
            except Exception as ex:
                print(f"    [ERROR Querying/Formatting Bills]: {ex}")
except Exception as e:
    import traceback
    traceback.print_exc()
