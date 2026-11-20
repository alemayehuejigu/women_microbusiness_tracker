import getpass

from logic import checks


# keeps asking until the check function accepts the answer
# if a default is given, pressing Enter returns the default
def ask(prompt, check, default=None, hidden=False):
    while True:
        if hidden:
            text = getpass.getpass(prompt)
        else:
            text = input(prompt)
        if text.strip() == "" and default is not None:
            return default
        try:
            return check(text)
        except ValueError as error:
            print(error)


def ask_yes(question):
    answer = input(question + " (y/n): ").strip().lower()
    return answer in ["y", "yes"]


def ask_new_pin():
    while True:
        pin = ask("New 4-digit PIN: ", checks.check_pin, hidden=True)
        again = getpass.getpass("Type the PIN again: ")
        if again.strip() == pin:
            return pin
        print("The two PINs are not the same. Try again.")
