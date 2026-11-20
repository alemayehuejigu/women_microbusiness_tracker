import datetime

ROLES = ["owner", "helper"]

# money and quantities stay below this so the numbers never get too big
BIGGEST_NUMBER = 100000000


def check_name(text):
    text = text.strip()
    if text == "":
        raise ValueError("This cannot be empty.")
    if len(text) > 25:
        raise ValueError("Please use 25 letters or fewer.")
    return text


def check_description(text):
    text = text.strip()
    if text == "":
        raise ValueError("This cannot be empty.")
    if len(text) > 40:
        raise ValueError("Please use 40 letters or fewer.")
    return text


def check_whole_number(text):
    text = text.strip().replace(",", "")
    try:
        number = int(text)
    except ValueError:
        raise ValueError("Please enter a whole number, for example 1500.")
    if number < 0:
        raise ValueError("The number cannot be negative.")
    if number > BIGGEST_NUMBER:
        raise ValueError("That number is too big.")
    return number


def check_positive_number(text):
    number = check_whole_number(text)
    if number == 0:
        raise ValueError("The number must be more than zero.")
    return number


def check_date(text):
    try:
        date = datetime.datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Please write the date like 2026-10-28.")
    if date > datetime.date.today():
        raise ValueError("The date cannot be in the future.")
    return date.isoformat()


def check_pin(text):
    text = text.strip()
    if len(text) != 4 or not text.isdigit():
        raise ValueError("The PIN must be 4 digits.")
    return text


def check_role(text):
    text = text.strip().lower()
    if text not in ROLES:
        raise ValueError("Please type owner or helper.")
    return text


def today():
    return datetime.date.today().isoformat()
