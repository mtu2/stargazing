from blessed import Terminal

term = Terminal()

with term.location():
    print(term.move_xy(1, 1) + 'Hi Mom!' + term.clear_eol)
