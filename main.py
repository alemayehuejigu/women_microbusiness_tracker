from data import database
from frontend import menu


def main():
    try:
        database.connect()
        database.create_tables()
        menu.run_app()
    except ValueError as error:
        print(error)
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye.")
    finally:
        database.close()


if __name__ == "__main__":
    main()
