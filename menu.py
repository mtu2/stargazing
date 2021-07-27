from typing import Callable


class Menu():

    def __init__(self, hover_dec: Callable[[str], str] = None) -> None:
        self.menu_item_texts = {}
        self.menu_item_callbacks = {}
        self.menu_item_count = 0

        self.menu_rows = []
        self.hover_row = 0

        self.hover_dec = hover_dec
        if hover_dec is None:
            self.hover_dec = lambda: None

    def add_item(self, text: str, handle_select: Callable[[], None] = None) -> None:
        if handle_select is None:
            def handle_select(): return None

        self.menu_item_texts[self.menu_item_count] = text
        self.menu_item_callbacks[self.menu_item_count] = handle_select
        self.menu_rows.append(self.menu_item_count)
        self.menu_item_count += 1

    def add_blank_row(self) -> None:
        self.menu_rows.append(-1)

    def hover_up(self) -> None:
        self.hover_row = max(self.hover_row - 1, 0)

    def hover_down(self) -> None:
        self.hover_row = min(self.hover_row + 1, self.menu_item_count-1)

    def set_hover(self, num: int) -> None:
        if num < 0 or num >= self.menu_item_count:
            raise Exception("Hover row out of range")
        self.hover_row = num

    def select(self) -> None:
        key = self.menu_rows[self.hover_row]
        if key == -1:
            return
        self.menu_item_callbacks[key]()

    def get_print_rows(self) -> str:
        print_rows = []

        for key in self.menu_rows:
            if key == -1:
                print_rows.append("")
            elif key == self.hover_row and self.hover_dec:
                print_rows.append(self.hover_dec(
                    self.menu_item_texts[key]))
            else:
                print_rows.append(self.menu_item_texts[key])

        return print_rows
