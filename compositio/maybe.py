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

    def maybe[B](self, nothing: B, otherwise: Callable[[T], B]) -> B:
        match self.val:
            case ("Just", v):
                return otherwise(v)
            case None:
                return nothing


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


def maybe_none[I, O](none: O, otherwise: Callable[[I], O], val: I | None) -> O:
    return none if val is None else otherwise(val)


def map_maybe[A, B](f: Callable[[A], Maybe[B]], ls: Sequence[A]) -> Sequence[B]:
    """A map that throws out elements for which `f` returns Nothing."""

    def to_list[T](m: Maybe[T]) -> list[T]:
        return m.maybe([], lambda v: [v])

    return [r for x in ls for r in to_list(f(x))]


def cat_maybes[A](ls: Sequence[Maybe[A]]) -> Sequence[A]:
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
