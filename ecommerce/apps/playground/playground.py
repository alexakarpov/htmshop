from .foo import foo


def do_something():
    print("do_something calling foo")
    f=foo()
    print(f"foo returned {f}")
    return f