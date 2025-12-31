# """
# generate_fake_data.py
# - A script to populate the database with realistic sample data for the upgraded application.
# - **New:** Intentionally creates a subset of customers with low activity to ensure churn modeling works.
# - **New:** Guarantees a high volume of calls, SMS, and data logs.
# """
# import random
# import os
# from faker import Faker
# from datetime import datetime, timedelta
# from module1_data_db import DatabaseManager, AuthManager, DataManager, Base, Customer, UsageLog, User

# fake = Faker()

# def clear_database(db_manager):
#     """Drops all tables and recreates them for a fresh start."""
#     print("[INFO] Clearing old database tables...")
#     Base.metadata.drop_all(db_manager.engine)
#     Base.metadata.create_all(db_manager.engine)
#     print("[INFO] Database tables cleared and recreated.")

# def create_default_users(auth_manager):
#     """Creates the default admin, analyst, and operator users."""
#     print("[INFO] Creating default users...")
#     users = [
#         ("admin1", "pass123", "admin"),
#         ("analyst1", "pass123", "analyst"),
#         ("operator1", "pass123", "operator")
#     ]
#     for user, pwd, role in users:
#         auth_manager.create_user(user, pwd, role)
#     print("[INFO] Default users created.")

# def generate_customers(db_manager, num_customers=100):
#     """Generates and inserts fake customers into the database."""
#     print(f"[INFO] Generating {num_customers} customers...")
#     session = db_manager.get_session()
    
#     try:
#         for _ in range(num_customers):
#             customer = Customer(
#                 name=fake.name(),
#                 phone_number=fake.phone_number()
#             )
#             session.add(customer)
#         session.commit()
        
#         all_customers = session.query(Customer).all()
#         print(f"[INFO] Successfully generated and added {len(all_customers)} customers.")
#         return all_customers
#     except Exception as e:
#         session.rollback()
#         print(f"[ERROR] Failed to generate customers: {e}")
#         return []
#     finally:
#         session.close()

# def generate_usage_logs(db_manager, customers, num_days=60, churn_candidate_ratio=0.3):
#     """Generates a realistic time-series of usage logs for all customers."""
#     session = db_manager.get_session()
#     print("[INFO] Generating time-series usage logs...")
    
#     logs = []
#     start_date = datetime.now() - timedelta(days=num_days)
    
#     num_churn_candidates = int(len(customers) * churn_candidate_ratio)
#     churn_candidates = customers[:num_churn_candidates]
#     active_customers = customers[num_churn_candidates:]

#     # --- Generate logs for ACTIVE customers ---
#     print(f"[INFO] Generating high-volume data for {len(active_customers)} active customers...")
#     for customer in active_customers:
#         for day in range(num_days):
#             if random.random() < 0.2: continue # 20% chance of being inactive on a given day
            
#             current_date = start_date + timedelta(days=day)
            
#             # Generate Calls
#             for _ in range(random.randint(1, 8)):
#                 logs.append(UsageLog(customer_id=customer.id, record_type='call', timestamp=current_date.replace(hour=random.randint(0,23)), duration_seconds=random.randint(30, 1200)))
            
#             # Generate SMS
#             for _ in range(random.randint(2, 20)):
#                 logs.append(UsageLog(customer_id=customer.id, record_type='sms', timestamp=current_date.replace(hour=random.randint(0,23))))

#             # Generate Data
#             for _ in range(random.randint(2, 10)):
#                 logs.append(UsageLog(customer_id=customer.id, record_type='data', timestamp=current_date.replace(hour=random.randint(0,23)), data_mb_used=random.uniform(50, 1024)))

#     # --- Generate logs for CHURN CANDIDATES ---
#     print(f"[INFO] Intentionally creating {num_churn_candidates} low-activity (churn candidate) customers...")
#     for customer in churn_candidates:
#         # These customers were only active in the first 20 days, then stopped completely.
#         for day in range(20):
#             current_date = start_date + timedelta(days=day)
            
#             if random.random() < 0.4: # 40% chance of activity
#                 # Generate very low usage
#                 logs.append(UsageLog(customer_id=customer.id, record_type='call', timestamp=current_date.replace(hour=random.randint(0,23)), duration_seconds=random.randint(10, 60)))
#                 logs.append(UsageLog(customer_id=customer.id, record_type='sms', timestamp=current_date.replace(hour=random.randint(0,23))))
#                 logs.append(UsageLog(customer_id=customer.id, record_type='data', timestamp=current_date.replace(hour=random.randint(0,23)), data_mb_used=random.uniform(5, 50)))

#     try:
#         session.bulk_save_objects(logs)
#         session.commit()
#         print(f"[INFO] Successfully generated and added {len(logs)} usage logs.")
#     except Exception as e:
#         session.rollback()
#         print(f"[ERROR] Failed to generate logs: {e}")
#     finally:
#         session.close()


# def main():
#     """Main function to orchestrate the data generation process."""
#     db_manager = DatabaseManager()
#     auth_manager = AuthManager(db_manager)
    
