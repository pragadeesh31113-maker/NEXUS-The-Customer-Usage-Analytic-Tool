# """
# Module 1: Data Collection & Database Management
# - Defines an enhanced SQLAlchemy ORM schema for detailed CDR data.
# - Handles DB setup, CRUD operations, and role-based access control.
# - Stores customer phone numbers and provides a masking function for display.
# """

# import hashlib
# import os
# from datetime import datetime
# import pandas as pd
# from sqlalchemy import (Column, Integer, String, DateTime, Float, ForeignKey,
#                         create_engine, func)
# from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Base = declarative_base()

# def hash_password(password):
#     """Hashes a password for storing."""
#     return hashlib.sha256(password.encode()).hexdigest()

# def mask_phone_number(phone):
#     """Masks a phone number, showing only the last 4 digits."""
#     if not phone or len(phone) < 4:
#         return "XXXX"
#     return f"******{phone[-4:]}"

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     username = Column(String(50), unique=True, nullable=False)
#     password_hash = Column(String(64), nullable=False)
#     role = Column(String(20), nullable=False, default='operator')

# class Customer(Base):
#     __tablename__ = "customers"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(100), nullable=False)
#     phone_number = Column(String(20), unique=True, nullable=False)
#     usage_logs = relationship("UsageLog", back_populates="customer", cascade="all, delete-orphan")

# class UsageLog(Base):
#     __tablename__ = "usage_logs"
#     id = Column(Integer, primary_key=True)
#     customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
#     record_type = Column(String(10), nullable=False)
#     timestamp = Column(DateTime, default=datetime.utcnow)
#     calling_number = Column(String(20))
#     called_number = Column(String(20))
#     duration_seconds = Column(Integer)
#     data_mb_used = Column(Float)
#     customer = relationship("Customer", back_populates="usage_logs")

# class DatabaseManager:
#     def __init__(self, db_url=None):
#         if not db_url:
#             db_url = os.getenv("USAGE_DB_URL", "sqlite:///customer_usage.db")
#         self.engine = create_engine(db_url)
#         Base.metadata.create_all(self.engine)
#         self.Session = sessionmaker(bind=self.engine)

#     def get_session(self):
#         return self.Session()

# class AuthManager:
#     def __init__(self, db_manager):
#         self.db_manager = db_manager

#     def create_user(self, username, password, role):
#         session = self.db_manager.get_session()
#         try:
#             if session.query(User).filter_by(username=username).first():
#                 return None
#             user = User(username=username, password_hash=hash_password(password), role=role)
#             session.add(user)
#             session.commit()
#             return user
#         except Exception as e:
#             session.rollback()
#             print(f"[ERROR] Creating user failed: {e}")
#             return None
#         finally:
#             session.close()

#     def authenticate(self, username, password):
#         session = self.db_manager.get_session()
#         try:
#             user = session.query(User).filter_by(username=username).first()
#             if user and user.password_hash == hash_password(password):
#                 return user
#             return None
#         finally:
#             session.close()

#     def get_all_users(self):
#         """Fetches a list of all users from the database."""
#         session = self.db_manager.get_session()
#         try:
#             return session.query(User).all()
#         finally:
#             session.close()

#     def delete_user(self, user_id):
#         """Deletes a user by their ID."""
#         session = self.db_manager.get_session()
#         try:
#             user = session.query(User).filter_by(id=user_id).first()
#             if user:
#                 session.delete(user)
#                 session.commit()
#                 return True
#             return False
#         except Exception as e:
#             session.rollback()
#             print(f"[ERROR] Deleting user failed: {e}")
#             return False
#         finally:
#             session.close()

#     def get_role_distribution(self):
#         """Calculates the distribution of user roles."""
#         session = self.db_manager.get_session()
#         try:
#             role_data = session.query(User.role, func.count(User.id)).group_by(User.role).all()
#             return pd.DataFrame(role_data, columns=['Role', 'Count'])
#         finally:
#             session.close()

# class DataManager:
#     def __init__(self, db_manager):
#         self.db_manager = db_manager

#     def add_customer(self, name, phone_number):
#         session = self.db_manager.get_session()
#         try:
#             if session.query(Customer).filter_by(phone_number=phone_number).first():
#                 return None
#             customer = Customer(name=name, phone_number=phone_number)
#             session.add(customer)
#             session.commit()
#             return customer
#         except Exception as e:
#             session.rollback()
#             print(f"[ERROR] Adding customer failed: {e}")
#             return None
#         finally:
#             session.close()

