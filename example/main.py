import time
from webcface import Client, Arg, view


class A:
    def __init__(self):
        self.x = 1
        self.y = 2

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "nest": {"a": 3, "b": 4}}


def main():
    wcli = Client("example_main")
    wcli.value("test").set(0)
    # wcli.value("dict").set(A().to_dict())

    def hello() -> None:
        print("hello, world!")

    wcli.func("func1").set(hello)

    @wcli.func(
        args=[Arg(min=0, max=10), Arg(), Arg(), Arg(option=["hoge", "fuga", "piyo"])]
    )
    def func2(a: int, b: float, c: bool, d: str) -> float:
        print(f"hello2 a={a},b={b},c={c},d={d}")
        return a + b

    i = 0
    while True:
        time.sleep(0.1)
        wcli.value("test").set(i)
        wcli.text("str").set("hello")

        v = wcli.view("a")
        v.add(f"hello, world\n{i}\n")
        v.add(view.button("a", lambda: print("hello")))
        v.sync()

        # a =

        i += 1
        wcli.sync()


if __name__ == "__main__":
    main()