#     clear_database(db_manager)
#     create_default_users(auth_manager)
#     customers = generate_customers(db_manager, num_customers=100) # Increased customer count
#     if customers:
#         generate_usage_logs(db_manager, customers)

# if __name__ == "__main__":
#     main()


"""
generate_fake_data.py
- A script to populate the database with realistic sample data for the upgraded application.
- Creates distinct customer personas (Loyal, Medium, Waning, Churned) to ensure a rich and
  diverse dataset with a variety of churn probabilities.
- **New:** Appends data to the existing database instead of deleting it.
- **New:** Adds more variety and randomness to persona generation.
"""
import random
import os
from faker import Faker
from datetime import datetime, timedelta
from module1_data_db import DatabaseManager, AuthManager, DataManager, Base, Customer, UsageLog, User

fake = Faker()

def clear_database(db_manager):
    """(Optional) Drops all tables and recreates them for a fresh start."""
    print("[INFO] Clearing old database tables...")
    Base.metadata.drop_all(db_manager.engine)
    Base.metadata.create_all(db_manager.engine)
    print("[INFO] Database tables cleared and recreated.")

def create_default_users(auth_manager):
    """Creates the default admin, analyst, and operator users if they don't exist."""
    print("[INFO] Checking for default users...")
    session = auth_manager.db_manager.get_session()
    users_to_create = [
        ("admin1", "pass123", "admin"),
        ("analyst1", "pass123", "analyst"),
        ("operator1", "pass123", "operator")
    ]
    for user, pwd, role in users_to_create:
        if not session.query(User).filter_by(username=user).first():
            auth_manager.create_user(user, pwd, role)
            print(f"[INFO] User '{user}' created.")
    session.close()


def generate_customers(db_manager, num_customers=50):
    """Generates and inserts a new batch of fake customers into the database."""
    print(f"[INFO] Generating {num_customers} new customers...")
    session = db_manager.get_session()
    
    try:
        new_customers = []
        for _ in range(num_customers):
            # The database schema ensures phone_number is unique.
            # We rely on Faker's randomness; duplicates are rare and will be skipped by the DB.
            customer = Customer(name=fake.name(), phone_number=fake.phone_number())
            new_customers.append(customer)
        
        session.add_all(new_customers)
        session.commit()
        
        # After commit, the objects are 'expired'. We need their IDs to get fresh objects.
        new_customer_ids = [c.id for c in new_customers]
        fresh_customers = session.query(Customer).filter(Customer.id.in_(new_customer_ids)).all()
        
        print(f"[INFO] Successfully added {len(fresh_customers)} new customers.")
        return fresh_customers
    except Exception as e:
        session.rollback()
        # This can happen if a duplicate phone number is generated. It's safe to ignore for this script.
        print(f"[WARNING] Could not add all customers, likely due to a duplicate phone number: {e}")
        # Query and return all customers to continue the script
        return session.query(Customer).all()
    finally:
        session.close()


