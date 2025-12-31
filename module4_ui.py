# """
# Module 4: Console User Interface
# - Provides menu-driven CLI with role selection and login.
# - Supports back and exit navigation options.
# - Role-based menus with all function options displayed explicitly.
# - Integrates matplotlib visualizations for admin & analyst.
# """

# import hashlib
# try:
#     import matplotlib.pyplot as plt
# except ImportError:
#     print("[ERROR] matplotlib not installed. Please install it using 'pip install matplotlib'.")
#     plt = None

# from module1_data_db import DatabaseManager, AuthManager, DataCollector, User, Customer, CallLog, SMSLog, DataSessionLog
# from module2_analytics import get_customer_summary, get_network_summary
# from module3_reporting import report_customer_summary, report_network_summary


# def prompt_create_user(auth):
#     print("\nCreate new user (type 'back' anytime to cancel)")
#     new_username = input("Enter new username: ").strip()
#     if new_username.lower() == "back":
#         return
#     new_password = input("Enter password: ").strip()
#     if new_password.lower() == "back":
#         return
#     new_role = input("Enter role (operator/analyst/admin): ").strip().lower()
#     if new_role.lower() == "back":
#         return
#     if new_role not in ["operator", "analyst", "admin"]:
#         print("[ERROR] Invalid role.")
#         return
#     auth.create_user(new_username, new_password, new_role)


# def show_pie_chart_user_roles(session):
#     if not plt:
#         print("[ERROR] matplotlib not installed; cannot show charts.")
#         return
#     try:
#         from sqlalchemy import func
#         data = session.query(User.role, func.count(User.id)).group_by(User.role).all()
#         if not data:
#             print("[INFO] No user data available for visualization.")
#             return
#         roles, counts = zip(*data)
#         plt.figure(figsize=(6,6))
#         plt.pie(counts, labels=roles, autopct='%1.1f%%', startangle=140)
#         plt.title("User Distribution by Role")
#         plt.show()
#     except Exception as e:
#         print(f"[ERROR] Could not generate user role pie chart: {e}")


# def show_line_chart_customer_calls(session, phone, Customer, CallLog):
#     if not plt:
#         print("[ERROR] matplotlib not installed; cannot show charts.")
#         return
#     try:
#         phone_h = hashlib.sha256(phone.encode()).hexdigest()
#         customer = session.query(Customer).filter_by(phone_hash=phone_h).first()
#         if not customer:
#             print("[ERROR] Customer not found for visualization.")
#             return

#         calls = session.query(CallLog).filter(CallLog.customer_id == customer.id).order_by(CallLog.timestamp).all()
#         if not calls:
#             print("[INFO] No call data available for customer.")
#             return

#         call_counts = {}
#         for call in calls:
#             day = call.timestamp.date()
#             call_counts[day] = call_counts.get(day, 0) + 1

#         dates = sorted(call_counts.keys())
#         counts = [call_counts[date] for date in dates]

#         plt.figure(figsize=(10,5))
#         plt.plot(dates, counts, marker='o')
#         plt.title(f"Call Volume Over Time for Customer {phone[-4:].rjust(len(phone), '*')}")
#         plt.xlabel("Date")
#         plt.ylabel("Number of Calls")
#         plt.grid(True)
#         plt.xticks(rotation=45)
#         plt.tight_layout()
#         plt.show()
#     except Exception as e:
#         print(f"[ERROR] Could not generate customer call chart: {e}")


# def list_all_customers(db_manager):
#     session = db_manager.get_session()
#     try:
#         customers = session.query(Customer).all()
#         if not customers:
#             print("[INFO] No customers found.")
#             return
#         print("\n---- Customer List ----")
#         for cust in customers:
#             # Display customer name and partial phone hash for privacy
#             print(f"ID: {cust.id} | Name: {cust.name} | Phone Hash (partial): {cust.phone_hash[:10]}...")
#         print("----------------------\n")
#     finally:
#         session.close()


# def run_console_app():
#     db = DatabaseManager()
#     auth = AuthManager(db)

