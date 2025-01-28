
from typing import Callable, Literal
from dataclasses import dataclass


@dataclass
class Result3[O, E, P]:
    _val: tuple[Literal["Ok"], O] | tuple[Literal["Err"], E] | tuple[Literal["Proc"], P] 

    def map[T](self, f: Callable[[O], T]) -> "Result3[T, E, P]":
        match self._val:
            case "Ok", v:
                return Result3(("Ok", f(v)))
            case "Err", v:
                return Result3(("Err", v))
            case "Proc", v:
                return Result3(("Proc", v))

    def bimap[
        O2, E2
    ](self, f: Callable[[O], O2], g: Callable[[E], E2]) -> "Result3[O2, E2, P]":
        match self._val:
            case "Ok", v:
                return Result3(("Ok", f(v)))
            case "Err", v:
                return Result3(("Err", g(v)))
            case "Proc", v:
                return Result3(("Proc", v))

    def bind[T](self, f: Callable[[O], "Result3[T, E, P]"]) -> "Result3[T, E, P]":
        match self._val:
            case "Ok", v:
                return f(v)
            case "Err", v:
                return Result3(("Err", v))
            case "Proc", v:
                return Result3(("Proc", v))

    def __rshift__[T](self, other: Callable[[O], "Result3[T, E, P]"]):
        return self.bind(other)

    def either[R](self, onsuccess: Callable[[O], R], onfailure: Callable[[E], R], onproc: Callable[[P], R]) -> R:
        match self._val:
            case "Ok", v:
                return onsuccess(v)
            case "Err", v:
                return onfailure(v)
            case "Proc", v:
                return onproc(v)


def ok[O, E, P](v: O):
    return Result3[O, E, P](("Ok", v))


def err[O, E, P](v: E):
    return Result3[O, E, P](("Err", v))

def proc[O, E, P](v: P):
    return Result3[O, E, P](("Proc", v))


if __name__ == "__main__":

    def suc(x: int) -> str:
        return "str"

    def failbad(x: str) -> int:
        return 3

    def fail(x: str) -> str:
        return "3"

    def b(x: int) -> Result3[int, str, str]:
        return ok(x + 2)

    s2 = ok(21)
    s = ok(21)
    f = err("Error")
    r = f.either(suc, fail, lambda x : x)
    r = s.either(suc, failbad, lambda x : x)
    print(r)
    r = s2 >> b >> b
    print(r)
