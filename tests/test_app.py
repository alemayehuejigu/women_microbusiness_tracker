import os
import sys
import tempfile
import unittest

# lets the tests import the project folders when run from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import database
from logic import checks, shop_logic, user_logic


class TrackerTests(unittest.TestCase):

    def setUp(self):
        # every test gets a fresh empty database
        self.folder = tempfile.TemporaryDirectory()
        database.DB_FILE = os.path.join(self.folder.name, "test.db")
        database.connect()
        database.create_tables()
        user_logic.create_first_owner("Amina", "1234")
        self.owner = user_logic.login("Amina", "1234")
        user_logic.add_user(self.owner, "Grace", "4321", "helper")
        self.helper = user_logic.login("Grace", "4321")

    def tearDown(self):
        database.close()
        self.folder.cleanup()

    def add_soap(self):
        return shop_logic.add_product(self.owner, "Soap", 1000, 1500, 20)

    # users and roles
    def test_login_works_and_wrong_pin_fails(self):
        self.assertEqual(self.owner["role"], "owner")
        with self.assertRaises(ValueError):
            user_logic.login("Amina", "0000")
        with self.assertRaises(ValueError):
            user_logic.login("Nobody", "1234")

    def test_login_name_ignores_capital_letters(self):
        user = user_logic.login("amina", "1234")
        self.assertEqual(user["name"], "Amina")

    def test_pin_is_not_saved_as_plain_text(self):
        rows = database.run_query("SELECT pin_hash FROM users")
        for row in rows:
            self.assertNotIn("1234", row["pin_hash"])
            self.assertNotIn("4321", row["pin_hash"])

    def test_helper_is_blocked_from_owner_actions(self):
        product_id = self.add_soap()
        with self.assertRaises(ValueError):
            shop_logic.add_product(self.helper, "Rice", 500, 700, 10)
        with self.assertRaises(ValueError):
            shop_logic.delete_product(self.helper, product_id)
        with self.assertRaises(ValueError):
            shop_logic.add_expense(self.helper, "Transport", 500, checks.today())
        with self.assertRaises(ValueError):
            shop_logic.get_summary(self.helper, "0000-01-01", "9999-12-31")
        with self.assertRaises(ValueError):
            shop_logic.get_sales(self.helper)
        with self.assertRaises(ValueError):
            user_logic.add_user(self.helper, "Eve", "1111", "owner")

    def test_helper_can_sell_and_view_stock(self):
        product_id = self.add_soap()
        self.assertEqual(len(shop_logic.get_products(self.helper)), 1)
        result = shop_logic.record_sale(self.helper, product_id, 2, "2020-01-01")
        self.assertEqual(result["stock_left"], 18)

    def test_helper_sale_is_always_dated_today(self):
        product_id = self.add_soap()
        shop_logic.record_sale(self.helper, product_id, 1, "2020-01-01")
        sales = shop_logic.get_sales(self.owner)
        self.assertEqual(sales[0]["sale_date"], checks.today())

    def test_user_rules(self):
        with self.assertRaises(ValueError):
            user_logic.add_user(self.owner, "grace", "1111", "helper")
        with self.assertRaises(ValueError):
            user_logic.add_user(self.owner, "Eve", "1111", "boss")
        with self.assertRaises(ValueError):
            user_logic.delete_user(self.owner, self.owner["id"])
        with self.assertRaises(ValueError):
            user_logic.create_first_owner("Second", "1111")

    def test_reset_pin_and_delete_user(self):
        user_logic.reset_pin(self.owner, self.helper["id"], "9999")
        with self.assertRaises(ValueError):
            user_logic.login("Grace", "4321")
        user_logic.login("Grace", "9999")
        user_logic.delete_user(self.owner, self.helper["id"])
        self.assertEqual(len(user_logic.get_users(self.owner)), 1)

    def test_sales_stay_when_the_seller_is_deleted(self):
        product_id = self.add_soap()
        shop_logic.record_sale(self.helper, product_id, 2, checks.today())
        user_logic.delete_user(self.owner, self.helper["id"])
        sales = shop_logic.get_sales(self.owner)
        self.assertEqual(len(sales), 1)
        self.assertIsNone(sales[0]["sold_by"])

    # products
    def test_product_crud(self):
        product_id = self.add_soap()
        product = shop_logic.get_product(self.owner, product_id)
        self.assertEqual(product["name"], "Soap")

        shop_logic.update_product(self.owner, product_id, "Big Soap", 1100, 1600, 15)
        product = shop_logic.get_product(self.owner, product_id)
        self.assertEqual((product["name"], product["cost_price"], product["selling_price"], product["stock"]),
                         ("Big Soap", 1100, 1600, 15))

        self.assertEqual(shop_logic.add_stock(self.owner, product_id, 5), 20)
        self.assertEqual(len(shop_logic.search_products(self.owner, "soap")), 1)
        self.assertEqual(len(shop_logic.search_products(self.owner, "rice")), 0)

        shop_logic.delete_product(self.owner, product_id)
        self.assertEqual(len(shop_logic.get_products(self.owner)), 0)

    def test_duplicate_product_names_are_refused(self):
        self.add_soap()
        with self.assertRaises(ValueError):
            shop_logic.add_product(self.owner, "soap", 1, 2, 3)
        other_id = shop_logic.add_product(self.owner, "Rice", 500, 700, 10)
        with self.assertRaises(ValueError):
            shop_logic.update_product(self.owner, other_id, "SOAP", 500, 700, 10)

    def test_bad_product_values_are_refused(self):
        with self.assertRaises(ValueError):
            shop_logic.add_product(self.owner, "Free", 100, 0, 5)
        with self.assertRaises(ValueError):
            shop_logic.add_product(self.owner, "Minus", -5, 100, 5)
        with self.assertRaises(ValueError):
            shop_logic.get_product(self.owner, 999)

    def test_product_with_sales_cannot_be_deleted(self):
        product_id = self.add_soap()
        shop_logic.record_sale(self.owner, product_id, 1, checks.today())
        with self.assertRaises(ValueError):
            shop_logic.delete_product(self.owner, product_id)

    def test_low_stock_list(self):
        self.add_soap()
        shop_logic.add_product(self.owner, "Salt", 100, 150, 3)
        low = shop_logic.get_low_stock(self.owner)
        self.assertEqual([product["name"] for product in low], ["Salt"])

    # sales
    def test_sale_lowers_stock_and_cancel_puts_it_back(self):
        product_id = self.add_soap()
        result = shop_logic.record_sale(self.owner, product_id, 5, checks.today())
        self.assertEqual(result["total"], 7500)
        self.assertEqual(result["stock_left"], 15)
        self.assertEqual(shop_logic.get_product(self.owner, product_id)["stock"], 15)

        sale_id = shop_logic.get_sales(self.owner)[0]["id"]
        shop_logic.cancel_sale(self.owner, sale_id)
        self.assertEqual(shop_logic.get_product(self.owner, product_id)["stock"], 20)
        self.assertEqual(len(shop_logic.get_sales(self.owner)), 0)

    def test_cannot_sell_more_than_stock(self):
        product_id = self.add_soap()
        with self.assertRaises(ValueError):
            shop_logic.record_sale(self.owner, product_id, 21, checks.today())
        self.assertEqual(shop_logic.get_product(self.owner, product_id)["stock"], 20)
        self.assertEqual(len(shop_logic.get_sales(self.owner)), 0)

    def test_sale_of_missing_product_or_sale(self):
        with self.assertRaises(ValueError):
            shop_logic.record_sale(self.owner, 999, 1, checks.today())
        with self.assertRaises(ValueError):
            shop_logic.cancel_sale(self.owner, 999)

    def test_old_sales_keep_their_prices(self):
        product_id = self.add_soap()
        shop_logic.record_sale(self.owner, product_id, 5, checks.today())
        shop_logic.update_product(self.owner, product_id, "Soap", 2000, 3000, 15)
        summary = shop_logic.get_summary(self.owner, "0000-01-01", "9999-12-31")
        self.assertEqual(summary["revenue"], 7500)
        self.assertEqual(summary["cogs"], 5000)

    # expenses
    def test_expense_crud(self):
        expense_id = shop_logic.add_expense(self.owner, "Transport", 500, checks.today())
        expense = shop_logic.get_expense(self.owner, expense_id)
        self.assertEqual(expense["amount"], 500)

        shop_logic.update_expense(self.owner, expense_id, "Taxi", 800, "2026-10-27")
        expense = shop_logic.get_expense(self.owner, expense_id)
        self.assertEqual((expense["description"], expense["amount"], expense["expense_date"]),
                         ("Taxi", 800, "2026-10-27"))

        self.assertEqual(len(shop_logic.get_expenses(self.owner)), 1)
        shop_logic.delete_expense(self.owner, expense_id)
        self.assertEqual(len(shop_logic.get_expenses(self.owner)), 0)
        with self.assertRaises(ValueError):
            shop_logic.get_expense(self.owner, expense_id)

    # summary: the sample numbers from the blueprint
    def test_summary_matches_the_blueprint_example(self):
        product_id = self.add_soap()
        shop_logic.record_sale(self.owner, product_id, 5, checks.today())
        shop_logic.add_expense(self.owner, "Transport", 500, checks.today())
        start, end = shop_logic.get_dates("all")
        summary = shop_logic.get_summary(self.owner, start, end)
        self.assertEqual(summary["revenue"], 7500)
        self.assertEqual(summary["cogs"], 5000)
        self.assertEqual(summary["expenses"], 500)
        self.assertEqual(summary["net_profit"], 2000)
        self.assertEqual(summary["units_sold"], 5)
        self.assertEqual(summary["remaining_stock"], 15)
        self.assertEqual(summary["by_product"][0]["profit"], 2500)

    def test_summary_periods(self):
        product_id = self.add_soap()
        shop_logic.record_sale(self.owner, product_id, 2, "2026-01-10")
        shop_logic.record_sale(self.owner, product_id, 3, checks.today())
        start, end = shop_logic.get_dates("today")
        self.assertEqual(shop_logic.get_summary(self.owner, start, end)["units_sold"], 3)
        start, end = shop_logic.get_dates("all")
        self.assertEqual(shop_logic.get_summary(self.owner, start, end)["units_sold"], 5)
        self.assertEqual(shop_logic.get_summary(self.owner, "2026-01-01", "2026-01-31")["units_sold"], 2)
        with self.assertRaises(ValueError):
            shop_logic.get_summary(self.owner, "2026-02-01", "2026-01-01")

    def test_loss_shows_as_negative_profit(self):
        shop_logic.add_expense(self.owner, "Rent", 3000, checks.today())
        summary = shop_logic.get_summary(self.owner, "0000-01-01", "9999-12-31")
        self.assertEqual(summary["net_profit"], -3000)
        self.assertEqual(summary["by_product"], [])

    # input checks
    def test_number_checks(self):
        self.assertEqual(checks.check_whole_number("1,500"), 1500)
        self.assertEqual(checks.check_whole_number(" 0 "), 0)
        for bad in ["abc", "", "-5", "2.5", "999999999999999999999"]:
            with self.assertRaises(ValueError):
                checks.check_whole_number(bad)
        with self.assertRaises(ValueError):
            checks.check_positive_number("0")

    def test_date_checks(self):
        self.assertEqual(checks.check_date("2026-1-5"), "2026-01-05")
        for bad in ["28/10/2026", "yesterday", "2026-13-01", "2999-01-01"]:
            with self.assertRaises(ValueError):
                checks.check_date(bad)

    def test_text_pin_and_role_checks(self):
        with self.assertRaises(ValueError):
            checks.check_name("   ")
        with self.assertRaises(ValueError):
            checks.check_name("x" * 26)
        with self.assertRaises(ValueError):
            checks.check_pin("12a4")
        with self.assertRaises(ValueError):
            checks.check_pin("123")
        self.assertEqual(checks.check_role(" Owner "), "owner")
        with self.assertRaises(ValueError):
            checks.check_role("boss")

    # database
    def test_database_rules_block_bad_rows(self):
        with self.assertRaises(ValueError):
            database.run_change("INSERT INTO products (name, cost_price, selling_price, stock) "
                                "VALUES ('Bad', 1, 2, -1)")
        with self.assertRaises(ValueError):
            database.run_change("INSERT INTO sales (product_id, quantity, cost_price, selling_price, sale_date) "
                                "VALUES (999, 1, 1, 2, '2026-10-28')")


if __name__ == "__main__":
    unittest.main()
