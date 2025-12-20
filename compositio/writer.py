from dataclasses import dataclass
from typing import Callable


@dataclass(eq=True, frozen=True)
class Writer[A, W]:
    val: A
    con: list[W]

    def map[B](self, f: Callable[[A], B]):
        return Writer(f(self.val), self.con)

    __rtruediv__ = map

    @classmethod
    def pure(cls, val: A):
        return cls(val, [])

    def bind[B](self, f: Callable[[A], "Writer[B, W]"]) -> "Writer[B, W]":
        r = f(self.val)
        return Writer(val=f(self.val).val, con=self.con + r.con)

    __matmul__ = bind

    def run(self):
        return (self.val, self.con)


def write[T, W](val: T, con: W) -> Writer[T, W]:
    return Writer(val, [con])