#     session = db.get_session()
#     try:
#         default_users = [
#             ("operator1", "pass123", "operator"),
#             ("analyst1", "pass123", "analyst"),
#             ("admin1", "pass123", "admin")
#         ]
#         for username, password, role in default_users:
#             if not session.query(User).filter_by(username=username).first():
#                 auth.create_user(username, password, role)
#     finally:
#         session.close()

#     print("Welcome to Customer Usage Analytics System")

#     roles = ["admin", "operator", "analyst"]
#     while True:
#         print("\nSelect role to login or type 'exit' to quit:")
#         for idx, role in enumerate(roles, 1):
#             print(f"{idx}. {role.capitalize()}")
#         role_choice = input("Enter choice number or 'exit': ").strip().lower()
#         if role_choice == "exit":
#             print("Exiting application.")
#             return
#         try:
#             selected_role = roles[int(role_choice) - 1]
#             break
#         except (ValueError, IndexError):
#             print("[ERROR] Invalid input; enter a listed number or 'exit'.")

#     user = None
#     while not user:
#         print("Type 'back' to choose role, or 'exit' to quit.")
#         username = input(f"Username for role '{selected_role}': ").strip()
#         if username.lower() == "back":
#             return run_console_app()
#         if username.lower() == "exit":
#             print("Exiting application.")
#             return
#         password = input("Password: ").strip()
#         if password.lower() == "back":
#             return run_console_app()
#         if password.lower() == "exit":
#             print("Exiting application.")
#             return
#         user = auth.authenticate(username, password)
#         if not user:
#             print("[ERROR] Invalid credentials. Try again.")
#         elif user.role != selected_role:
#             print(f"[ERROR] Logged user role '{user.role}' doesn't match selected '{selected_role}'. Try again.")
#             user = None

#     collector = DataCollector(db, user)

#     while True:
#         print(f"\nLogged in as {user.username} ({user.role})")
#         print("Type 'exit' anytime to logout or 'create' to create a new user.")

#         # Show menu according to role
#         if user.role == "admin":
#             print("""
# 1. Add customer
# 2. Log call
# 3. Log SMS
# 4. Log data session
# 5. View customer report
# 6. View network report
# 7. List all users
# 8. Create new user
# 9. Delete user
# 10. Show user role distribution pie chart
# 11. View customer list
# 12. Logout
# """)
#         elif user.role == "operator":
#             print("""
# 1. Add customer
# 2. Log call
# 3. Log SMS
# 4. Log data session
# 5. Logout
# """)
#         elif user.role == "analyst":
#             print("""
# 1. View customer report
# 2. View network report
# 3. Show customer call usage chart
# 4. View customer list
# 5. Logout
# """)

#         choice = input("Choose an option: ").strip().lower()

#         # Logout conditions
#         if (
#             choice == "exit"
#             or (user.role == "admin" and choice == "12")
#             or (user.role == "operator" and choice == "5")
#             or (user.role == "analyst" and choice == "5")
#         ):
#             print("Logging out...")
#             break

#         if choice == "create":
#             prompt_create_user(auth)
#             continue

#         if user.role == "operator":
#             if choice == "1":
#                 name = input("Customer name: ").strip()
#                 phone = input("Customer phone: ").strip()
#                 collector.add_customer(name, phone)
#             elif choice == "2":
#                 phone = input("Customer phone: ").strip()
#                 call_type = input("Call type (incoming/outgoing): ").strip()
#                 duration = input("Duration (minutes): ").strip()
#                 try:
#                     d = float(duration)
#                     collector.log_call(phone, call_type, d)
#                 except:
#                     print("[ERROR] Invalid duration input.")
#             elif choice == "3":
#                 phone = input("Customer phone: ").strip()
#                 sms_type = input("SMS type (sent/received): ").strip()
#                 collector.log_sms(phone, sms_type)
#             elif choice == "4":
#                 phone = input("Customer phone: ").strip()
#                 data_used = input("Data used (MB): ").strip()
#                 try:
#                     d = float(data_used)
#                     collector.log_data_session(phone, d)
#                 except:
#                     print("[ERROR] Invalid data input.")
#             else:
#                 print("[ERROR] Invalid option. Choose a valid menu item.")

