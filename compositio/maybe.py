from dataclasses import dataclass
from typing import Callable


@dataclass(eq=True, frozen=True)
class Maybe[T]:
    val: T | None

    def map[U](self, f: Callable[[T], U]):
        return Maybe(f(self.val) if self.val is not None else None)

    @staticmethod
    def maybe[I, O](none: Callable[[], O], otherwise: Callable[[I], O], val: I | None):
        return none() if val is None else otherwise(val)
