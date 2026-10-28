from dataclasses import dataclass
from typing import Callable, Literal, Iterable

import compositio.combinators as C


@dataclass
class Result[O, E]:
    val: tuple[Literal["Ok"], O] | tuple[Literal["Err"], E]

    def map[T](self, f: Callable[[O], T]) -> "Result[T,E]":
        match self.val:
            case "Ok", v:
                return Result(("Ok", f(v)))
            case "Err", v:
                return Result(("Err", v))

    __rtruediv__ = map

    def bimap[O2, E2](self, f: Callable[[O], O2], g: Callable[[E], E2]) -> "Result[O2, E2]":
        match self.val:
            case "Ok", v:
                return Result(("Ok", f(v)))
            case "Err", v:
                return Result(("Err", g(v)))

    def __rfloordiv__[O2, E2](self, fg: tuple[Callable[[O], O2], Callable[[E], E2]]) -> "Result[O2, E2]":
        return self.bimap(fg[0], fg[1])

    def bind[T](self, f: Callable[[O], "Result[T, E]"]) -> "Result[T, E]":
        match self.val:
            case "Ok", v:
                return f(v)
            case "Err", v:
                return Result(("Err", v))

    __matmul__ = bind

    def either[R](self, onsuccess: Callable[[O], R], onfailure: Callable[[E], R]) -> R:
        match self.val:
            case "Ok", v:
                return onsuccess(v)
            case "Err", v:
                return onfailure(v)

    def is_ok(self) -> bool:
        return self.either(C.const(True), C.const(False))

    def from_ok(self, default: O) -> O:
        """Return the contents of an Ok-value or a default value otherwise."""
        return self.either(C.i, C.const(default))

    def from_err(self, default: E) -> E:
        """Return the contents of an Err-value or a default value otherwise."""
        return self.either(C.const(default), C.i)


def ok[O, E](v: O):  # pyright: ignore
    return Result[O, E](("Ok", v))


def err[O, E](v: E):  # pyright: ignore
    return Result[O, E](("Err", v))


def oks[O, E](rs: Iterable[Result[O, E]]) -> list[O]:
    """Extracts from a list of `Result` all the Ok elements, in order."""
    return partition_results(rs)[0]


def errs[O, E](rs: Iterable[Result[O, E]]) -> list[E]:
    """Extracts from a list of `Result` all the Err elements, in order."""
    return partition_results(rs)[1]


def partition_results[O, E](rs: Iterable[Result[O, E]]) -> tuple[list[O], list[E]]:
    """Partitions a list of `Result` into a tuple of two lists: the first containing all the Ok values, and the second containing all the Err values."""
    oks: list[O] = []
    errs: list[E] = []
    for r in rs:
        match r.val:
            case "Ok", v:
                oks.append(v)
            case "Err", v:
                errs.append(v)
    return (oks, errs)


def sequence[O, E](seq: Iterable[Result[O, E]]) -> Result[Iterable[O], E]:
    result: list[O] = []
    for item in seq:
        match item.val:
            case "Ok", v:
                result.append(v)
            case "Err", v:
                return err(v)
    return ok(result)


def traverse[A, B, E](f: Callable[[A], Result[B, E]], seq: Iterable[A]) -> Result[Iterable[B], E]:
    return sequence(map(f, seq))