#         elif user.role == "analyst":
#             if choice == "1":
#                 phone = input("Customer phone: ").strip()
#                 session = db.get_session()
#                 try:
#                     summary = get_customer_summary(
#                         session, Customer, CallLog, SMSLog, DataSessionLog, phone
#                     )
#                     if summary:
#                         report_customer_summary(phone, summary)
#                     else:
#                         print(f"[ERROR] Customer with phone '{phone}' not found.")
#                 finally:
#                     session.close()
#             elif choice == "2":
#                 session = db.get_session()
#                 try:
#                     summary = get_network_summary(session, CallLog, SMSLog, DataSessionLog)
#                     report_network_summary(summary)
#                 finally:
#                     session.close()
#             elif choice == "3":
#                 phone = input("Customer phone: ").strip()
#                 session = db.get_session()
#                 try:
#                     show_line_chart_customer_calls(session, phone, Customer, CallLog)
#                 finally:
#                     session.close()
#             elif choice == "4":
#                 list_all_customers(db)
#             else:
#                 print("[ERROR] Invalid option. Choose a valid menu item.")

#         elif user.role == "admin":
#             if choice == "1":
#                 name = input("Customer name: ").strip()
#                 phone = input("Customer phone: ").strip()
#                 collector.add_customer(name, phone)
#             elif choice == "2":
#                 phone = input("Customer phone: ").strip()
#                 call_type = input("Call type (incoming/outgoing): ").strip()
#                 duration = input("Duration (minutes): ").strip()
#                 try:
#                     d = float(duration)
#                     collector.log_call(phone, call_type, d)
#                 except:
#                     print("[ERROR] Invalid duration input.")
#             elif choice == "3":
#                 phone = input("Customer phone: ").strip()
#                 sms_type = input("SMS type (sent/received): ").strip()
#                 collector.log_sms(phone, sms_type)
#             elif choice == "4":
#                 phone = input("Customer phone: ").strip()
#                 data_used = input("Data used (MB): ").strip()
#                 try:
#                     d = float(data_used)
#                     collector.log_data_session(phone, d)
#                 except:
#                     print("[ERROR] Invalid data input.")
#             elif choice == "5":
#                 phone = input("Customer phone: ").strip()
#                 session = db.get_session()
#                 try:
#                     summary = get_customer_summary(
#                         session, Customer, CallLog, SMSLog, DataSessionLog, phone
#                     )
#                     if summary:
#                         report_customer_summary(phone, summary)
#                     else:
#                         print(f"[ERROR] Customer with phone '{phone}' not found.")
#                 finally:
#                     session.close()
#             elif choice == "6":
#                 session = db.get_session()
#                 try:
#                     summary = get_network_summary(session, CallLog, SMSLog, DataSessionLog)
#                     report_network_summary(summary)
#                 finally:
#                     session.close()
#             elif choice == "7":
#                 auth.list_users()
#             elif choice == "8":
#                 prompt_create_user(auth)
#             elif choice == "9":
#                 del_username = input("Username to delete: ").strip()
#                 if del_username == user.username:
#                     print("[ERROR] Cannot delete yourself.")
#                 else:
#                     auth.delete_user(del_username)
#             elif choice == "10":
#                 session = db.get_session()
#                 try:
#                     show_pie_chart_user_roles(session)
#                 finally:
#                     session.close()
#             elif choice == "11":
#                 list_all_customers(db)
#             else:
#                 print("[ERROR] Invalid option. Choose a valid menu item.")
"""
Module 4: Console User Interface
- Provides menu-driven CLI with role selection and login.
- Supports back and exit navigation options.
- Role-based menus with all function options displayed explicitly.
- Integrates matplotlib visualizations for admin & analyst.
"""

