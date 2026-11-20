import datetime

from data import queries
from logic import checks, user_logic

LOW_STOCK = 5


# products

def get_products(user):
    user_logic.check_permission(user, "stock")
    return queries.get_all_products()


def get_product(user, product_id):
    user_logic.check_permission(user, "stock")
    product = queries.get_product_by_id(product_id)
    if product is None:
        raise ValueError(f"There is no product with number {product_id}.")
    return product


def search_products(user, text):
    user_logic.check_permission(user, "stock")
    return queries.search_products(text)


def get_low_stock(user):
    products = get_products(user)
    return [product for product in products if product["stock"] <= LOW_STOCK]


def add_product(user, name, cost_price, selling_price, stock):
    user_logic.check_permission(user, "products")
    if queries.get_product_by_name(name) is not None:
        raise ValueError(f"A product called {name} already exists.")
    return queries.add_product(name, cost_price, selling_price, stock)


def update_product(user, product_id, name, cost_price, selling_price, stock):
    user_logic.check_permission(user, "products")
    get_product(user, product_id)
    other = queries.get_product_by_name(name)
    if other is not None and other["id"] != product_id:
        raise ValueError(f"Another product is already called {name}.")
    queries.update_product(product_id, name, cost_price, selling_price, stock)


def add_stock(user, product_id, quantity):
    user_logic.check_permission(user, "products")
    product = get_product(user, product_id)
    queries.add_stock(product_id, quantity)
    return product["stock"] + quantity


def delete_product(user, product_id):
    user_logic.check_permission(user, "products")
    get_product(user, product_id)
    if queries.count_sales_for_product(product_id) > 0:
        raise ValueError("This product has sales records, so it cannot be deleted. "
                         "You can change its stock to 0 instead.")
    queries.delete_product(product_id)


# sales

def record_sale(user, product_id, quantity, sale_date):
    user_logic.check_permission(user, "record_sale")
    # a helper can only record sales for today
    if not user_logic.has_permission(user, "choose_date"):
        sale_date = checks.today()
    product = queries.get_product_by_id(product_id)
    if product is None:
        raise ValueError(f"There is no product with number {product_id}.")
    if quantity > product["stock"]:
        raise ValueError(f"Only {product['stock']} of {product['name']} left in stock.")
    queries.add_sale(product_id, quantity, product["cost_price"],
                     product["selling_price"], sale_date, user["id"])
    return {
        "name": product["name"],
        "total": quantity * product["selling_price"],
        "stock_left": product["stock"] - quantity,
    }


def get_sales(user):
    user_logic.check_permission(user, "view_sales")
    return queries.get_all_sales()


def cancel_sale(user, sale_id):
    user_logic.check_permission(user, "cancel_sale")
    if queries.get_sale_by_id(sale_id) is None:
        raise ValueError(f"There is no sale with number {sale_id}.")
    queries.cancel_sale(sale_id)


# expenses

def add_expense(user, description, amount, expense_date):
    user_logic.check_permission(user, "expenses")
    return queries.add_expense(description, amount, expense_date, user["id"])


def get_expenses(user):
    user_logic.check_permission(user, "expenses")
    return queries.get_all_expenses()


def get_expense(user, expense_id):
    user_logic.check_permission(user, "expenses")
    expense = queries.get_expense_by_id(expense_id)
    if expense is None:
        raise ValueError(f"There is no expense with number {expense_id}.")
    return expense


def update_expense(user, expense_id, description, amount, expense_date):
    get_expense(user, expense_id)
    queries.update_expense(expense_id, description, amount, expense_date)


def delete_expense(user, expense_id):
    get_expense(user, expense_id)
    queries.delete_expense(expense_id)


# business summary

def get_dates(period):
    today = datetime.date.today()
    if period == "today":
        start = today
    elif period == "week":
        start = today - datetime.timedelta(days=6)
    else:
        # all time
        return "0000-01-01", "9999-12-31"
    return start.isoformat(), today.isoformat()


def get_summary(user, start_date, end_date):
    user_logic.check_permission(user, "summary")
    if start_date > end_date:
        raise ValueError("The start date must come before the end date.")

    sales = queries.get_sale_totals(start_date, end_date)
    expenses = queries.get_expense_total(start_date, end_date)

    revenue = sales["revenue"]
    cogs = sales["cogs"]
    net_profit = revenue - cogs - expenses

    by_product = []
    for row in queries.get_sale_totals_by_product(start_date, end_date):
        by_product.append({
            "product": row["product"],
            "units": row["units"],
            "profit": row["revenue"] - row["cogs"],
        })
    # best selling profit first
    by_product = sorted(by_product, key=lambda item: item["profit"], reverse=True)

    return {
        "revenue": revenue,
        "cogs": cogs,
        "expenses": expenses,
        "net_profit": net_profit,
        "units_sold": sales["units"],
        "remaining_stock": queries.get_total_stock(),
        "by_product": by_product,
    }
