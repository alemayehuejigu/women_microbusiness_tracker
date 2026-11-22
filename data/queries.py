import sqlite3

from data import database


# users

def count_users():
    rows = database.run_query("SELECT COUNT(*) AS total FROM users")
    return rows[0]["total"]

def get_user_by_name(name):
    rows = database.run_query(
        "SELECT users.id, users.name, users.pin_hash, roles.name AS role "
        "FROM users JOIN roles ON users.role_id = roles.id "
        "WHERE users.name = ?",
        (name,),
    )
    if len(rows) == 0:
        return None
    return rows[0]

def get_user_by_id(user_id):
    rows = database.run_query(
        "SELECT users.id, users.name, roles.name AS role "
        "FROM users JOIN roles ON users.role_id = roles.id "
        "WHERE users.id = ?",
        (user_id,),
    )
    if len(rows) == 0:
        return None
    return rows[0]




def get_all_users():
    return database.run_query(
        "SELECT users.id, users.name, roles.name AS role "
        "FROM users JOIN roles ON users.role_id = roles.id "
        "ORDER BY users.name"
    )


def add_user(name, pin_hash, role_name):
    cursor = database.run_change(
        "INSERT INTO users (name, pin_hash, role_id) "
        "VALUES (?, ?, (SELECT id FROM roles WHERE name = ?))",
        (name, pin_hash, role_name),
    )
    return cursor.lastrowid

def update_pin(user_id, pin_hash):
    database.run_change("UPDATE users SET pin_hash = ? WHERE id = ?", (pin_hash, user_id))


def delete_user(user_id):
    database.run_change("DELETE FROM users WHERE id = ?", (user_id,))


# products

def add_product(name, cost_price, selling_price, stock):
    cursor = database.run_change(
        "INSERT INTO products (name, cost_price, selling_price, stock) VALUES (?, ?, ?, ?)",
        (name, cost_price, selling_price, stock),
    )
    return cursor.lastrowid


def get_all_products():
    return database.run_query("SELECT * FROM products ORDER BY name")


def get_product_by_id(product_id):
    rows = database.run_query("SELECT * FROM products WHERE id = ?", (product_id,))
    if len(rows) == 0:
        return None
    return rows[0]


def get_product_by_name(name):
    rows = database.run_query("SELECT * FROM products WHERE name = ?", (name,))
    if len(rows) == 0:
        return None
    return rows[0]


def search_products(text):
    return database.run_query(
        "SELECT * FROM products WHERE name LIKE ? ORDER BY name",
        ("%" + text + "%",),
    )


def update_product(product_id, name, cost_price, selling_price, stock):
    database.run_change(
        "UPDATE products SET name = ?, cost_price = ?, selling_price = ?, stock = ? WHERE id = ?",
        (name, cost_price, selling_price, stock, product_id),
    )


def add_stock(product_id, quantity):
    database.run_change(
        "UPDATE products SET stock = stock + ? WHERE id = ?",
        (quantity, product_id),
    )


def delete_product(product_id):
    database.run_change("DELETE FROM products WHERE id = ?", (product_id,))


def get_total_stock():
    rows = database.run_query("SELECT COALESCE(SUM(stock), 0) AS total FROM products")
    return rows[0]["total"]