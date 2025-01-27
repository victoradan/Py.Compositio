from typing import Callable, Protocol, Self
from dataclasses import dataclass


@dataclass
class Ok[T]:
    _val: T

    def map[R](self, f: Callable[[T], R]):
        return Ok(f(self._val))

    def bimap[F, R](self, f: Callable[[T], R], _: Callable[[F], R]):
        return Ok(f(self._val))

    def bind[R](self, f: Callable[[T], "Ok[R]"]):
        return f(self._val)

    def either[F, R](self, onsuccess: Callable[[T], R], _: Callable[[F], R]):
        return onsuccess(self._val)


@dataclass
class Err[T]:
    _val: T

    def map[R](self, _: Callable[[T], R]):
        return self

    def bimap[S, R](self, _: Callable[[S], R], g: Callable[[T], R]):
        return Err(g(self._val))

    def bind[R](self, _: Callable[[T], "Ok[R]"]):
        return self

    def either[S, R](self, _: Callable[[S], R], onfailure: Callable[[T], R]):
        return onfailure(self._val)


type Result[O, E] = Ok[O] | Err[E]


if __name__ == "__main__":

    def suc(x: int) -> str:
        return "str"

    def failbad(x: str) -> int:
        return 3

    def fail(x: str) -> str:
        return "3"

    s = Ok(21)
    f = Err("error")
    r = s.either(suc, fail)
    print(r)
    r: str = f.either(suc, fail)
    print(r)