#     def process_cdr_upload(self, dataframe):
#         session = self.db_manager.get_session()
#         try:
#             new_logs = []
#             for _, row in dataframe.iterrows():
#                 customer = session.query(Customer).filter_by(id=row['customer_id']).first()
#                 if not customer:
#                     continue
#                 log_data = {
#                     'customer_id': customer.id,
#                     'record_type': row.get('type'),
#                     'timestamp': pd.to_datetime(row.get('timestamp', datetime.utcnow())),
#                     'calling_number': row.get('calling_number'),
#                     'called_number': row.get('called_number'),
#                     'duration_seconds': row.get('duration_seconds'),
#                     'data_mb_used': row.get('data_mb_used'),
#                 }
#                 new_logs.append(UsageLog(**log_data))
#             session.bulk_save_objects(new_logs)
#             session.commit()
#             return len(new_logs)
#         except Exception as e:
#             session.rollback()
#             print(f"[ERROR] CDR processing failed: {e}")
#             return 0
#         finally:
#             session.close()
"""
Module 1: Data Collection & Database Management
- Defines an enhanced SQLAlchemy ORM schema for detailed CDR data.
- Handles DB setup, CRUD operations, and role-based access control.
- Stores customer phone numbers and provides a masking function for display.
"""

import hashlib
import os
from datetime import datetime
import pandas as pd
from sqlalchemy import (Column, Integer, String, DateTime, Float, ForeignKey,
                        create_engine, func)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

def hash_password(password):
    """Hashes a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def mask_phone_number(phone):
    """Masks a phone number, showing only the last 4 digits."""
    if not phone or len(phone) < 4:
        return "XXXX"
    return f"******{phone[-4:]}"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    role = Column(String(20), nullable=False, default='operator')

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    usage_logs = relationship("UsageLog", back_populates="customer", cascade="all, delete-orphan")

class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    record_type = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    calling_number = Column(String(20))
    called_number = Column(String(20))
    duration_seconds = Column(Integer)
    data_mb_used = Column(Float)
    customer = relationship("Customer", back_populates="usage_logs")

class DatabaseManager:
    def __init__(self, db_url=None):
        if not db_url:
            db_url = os.getenv("USAGE_DB_URL", "sqlite:///customer_usage.db")
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

class AuthManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_user(self, username, password, role):
        session = self.db_manager.get_session()
        try:
            if session.query(User).filter_by(username=username).first():
                return None
            user = User(username=username, password_hash=hash_password(password), role=role)
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Creating user failed: {e}")
            return None
        finally:
            session.close()

    def authenticate(self, username, password):
        session = self.db_manager.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user and user.password_hash == hash_password(password):
                return user
            return None
        finally:
            session.close()

    def get_all_users(self):
        session = self.db_manager.get_session()
        try:
            return session.query(User).all()
        finally:
            session.close()

    def delete_user(self, user_id):
        session = self.db_manager.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Deleting user failed: {e}")
            return False
        finally:
            session.close()

    def get_role_distribution(self):
        session = self.db_manager.get_session()
        try:
            role_data = session.query(User.role, func.count(User.id)).group_by(User.role).all()
            return pd.DataFrame(role_data, columns=['Role', 'Count'])
        finally:
            session.close()

class DataManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_customer(self, name, phone_number):
        session = self.db_manager.get_session()
        try:
            if session.query(Customer).filter_by(phone_number=phone_number).first():
                return None
            customer = Customer(name=name, phone_number=phone_number)
            session.add(customer)
            session.commit()
            return customer
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Adding customer failed: {e}")
            return None
        finally:
            session.close()

    def process_cdr_upload(self, dataframe):
        session = self.db_manager.get_session()
        try:
            # --- NEW DATA CLEANING STEP ---
            dataframe['duration_seconds'] = pd.to_numeric(dataframe['duration_seconds'], errors='coerce')
            dataframe['data_mb_used'] = pd.to_numeric(dataframe['data_mb_used'], errors='coerce')

            new_logs = []
            for _, row in dataframe.iterrows():
                customer = session.query(Customer).filter_by(id=row['customer_id']).first()
                if not customer:
                    print(f"[WARNING] Skipping record for non-existent customer_id: {row['customer_id']}")
                    continue

                # Convert pandas NaN to None, which SQLAlchemy can handle as NULL
                duration = row['duration_seconds'] if pd.notna(row['duration_seconds']) else None
                data_used = row['data_mb_used'] if pd.notna(row['data_mb_used']) else None

                log_data = {
                    'customer_id': customer.id,
                    'record_type': row.get('type'),
                    'timestamp': pd.to_datetime(row.get('timestamp', datetime.utcnow())),
                    'calling_number': row.get('calling_number'),
                    'called_number': row.get('called_number'),
                    'duration_seconds': duration,
                    'data_mb_used': data_used,
                }
                new_logs.append(UsageLog(**log_data))
            
            if not new_logs:
                print("[INFO] No new valid logs to add from the CSV.")
                return 0

            session.bulk_save_objects(new_logs)
            session.commit()
            print(f"[INFO] Successfully added {len(new_logs)} logs to the database.")
            return len(new_logs)
        except Exception as e:
            session.rollback()
            print(f"[ERROR] CDR processing failed: {e}")
            raise e # Re-raise the exception to show a specific error in the UI
        finally:
            session.close()

