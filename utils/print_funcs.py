import math

from typing import List
from blessed import Terminal


def print_xy(term: Terminal, x: int, y: int, *values: str, sep="", end=""):
    with term.location(x, y):
        print(*values, sep=sep, end=end, flush=True)


def print_lines_xy(term: Terminal, x: int, y: int, lines: List[str], max_width: int = None):
    for i, line in enumerate(lines):
        if max_width is not None:
            empty = " " * max(max_width - term.length(line), 0)
            print_xy(term, x, y + i, f" {line}{empty} ")
        else:
            print_xy(term, x, y + i, line)
