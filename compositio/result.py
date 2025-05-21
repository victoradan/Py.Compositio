from dataclasses import dataclass
from typing import Callable, Literal

import compositio.combinators as Comb


@dataclass
class Result[O, E]:
    _val: tuple[Literal["Ok"], O] | tuple[Literal["Err"], E]

    def map[T](self, f: Callable[[O], T]) -> "Result[T,E]":
        match self._val:
            case "Ok", v:
                return Result(("Ok", f(v)))
            case "Err", v:
                return Result(("Err", v))

    __truediv__ = map

    def bimap[O2, E2](self, f: Callable[[O], O2], g: Callable[[E], E2]) -> "Result[O2, E2]":
        match self._val:
            case "Ok", v:
                return Result(("Ok", f(v)))
            case "Err", v:
                return Result(("Err", g(v)))

    def __floordiv__[O2, E2](self, fg: tuple[Callable[[O], O2], Callable[[E], E2]]) -> "Result[O2, E2]":
        return self.bimap(fg[0], fg[1])

    def bind[T](self, f: Callable[[O], "Result[T, E]"]) -> "Result[T, E]":
        match self._val:
            case "Ok", v:
                return f(v)
            case "Err", v:
                return Result(("Err", v))

    def __rshift__[T](self, other: Callable[[O], "Result[T, E]"]):
        return self.bind(other)

    def either[R](self, onsuccess: Callable[[O], R], onfailure: Callable[[E], R]) -> R:
        match self._val:
            case "Ok", v:
                return onsuccess(v)
            case "Err", v:
                return onfailure(v)


def ok[S, F](v: S):
    return Result[S, F](("Ok", v))


def err[S, F](v: F):
    return Result[S, F](("Err", v))