import hashlib
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("[ERROR] matplotlib not installed. Please install it using 'pip install matplotlib'.")
    plt = None

from module1_data_db import DatabaseManager, AuthManager, DataCollector, User, Customer, CallLog, SMSLog, DataSessionLog
from module2_analytics import get_customer_summary, get_network_summary
from module3_reporting import report_customer_summary, report_network_summary


def prompt_create_user(auth):
    print("\nCreate new user (type 'back' anytime to cancel)")
    new_username = input("Enter new username: ").strip()
    if new_username.lower() == "back":
        return
    new_password = input("Enter password: ").strip()
    if new_password.lower() == "back":
        return
    new_role = input("Enter role (operator/analyst/admin): ").strip().lower()
    if new_role.lower() == "back":
        return
    if new_role not in ["operator", "analyst", "admin"]:
        print("[ERROR] Invalid role.")
        return
    auth.create_user(new_username, new_password, new_role)


def show_pie_chart_user_roles(session):
    if not plt:
        print("[ERROR] matplotlib not installed; cannot show charts.")
        return
    try:
        from sqlalchemy import func
        data = session.query(User.role, func.count(User.id)).group_by(User.role).all()
        if not data:
            print("[INFO] No user data available for visualization.")
            return
        roles, counts = zip(*data)
        plt.figure(figsize=(6,6))
        plt.pie(counts, labels=roles, autopct='%1.1f%%', startangle=140)
        plt.title("User Distribution by Role")
        plt.show()
    except Exception as e:
        print(f"[ERROR] Could not generate user role pie chart: {e}")


def show_line_chart_customer_calls(session, phone, Customer, CallLog):
    if not plt:
        print("[ERROR] matplotlib not installed; cannot show charts.")
        return
    try:
        phone_h = hashlib.sha256(phone.encode()).hexdigest()
        customer = session.query(Customer).filter_by(phone_hash=phone_h).first()
        if not customer:
            print("[ERROR] Customer not found for visualization.")
            return

        calls = session.query(CallLog).filter(CallLog.customer_id == customer.id).order_by(CallLog.timestamp).all()
        if not calls:
            print("[INFO] No call data available for customer.")
            return

        call_counts = {}
        for call in calls:
            day = call.timestamp.date()
            call_counts[day] = call_counts.get(day, 0) + 1

        dates = sorted(call_counts.keys())
        counts = [call_counts[date] for date in dates]

        plt.figure(figsize=(10,5))
        plt.plot(dates, counts, marker='o')
        plt.title(f"Call Volume Over Time for Customer {phone[-4:].rjust(len(phone), '*')}")
        plt.xlabel("Date")
        plt.ylabel("Number of Calls")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"[ERROR] Could not generate customer call chart: {e}")


def list_all_customers(db_manager):
    session = db_manager.get_session()
    try:
        customers = session.query(Customer).all()
        if not customers:
            print("[INFO] No customers found.")
            return
        print("\n---- Customer List ----")
        for cust in customers:
            # Display customer name and partial phone hash for privacy
            print(f"ID: {cust.id} | Name: {cust.name} | Phone Hash (partial): {cust.phone_hash[:10]}...")
        print("----------------------\n")
    finally:
        session.close()


