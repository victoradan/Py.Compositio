from dataclasses import dataclass
from typing import Callable, Literal


@dataclass(eq=True, frozen=True)
class Maybe[T]:
    val: tuple[Literal["Just"], T] | Literal["Nothing"]

    def map[B](self, f: Callable[[T], B]) -> "Maybe[B]":
        match self.val:
            case ("Just", v):
                return Maybe(("Just", f(v)))
            case "Nothing":
                return Maybe("Nothing")

    __rtruediv__ = map

    def bind[B](self, f: Callable[[T], "Maybe[B]"]) -> "Maybe[B]":
        match self.val:
            case ("Just", v):
                return f(v)
            case "Nothing":
                return Maybe("Nothing")

    __rshift__ = bind

    def maybe[B](self, nothing: B, otherwise: Callable[[T], B]) -> B:
        match self.val:
            case ("Just", v):
                return otherwise(v)
            case "Nothing":
                return nothing


def just[T](val: T) -> Maybe[T]:
    return Maybe(("Just", val))


def nothing():
    return Maybe("Nothing")


def from_optional[T](val: T | None) -> Maybe[T]:
    return just(val) if val is not None else nothing()


def maybe_none[I, O](none: O, otherwise: Callable[[I], O], val: I | None) -> O:
    return none if val is None else otherwise(val)
