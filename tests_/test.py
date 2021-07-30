replacement = {
    12288: " ",
    12290: "°",
    65439: "°°°°°",
    7506:  "*",
    65294: ".",
    65291: "+",
    65359: "*",
    9734:  "*",
}


with open("res/new_stars.txt", "r") as f:
    with open("res/test_output.txt", "w") as w:
        lines = f.readlines()
        for line in lines:
            for c in line:
                o = ord(c)

                if o not in replacement:
                    print(c, ord(c))

                w.write(replacement[o] if o in replacement else c)
