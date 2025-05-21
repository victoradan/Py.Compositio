from dataclasses import dataclass
from typing import Callable, Literal


@dataclass(eq=True, frozen=True)
class Maybe[T]:
    _val: tuple[Literal["Just"], T] | Literal["Nothing"]

    def map[U](self, f: Callable[[T], U]) -> "Maybe[U]":
        match self._val:
            case ("Just", v):
                return Maybe(("Just", f(v)))
            case "Nothing":
                return Maybe("Nothing")

    def maybe[B](self, nothing: B, otherwise: Callable[[T], B]) -> B:
        match self._val:
            case ("Just", v):
                return otherwise(v)
            case "Nothing":
                return nothing


def just[T](val: T):  # pyright: ignore
    return Maybe(("Just", val))


def nothing():
    return Maybe("Nothing")


def maybe_none[I, O](none: O, otherwise: Callable[[I], O], val: I | None):
    return none if val is None else otherwise(val)