def generate_usage_logs(db_manager, customers, num_days=90):
    """Generates a realistic time-series of usage logs for different customer personas."""
    session = db_manager.get_session()
    print("[INFO] Generating time-series usage logs for different customer personas...")
    
    # --- FIX: Re-attach detached customer instances to the current session ---
    # The 'customers' list can contain objects from closed sessions. We merge them into the new session.
    try:
        customers = [session.merge(c) for c in customers]
    except Exception as e:
        print(f"[ERROR] Could not re-attach customers to session: {e}")
        session.close()
        return

    logs = []
    start_date = datetime.now() - timedelta(days=num_days)
    
    random.shuffle(customers)
    
    persona_ratios = {'loyal': 0.3, 'medium': 0.3, 'waning': 0.2, 'occasional': 0.1, 'churned': 0.1}
    
    num_customers = len(customers)
    loyal_end_idx = int(num_customers * persona_ratios['loyal'])
    medium_end_idx = loyal_end_idx + int(num_customers * persona_ratios['medium'])
    waning_end_idx = medium_end_idx + int(num_customers * persona_ratios['waning'])
    occasional_end_idx = waning_end_idx + int(num_customers * persona_ratios['occasional'])

    personas = {
        'Loyal': customers[0:loyal_end_idx],
        'Medium': customers[loyal_end_idx:medium_end_idx],
        'Waning': customers[medium_end_idx:waning_end_idx],
        'Occasional': customers[waning_end_idx:occasional_end_idx],
        'Churned': customers[occasional_end_idx:]
    }

    print(f"[INFO] Personas assigned: Loyal({len(personas['Loyal'])}), Medium({len(personas['Medium'])}), Waning({len(personas['Waning'])}), Occasional({len(personas['Occasional'])}), Churned({len(personas['Churned'])})")

    # --- 1. Loyal Power Users ---
    for customer in personas['Loyal']:
        specialty = random.choice(['call_heavy', 'data_heavy']) # Assign a random specialty
        for day in range(num_days):
            if random.random() < 0.1: continue
            date = start_date + timedelta(days=day)
            
            call_range = (5, 12) if specialty == 'call_heavy' else (2, 6)
            data_range = (2, 8) if specialty == 'data_heavy' else (3, 9)
            
            for _ in range(random.randint(*call_range)): logs.append(UsageLog(customer_id=customer.id, record_type='call', timestamp=date.replace(hour=random.randint(0,23)), duration_seconds=random.randint(100, 1500)))
            for _ in range(random.randint(5, 25)): logs.append(UsageLog(customer_id=customer.id, record_type='sms', timestamp=date.replace(hour=random.randint(0,23))))
            for _ in range(random.randint(*data_range)): logs.append(UsageLog(customer_id=customer.id, record_type='data', timestamp=date.replace(hour=random.randint(0,23)), data_mb_used=random.uniform(100, 1024)))

    # --- 2. Stable Medium Users ---
    for customer in personas['Medium']:
        for day in range(num_days):
            if random.random() < 0.4: continue
            date = start_date + timedelta(days=day)
            for _ in range(random.randint(1, 5)): logs.append(UsageLog(customer_id=customer.id, record_type='call', timestamp=date.replace(hour=random.randint(0,23)), duration_seconds=random.randint(50, 500)))
            for _ in range(random.randint(1, 10)): logs.append(UsageLog(customer_id=customer.id, record_type='sms', timestamp=date.replace(hour=random.randint(0,23))))
            for _ in range(random.randint(1, 7)): logs.append(UsageLog(customer_id=customer.id, record_type='data', timestamp=date.replace(hour=random.randint(0,23)), data_mb_used=random.uniform(50, 400)))

    # --- 3. Waning / At-Risk Users ---
    for customer in personas['Waning']:
        waning_factor = random.uniform(1.2, 2.0) # Each waning user declines at a different rate
        for day in range(num_days):
            activity_prob = 1.0 - (day / num_days)**waning_factor 
            if random.random() > activity_prob: continue
            date = start_date + timedelta(days=day)
            for _ in range(random.randint(0, 3)): logs.append(UsageLog(customer_id=customer.id, record_type='call', timestamp=date.replace(hour=random.randint(0,23)), duration_seconds=random.randint(10, 200)))
            for _ in range(random.randint(0, 5)): logs.append(UsageLog(customer_id=customer.id, record_type='sms', timestamp=date.replace(hour=random.randint(0,23))))
            for _ in range(random.randint(0, 4)): logs.append(UsageLog(customer_id=customer.id, record_type='data', timestamp=date.replace(hour=random.randint(0,23)), data_mb_used=random.uniform(10, 100)))

    # --- 4. Occasional / Low-Value Users ---
    for customer in personas['Occasional']:
        for day in range(num_days):
            if random.random() < 0.9: continue 
            date = start_date + timedelta(days=day)
            for _ in range(random.randint(0, 2)): logs.append(UsageLog(customer_id=customer.id, record_type='call', timestamp=date.replace(hour=random.randint(0,23)), duration_seconds=random.randint(10, 100)))
            for _ in range(random.randint(1, 5)): logs.append(UsageLog(customer_id=customer.id, record_type='sms', timestamp=date.replace(hour=random.randint(0,23))))
            
    # --- 5. Hard Churners ---
    for customer in personas['Churned']:
        for day in range(random.randint(15, 35)): # Random active period before churning
            date = start_date + timedelta(days=day)
            if random.random() < 0.5: continue
            for _ in range(random.randint(1, 4)): logs.append(UsageLog(customer_id=customer.id, record_type='call', timestamp=date.replace(hour=random.randint(0,23)), duration_seconds=random.randint(20, 300)))
            for _ in range(random.randint(1, 6)): logs.append(UsageLog(customer_id=customer.id, record_type='data', timestamp=date.replace(hour=random.randint(0,23)), data_mb_used=random.uniform(20, 200)))

    try:
        session.bulk_save_objects(logs)
        session.commit()
        print(f"[INFO] Successfully generated and added {len(logs)} usage logs.")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to generate logs: {e}")
    finally:
        session.close()

def main():
    """Main function to orchestrate the data generation process."""
    print("\n--- Running Data Generation in Append Mode ---")
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)
    data_manager = DataManager(db_manager)
    
    # This script NO LONGER deletes the database by default.
    # To start fresh, manually delete the 'customer_usage.db' file.
    # clear_database(db_manager) 
    
    create_default_users(auth_manager)
    
    # Fetch existing customers to generate logs for them
    session = db_manager.get_session()
    existing_customers = session.query(Customer).all()
    session.close()
    
    # You can choose to generate new customers or just add logs for existing ones
    # For this example, we will generate a small number of new customers each time.
    new_customers = generate_customers(db_manager, num_customers=50) 
    
    all_customers = existing_customers + new_customers
    if all_customers:
        generate_usage_logs(db_manager, all_customers)

if __name__ == "__main__":
    main()


