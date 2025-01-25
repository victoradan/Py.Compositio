from dataclasses import dataclass
from typing import Callable


@dataclass(eq=True, frozen=True)
class Writer[A, W]:
    val: A
    con: list[W]

    def map[B](self, f: Callable[[A], B]):
        return Writer(f(self.val), self.con)

    @staticmethod
    def pure[T](val: A):
        con: list[T] = []
        return Writer(val, con)

    def bind[B](self, f: Callable[[A], "Writer[B, W]"]):
        r = f(self.val)
        return Writer(r.val, self.con + r.con)

    def __rshift__[B](self, other: Callable[[A], "Writer[B, W]"]):
        return self.bind(other)


def write[T, W](val: T, con: W):
    return Writer(val, [con])


if __name__ == "__main__":
    w1 = Writer(1, ["one"])

    def addone(x):
        return write(x + 1, "added one")

    r = Writer.pure(1).bind(addone)
    print(r)
    r = w1 >> addone >> addone
    print(r)
