from functools import reduce
from typing import Callable, Iterable

import compositio.combinators as C


class Arrow[A, B]:
    f: Callable[[A], B]

    __match_args__ = ("f",)

    def __init__(self, f: Callable[[A], B]):
        self.f = f

    def __rrshift__(self, x: A):
        """Arrow application.

        x >> F, invokes the `F` Arrow on `x`.
        x >> F = F.f(x)

        >>> 10 >> Arrow(lambda x : x + 1)
        11

        """
        return self.f(x)

    __call__ = __rrshift__

    def __rmatmul__[C](self, other: "Arrow[C, A]" | Callable[[C], A]) -> "Arrow[C, B]":
        """Arrow composition

        (C -> A) -> (A -> B) ==> (C -> B)
        """

        match other:
            case Arrow():

                def h(x: C):
                    return self.f(other.f(x))

                return Arrow(h)
            case _:

                def g(x: C):
                    return self.f(other(x))

                return Arrow(g)

    def __matmul__[C](self, other: "Arrow[B, C]" | Callable[[B], C]) -> "Arrow[A, C]":
        """Arrow composition

        (I -> O) -> (O -> P) ==> (I -> P)
        """

        match other:
            case Arrow():

                def h(x: A):
                    return other.f(self.f(x))

                return Arrow(h)
            case _:

                def g(x: A):
                    return other(self.f(x))

                return Arrow(g)

    def __add__[C, D](self, other: "Arrow[C, D]"):
        """Split the input between the two argument arrows and combine their output.

        (A -> B, C -> D) ==> (A, C) -> (B, D)

           |--> self -->|
        ==>|            |==>
           |--> other ->|

        (x, y) >> f + g = (f x, g y)

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> (5, 10) >> addOne + double
        (6, 20)
        """

        def h(xy: tuple[A, C]): 
            return self.f(xy[0]), other.f(xy[1])

        return Arrow(h)

    def __sub__[C](self, other: "Arrow[A, C]") -> "Arrow[A, tuple[B, C]]":
        """Fanout

        (A -> B, A -> C) ==> A -> (B, C)

           |--> self -->|
        -->|            |==>
           |--> other ->|

        x >> f - g = (f x, g x)

        This is equivalent to: (f + g) @ (lambda x : (x, x))

        Mnemonic: The - sign means that we process a single input.

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> 10 >> addOne - double
        (11, 20)

        """

        def h(x: A):  # pylint: disable=undefined-variable
            return (x, x)

        return Arrow(h) @ (self + other)

    def __or__(self, other: "Arrow[A,B]") -> "Arrow[A, B]":
        """
        Apply alternate Arrows until the first non-falsy result is found.

        >>> none = Arrow(lambda x : None)
        >>> addOne = Arrow(lambda x : x + 1)
        >>> triple = Arrow(lambda x : x * 3)
        >>> 1 >> (addOne | triple)
        2
        >>> 1 >> (none | triple)
        3
        """

        def h(x: A) -> B:  # pylint: disable=undefined-variable
            return self.f(x) or other.f(x)

        return Arrow(h)

    def __xor__(self, other: B) -> "Arrow[A | None, B]":
        """If input is None, return `other`, else call `self` on input.

        >>> addOne = Arrow(lambda x : x + 1)
        >>> None >> (addOne ^ 0)
        0
        >>> 1 >> (addOne ^ 0)
        2
        """

        def h(x: A | None) -> B:  # pylint: disable=undefined-variable
            return self.f(x) if x is not None else other

        return Arrow(h)


def first[A, B, T](arrow: "Arrow[A, B]") -> Arrow[tuple[A, T], tuple[B,T]]:
    """
    Send the first component of the input through the argument arrow, and copy the rest unchanged to the output.

    A -> B ==> (A, T) -> (B, T)
    """

    return arrow + Arrow(C.i)


aid = Arrow(C.i)


def mapa[I, O](f: Callable[[I], O]):
    """Version of map that works like an arrow.

    >>> list([2, 3, 5, 7, 11] >> mapa(lambda x : x + 1))
    [3, 4, 6, 8, 12]

    >>> [2, 3, 5, 7, 11] >> mapa(lambda x : x + 1) >> Arrow(list)
    [3, 4, 6, 8, 12]

    """
    return Arrow[Iterable[I], Iterable[O]](lambda xs: map(f, xs))


def mapca[I, O](f: Callable[[I], O]):
    """Concurrent map that works like an arrow.

    >>> [2, 3, 5, 7, 11] >> mapca(lambda x : x + 1) >> Arrow(list)
    [3, 4, 6, 8, 12]

    """
    return Arrow[Iterable[I], Iterable[O]](lambda xs: C.mapc(f, xs))


def reducea[I, O](f, z):
    """Version of reduce (fold) that works like an arrow.

    >>> from operator import add
    >>> [2, 3, 5, 7, 11] >> reducea(add, 0)
    28

    `z` stands for "zero", it initializes the reduction.

    >>> [2, 3, 5, 7, 11] >> reducea(lambda s, n : s + str(n), '')
    '235711'

    """
    return Arrow[list[I], O](lambda xs: reduce(f, xs, z))
