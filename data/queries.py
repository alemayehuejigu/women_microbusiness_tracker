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

