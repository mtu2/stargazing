from blessed import Terminal
from stargazing import Stargazing

def main():
    """Main entry point for script"""

    term = Terminal()
    stargazing = Stargazing(term)
    stargazing.start()


if __name__ == "__main__":
    main()
