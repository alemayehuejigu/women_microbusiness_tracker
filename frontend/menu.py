import getpass

from frontend import inputs, shop_screens
from logic import checks, user_logic

# number, text on screen, and the permission needed to see it
menu_items = [
    ("1", "Add or update products", "products"),
    ("2", "Sales", "record_sale"),
    ("3", "Expenses", "expenses"),
    ("4", "View products and stock", "stock"),
    ("5", "Business summary", "summary"),
    ("6", "Manage users", "users"),
]


def show_banner():
    print("=" * 46)
    print("  WELCOME TO WOMEN'S MICROBUSINESS TRACKER")
    print("=" * 46)


def run_app():
    show_banner()
    if user_logic.no_users_yet():
        first_time_setup()
    user = login()
    if user is not None:
        main_menu(user)


def first_time_setup():
    print("\nFirst time setup: create the owner account.")
    name = inputs.ask("Your name: ", checks.check_name)
    pin = inputs.ask_new_pin()
    user_logic.create_first_owner(name, pin)
    print("Owner account created. Please log in.")


def login():
    tries = 0
    while tries < 3:
        print("\nPlease log in.")
        name = input("Name: ").strip()
        pin = getpass.getpass("PIN: ")
        try:
            user = user_logic.login(name, pin)
            print(f"\nHello {user['name']}. You are logged in as {user['role']}.")
            return user
        except ValueError as error:
            print(error)
            tries = tries + 1
    print("Too many wrong tries. Goodbye.")
    return None


def main_menu(user):
    while True:
        visible = [item for item in menu_items if user_logic.has_permission(user, item[2])]
        numbers = [item[0] for item in visible]

        print("\n--- Main menu ---")
        for item in visible:
            print(f"{item[0]}. {item[1]}")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "0":
                print("Goodbye.")
                break
            elif choice not in numbers:
                print("Please choose a number from the menu.")
            elif choice == "1":
                shop_screens.product_menu(user)
            elif choice == "2":
                shop_screens.sales_menu(user)
            elif choice == "3":
                shop_screens.expenses_menu(user)
            elif choice == "4":
                shop_screens.show_stock(user)
            elif choice == "5":
                shop_screens.summary_menu(user)
            elif choice == "6":
                users_menu(user)
        except ValueError as error:
            print(error)


def show_users(users):
    print(f"{'No.':<5}{'Name':<26}Role")
    print("-" * 40)
    for user in users:
        print(f"{user['id']:<5}{user['name']:<26}{user['role']}")


def users_menu(owner):
    while True:
        print("\n--- Manage users ---")
        print("1. Add a user")
        print("2. View users")
        print("3. Reset a PIN")
        print("4. Delete a user")
        print("0. Back")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                add_user(owner)
            elif choice == "2":
                show_users(user_logic.get_users(owner))
            elif choice == "3":
                reset_pin(owner)
            elif choice == "4":
                delete_user(owner)
            elif choice == "0":
                break
            else:
                print("Please choose a number from the menu.")
        except ValueError as error:
            print(error)


def add_user(owner):
    name = inputs.ask("Name of the new user: ", checks.check_name)
    role = inputs.ask("Role (owner or helper): ", checks.check_role)
    pin = inputs.ask_new_pin()
    user_logic.add_user(owner, name, pin, role)
    print(f"User {name} added as {role}.")


def reset_pin(owner):
    show_users(user_logic.get_users(owner))
    user_id = inputs.ask("User number: ", checks.check_positive_number)
    pin = inputs.ask_new_pin()
    user_logic.reset_pin(owner, user_id, pin)
    print("PIN changed.")


def delete_user(owner):
    show_users(user_logic.get_users(owner))
    user_id = inputs.ask("User number to delete: ", checks.check_positive_number)
    if inputs.ask_yes(f"Delete user {user_id}?"):
        user_logic.delete_user(owner, user_id)
        print("User deleted.")
    else:
        print("Nothing was deleted.")
