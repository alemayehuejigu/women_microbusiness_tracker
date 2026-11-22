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