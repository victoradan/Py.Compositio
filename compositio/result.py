from typing import Callable
from dataclasses import dataclass

@dataclass
class Success[T]:
    _val: T

@dataclass
class Failure[T]:
    _val: T

@dataclass
class Result[S,F]:
    _val: Success[S] | Failure[F]

    def map[T](self, f:Callable[[S], T]):
        match self._val:
            case Success(v):
                return Result(Success(f(v)))
            case Failure(v):
                return Result(Failure(v))

    def bind[T](self, f: Callable[[S], "Result[T, F]"]):
        match self._val:
            case Success(v):
                return f(v)
            case Failure(v):
                return Result(Failure(v))

    def __rshift__[T](self, other: Callable[[S], "Result[T, F]"]):
        return self.bind(other)
