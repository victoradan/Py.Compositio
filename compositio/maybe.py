from dataclasses import dataclass
from typing import Callable, Literal, Sequence

import compositio.combinators as C


@dataclass(eq=True, frozen=True)
class Maybe[T]:
    val: tuple[Literal["Just"], T] | None

    def map[B](self, f: Callable[[T], B]) -> "Maybe[B]":
        match self.val:
            case ("Just", v):
                return just(f(v))
            case None:
                return nothing()

    __rtruediv__ = map

    def apply[B](self, f: "Maybe[Callable[[T], B]]") -> "Maybe[B]":
        match self.val, f.val:
            case ("Just", v), ("Just", vf):
                return just(vf(v))
            case _, _:
                return nothing()

    # __rmod__ = apply  # TODO not working (TypeError at runtime... why?)

    def bind[B](self, f: Callable[[T], "Maybe[B]"]) -> "Maybe[B]":
        match self.val:
            case ("Just", v):
                return f(v)
            case None:
                return nothing()

    __matmul__ = bind

    def maybe[B](self, nothing: B, f: Callable[[T], B]) -> B:
        match self.val:
            case ("Just", v):
                return f(v)
            case None:
                return nothing

    def is_just(self) -> bool:
        return self.maybe(False, C.const(True))

    def value_or(self, nothing: T) -> T:
        """Returns the `nothing` value if `Nothing`, else the Just value"""
        return self.maybe(nothing, C.i)


def both[A, B](a: Maybe[A], b: Maybe[B]) -> Maybe[tuple[A, B]]:
    match a.val, b.val:
        case ("Just", v1), ("Just", v2):
            return just((v1, v2))
        case _, _:
            return nothing()


def just[T](val: T) -> Maybe[T]:
    return Maybe(("Just", val))


def nothing():
    return Maybe(None)


def from_optional[T](val: T | None) -> Maybe[T]:
    return just(val) if val is not None else nothing()


def maybe_none[I, O](none: O, f: Callable[[I], O], val: I | None) -> O:
    return none if val is None else f(val)


def map_maybe[A, B](f: Callable[[A], Maybe[B]], ls: Sequence[A]) -> list[B]:
    """A map that throws out elements for which `f` returns `Nothing`."""
    result: list[B] = []
    for l in ls:
        match f(l).val:
            case ("Just", v):
                result.append(v)
            case None:
                pass
    return result


def cat_maybes[A](ls: Sequence[Maybe[A]]) -> list[A]:
    """Takes a list of `Maybe`s and returns a list of all the Just values."""
    return map_maybe(C.i, ls)


def traverse[A, B](f: Callable[[A], Maybe[B]], seq: Sequence[A]) -> Maybe[Sequence[B]]:
    result: list[B] = []
    for x in seq:
        mb = f(x)
        match mb.val:
            case None:
                return nothing()
            case ("Just", v):
                result.append(v)
    return just(result)


def sequence[A](lst: Sequence[Maybe[A]]) -> Maybe[Sequence[A]]:
    return traverse(C.i, lst)
