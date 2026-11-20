import hashlib

from data import queries

# what each role is allowed to do
permissions = {
    "owner": ["products", "record_sale", "view_sales", "cancel_sale", "choose_date",
              "expenses", "stock", "summary", "users"],
    "helper": ["record_sale", "stock"],
}


def has_permission(user, action):
    return action in permissions.get(user["role"], [])


def check_permission(user, action):
    if not has_permission(user, action):
        raise ValueError("You are not allowed to do this. Please ask the owner.")


# the PIN is saved as a hash, never as plain text
def make_hash(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def no_users_yet():
    return queries.count_users() == 0


def create_first_owner(name, pin):
    if not no_users_yet():
        raise ValueError("The owner account already exists.")
    queries.add_user(name, make_hash(pin), "owner")


def login(name, pin):
    row = queries.get_user_by_name(name)
    if row is None or row["pin_hash"] != make_hash(pin):
        raise ValueError("Wrong name or PIN.")
    return {"id": row["id"], "name": row["name"], "role": row["role"]}


def get_users(owner):
    check_permission(owner, "users")
    return queries.get_all_users()


def add_user(owner, name, pin, role):
    check_permission(owner, "users")
    if role not in permissions:
        raise ValueError("That role does not exist.")
    if queries.get_user_by_name(name) is not None:
        raise ValueError(f"The name {name} is already used.")
    queries.add_user(name, make_hash(pin), role)


def reset_pin(owner, user_id, new_pin):
    check_permission(owner, "users")
    if queries.get_user_by_id(user_id) is None:
        raise ValueError(f"There is no user with number {user_id}.")
    queries.update_pin(user_id, make_hash(new_pin))


def delete_user(owner, user_id):
    check_permission(owner, "users")
    if user_id == owner["id"]:
        raise ValueError("You cannot delete your own account.")
    if queries.get_user_by_id(user_id) is None:
        raise ValueError(f"There is no user with number {user_id}.")
    queries.delete_user(user_id)
