from typing import List
from blessed import Terminal
import math


def print_xy(term: Terminal, x: int, y: int, value: str, flush=True, max_width: int = None,
             center=False, trim=False):
    """trim and center both require max_width to be given"""
    if max_width is not None:
        empty_len = max(max_width - term.length(value), 0)

        if trim and term.length(value) > max_width:
            length = term.length(value)
            eles = term.split_seqs(value)[::-1]
            dot_count = 0

            for i, ele in enumerate(eles):
                # Skip if element is a sequence
                if len(term.strip_seqs(ele)) == 0:
                    continue

                if length > max_width:
                    eles[i] = ""
                    length -= 1
                else:
                    eles[i] = "."
                    dot_count += 1

                    if dot_count == 2:
                        break

            value = "".join(eles[::-1])

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


def print_lines_xy(term: Terminal, x: int, y: int, lines: List[str], flush=True, max_width: int = None,
                   center=False, trim=False):
    for i, line in enumerate(lines):
        print_xy(term, x, y + i, line, flush, max_width, center, trim)
