import re

dimensions_pattern = r"\d+(?:x\d+)+"


def reorder(stocks):
    standards = []
    prints = []
    enreds = []
    ss = list(stocks)
    for s in ss:
        print(f"inspecting {s}")
        if s.is_standard():
            standards.append(s)
        elif s.is_print():
            prints.append(s)
        elif s.is_enlargement():
            enreds.append(s)
        else:
            raise Exception("unable to classify the stock(?!)")
    return (standards, enreds, prints)