def run_console_app():
    db = DatabaseManager()
    auth = AuthManager(db)

    session = db.get_session()
    try:
        default_users = [
            ("operator1", "pass123", "operator"),
            ("analyst1", "pass123", "analyst"),
            ("admin1", "pass123", "admin")
        ]
        for username, password, role in default_users:
            if not session.query(User).filter_by(username=username).first():
                auth.create_user(username, password, role)
    finally:
        session.close()

    print("Welcome to Customer Usage Analytics System")

    roles = ["admin", "operator", "analyst"]
    while True:
        print("\nSelect role to login or type 'exit' to quit:")
        for idx, role in enumerate(roles, 1):
            print(f"{idx}. {role.capitalize()}")
        role_choice = input("Enter choice number or 'exit': ").strip().lower()

        if role_choice == "exit":
            print("Exiting application.")
            return

        try:
            selected_role = roles[int(role_choice) - 1]
            break
        except (ValueError, IndexError):
            print("[ERROR] Invalid input; enter a listed number or 'exit'.")

    user = None
    while not user:
        print("Type 'back' to choose role, or 'exit' to quit.")
        username = input(f"Username for role '{selected_role}': ").strip()
        if username.lower() == "back":
            return run_console_app()
        if username.lower() == "exit":
            print("Exiting application.")
            return
        password = input("Password: ").strip()
        if password.lower() == "back":
            return run_console_app()
        if password.lower() == "exit":
            print("Exiting application.")
            return
        user = auth.authenticate(username, password)
        if not user:
            print("[ERROR] Invalid credentials. Try again.")
        elif user.role != selected_role:
            print(f"[ERROR] Logged user role '{user.role}' doesn't match selected '{selected_role}'. Try again.")
            user = None

    collector = DataCollector(db, user)

    while True:
        print(f"\nLogged in as {user.username} ({user.role})")
        print("Type 'exit' anytime to logout or 'create' to create a new user.")

        # Show menu according to role
        if user.role == "admin":
            print("""
Admin Menu:
1.  Add Customer
2.  Log a Call
3.  Log an SMS
4.  Log a Data Session
5.  Get Customer Report
6.  Get Network Report
7.  List Users
8.  Create User
9.  Delete User
10. Show User Roles Chart
11. List All Customers
""")
        elif user.role == "analyst":
            print("""
Analyst Menu:
1. Get Customer Report
2. Get Network Report
3. Show User Roles Chart
4. List All Customers
""")
        elif user.role == "operator":
            print("""
Operator Menu:
1. Add Customer
2. Log a Call
3. Log an SMS
4. Log a Data Session
""")

        choice = input("Enter choice: ").strip()

        if choice.lower() == "exit":
            break
        if choice.lower() == "create":
            prompt_create_user(auth)
            continue

        if user.role == "admin":
            if choice == "1":
                name = input("Customer Name: ").strip()
                phone = input("Customer Phone: ").strip()
                collector.add_customer(name, phone)
            elif choice == "2":
                phone = input("Customer Phone: ").strip()
                call_type = input("Call Type (incoming/outgoing): ").strip()
                duration = float(input("Duration (minutes): ").strip())
                collector.log_call(phone, call_type, duration)
            elif choice == "3":
                phone = input("Customer Phone: ").strip()
                sms_type = input("SMS Type (sent/received): ").strip()
                collector.log_sms(phone, sms_type)
            elif choice == "4":
                phone = input("Customer Phone: ").strip()
                data_used = float(input("Data Used (MB): ").strip())
                collector.log_data_session(phone, data_used)
            elif choice == "5":
                phone = input("Enter customer phone for report: ").strip()
                session = db.get_session()
                try:
                    summary = get_customer_summary(
                        session, Customer, CallLog, SMSLog, DataSessionLog, phone
                    )
                    if summary:
                        report_customer_summary(phone, summary)
                    else:
                        print(f"[ERROR] Customer with phone '{phone}' not found.")
                finally:
                    session.close()
            elif choice == "6":
                session = db.get_session()
                try:
                    summary = get_network_summary(session, CallLog, SMSLog, DataSessionLog)
                    report_network_summary(summary)
                finally:
                    session.close()
            elif choice == "7":
                auth.list_users()
            elif choice == "8":
                prompt_create_user(auth)
            elif choice == "9":
                del_username = input("Username to delete: ").strip()
                if del_username == user.username:
                    print("[ERROR] Cannot delete yourself.")
                else:
                    auth.delete_user(del_username)
            elif choice == "10":
                session = db.get_session()
                try:
                    show_pie_chart_user_roles(session)
                finally:
                    session.close()
            elif choice == "11":
                list_all_customers(db)
            else:
                print("[ERROR] Invalid option. Choose a valid menu item.")