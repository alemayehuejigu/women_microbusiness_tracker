# Women's Microbusiness Tracker

A command-line app for small shop owners. It records products, sales and expenses
and works out the real profit. Everything is saved in a local SQLite database, so it
works without internet.

This is Part 2 of our Peer Learning Project. The idea and the plan are in our Part 1 blueprint.

## How to run

You need Python 3.8 or newer. Nothing else has to be installed.

```
python main.py
```

The first time you run it, the app asks you to create the owner account (a name and a 4-digit PIN).
The database file `tracker.db` is created next to `main.py`. It is not pushed to GitHub,
so everyone on the team has their own copy.

## Folders

```
main.py            starts the app
frontend/          what the user sees: menus, questions and printed tables
logic/             the rules: input checks, permissions, stock check, profit formulas
data/              everything that talks to SQLite
tests/             automatic tests
```

The data always moves in one direction:

```
frontend (screen)  ->  logic (rules)  ->  data (SQL)  ->  tracker.db
```

- A screen never writes SQL. A data file never prints anything.
- When something is wrong, the logic raises a `ValueError` with a message the user can read.
  The screen catches it and prints the message.
- Only `data/database.py` opens the database. `data/queries.py` uses its
  `run_query` and `run_change` functions, and its connection for the two sale changes
  that must be saved together.
- Each file below is divided into labelled sections (for example products, sales,
  expenses), so people can work on different sections of the same file.

| File | What it does |
| --- | --- |
| `main.py` | starts the app |
| `frontend/menu.py` | welcome banner, login, main menu and the manage users menu |
| `frontend/inputs.py` | asks a question again until the answer is valid |
| `frontend/shop_screens.py` | product, sales and expenses menus and tables, the stock view and the business summary |
| `logic/checks.py` | checks for names, numbers, dates, PINs and roles |
| `logic/user_logic.py` | login, roles and what each role may do |
| `logic/shop_logic.py` | product rules (no double names, no delete if sold), sale rules (enough stock, helper sells for today only), expense rules, the profit formulas and the date ranges |
| `data/database.py` | connection, table creation and the two query functions |
| `data/queries.py` | all the SQL: roles and users, products, sales (stock and sale are saved together) and expenses |
| `tests/test_app.py` | automatic tests |

## Database tables

| Table | Columns |
| --- | --- |
| `roles` | id, name (`owner` or `helper`) |
| `users` | id, name, pin_hash, role_id |
| `products` | id, name, cost_price, selling_price, stock |
| `sales` | id, product_id, quantity, cost_price, selling_price, sale_date, user_id |
| `expenses` | id, description, amount, expense_date, user_id |

- Money is saved as whole numbers in RWF.
- Dates are saved as text like `2026-10-28`.
- A sale keeps its own copy of the cost price and selling price. If a product price changes
  later, the old sales and the old profit do not change.
- PINs are saved as a hash, not as plain text.

## Roles

| Action | owner | helper |
| --- | --- | --- |
| Record a sale (today only for helper) | yes | yes |
| View products and stock | yes | yes |
| Add, update and delete products | yes | no |
| View and cancel sales | yes | no |
| Record, edit and delete expenses | yes | no |
| Business summary | yes | no |
| Manage users | yes | no |

The permissions are in one place, the `permissions` dictionary in `logic/user_logic.py`.

## Profit formulas

```
Revenue        = selling price x quantity, added up for every sale
COGS           = cost price x quantity, added up for every sale
Expenses       = all expenses added up
Net profit     = Revenue - COGS - Expenses
Remaining stock = the stock number saved for each product
```

Example: Soap costs 1,000 RWF and sells for 1,500 RWF. We start with 20 and sell 5.
Revenue is 7,500 RWF and COGS is 5,000 RWF. With 500 RWF of expenses the net profit is 2,000 RWF
and 15 soaps are left.

## Tests

```
python tests/test_app.py
```

The tests use a temporary database, so they never touch your real `tracker.db`.

## Limits

- The numbers are only as good as what the owner types in.
- The app runs in a terminal, so the owner needs a computer with Python.
- Money is in whole RWF only. Cents are not supported.
