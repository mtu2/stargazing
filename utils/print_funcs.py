import math

from typing import List
from blessed import Terminal


def print_xy(term: Terminal, x: int, y: int, value: str, flush=True, max_width: int = None, center=False):
    if max_width is not None:
        empty_len = max(max_width - term.length(value), 0)

        if center:
            empty = " " * (empty_len // 2)
            print(term.move_xy(x - max_width // 2, y) +
                  f" {empty}{value}{empty} ", end="", flush=flush)
        else:
            empty = " " * empty_len
            print(term.move_xy(x, y) +
                  f" {value}{empty} ", end="", flush=flush)
    else:
        print(term.move_xy(x, y) + value, end="", flush=flush)


def print_lines_xy(term: Terminal, x: int, y: int, lines: List[str], flush=True, max_width: int = None, center=False):
    for i, line in enumerate(lines):
        print_xy(term, x, y + i, line, flush, max_width, center)
