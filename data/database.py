import os
import sqlite3

# the database file is kept next to main.py
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tracker.db")

connection = None

# sales keep their own copy of the prices, so old sales do not change
# when the product price is edited later
SCHEMA = """
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    pin_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles (id)
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    cost_price INTEGER NOT NULL CHECK (cost_price >= 0),
    selling_price INTEGER NOT NULL CHECK (selling_price > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    cost_price INTEGER NOT NULL,
    selling_price INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (product_id) REFERENCES products (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0),
    expense_date TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON sales (sale_date);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses (expense_date);

INSERT OR IGNORE INTO roles (name) VALUES ('owner'), ('helper');
"""


def connect():
    global connection
    try:
        connection = sqlite3.connect(DB_FILE)
        connection.row_factory = sqlite3.Row
        # sqlite only checks foreign keys when this is switched on
        connection.execute("PRAGMA foreign_keys = ON")
    except sqlite3.Error:
        raise ValueError("Could not open the database file.")


def create_tables():
    try:
        connection.executescript(SCHEMA)
    except sqlite3.Error:
        raise ValueError("Could not create the database tables.")


def close():
    global connection
    if connection is not None:
        connection.close()
        connection = None


def run_query(sql, values=()):
    try:
        cursor = connection.execute(sql, values)
        return cursor.fetchall()
    except sqlite3.Error:
        raise ValueError("Could not read from the database. Please try again.")


def run_change(sql, values=()):
    try:
        cursor = connection.execute(sql, values)
        connection.commit()
        return cursor
    except sqlite3.Error:
        connection.rollback()
        raise ValueError("Could not save the change. Please check the values and try again.")
