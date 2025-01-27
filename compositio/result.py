from typing import Callable, Literal
from dataclasses import dataclass


@dataclass
class Result[S, F]:
    _val: tuple[Literal["Ok"], S] | tuple[Literal["Err"], F]

    def map[T](self, f: Callable[[S], T]) -> "Result[T,F]":
        match self._val:
            case "Ok", v:
                return Result(("Ok", f(v)))
            case "Err", v:
                return Result(("Err", v))

    def bimap[
        S2, F2
    ](self, f: Callable[[S], S2], g: Callable[[F], F2]) -> "Result[S2, F2]":
        match self._val:
            case "Ok", v:
                return Result(("Ok", f(v)))
            case "Err", v:
                return Result(("Err", g(v)))

    def bind[T](self, f: Callable[[S], "Result[T, F]"]) -> "Result[T, F]":
        match self._val:
            case "Ok", v:
                return f(v)
            case "Err", v:
                return Result(("Err", v))

    def __rshift__[T](self, other: Callable[[S], "Result[T, F]"]):
        return self.bind(other)

    def either[R](self, onsuccess: Callable[[S], R], onfailure: Callable[[F], R]) -> R:
        match self._val:
            case "Ok", v:
                return onsuccess(v)
            case "Err", v:
                return onfailure(v)


def ok[S, F](v: S):
    return Result[S, F](("Ok", v))


def err[S, F](v: F):
    return Result[S, F](("Err", v))


if __name__ == "__main__":

    def suc(x: int) -> str:
        return "str"

    def failbad(x: str) -> int:
        return 3

    def fail(x: str) -> str:
        return "3"

    def b(x: int) -> Result[int, str]:
        return ok(x + 2)

    s2: Result[int, str] = ok(21)
    s: Result[int, str] = ok(21)
    f = err("Error")
    r = f.either(suc, fail)
    r = s.either(suc, failbad)
    print(r)
    r = s2 >> b >> b
    print(r)
