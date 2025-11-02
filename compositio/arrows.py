import functools
from typing import Callable, Iterable

import compositio.combinators as Comb


class Arrow[A, B]:
    f: Callable[[A], B]

    __match_args__ = ("f",)

    def __init__(self, f: Callable[[A], B]):
        self.f = f

    def __call__(self, x: A):
        """Arrow application.

        A(x) = A.f(x)

        """
        return self.f(x)

    __ror__ = __call__
    __or__ = __call__

    def __rrshift__[C](self, other: "Arrow[C, A]" | Callable[[C], A]) -> "Arrow[C, B]":
        """Arrow composition.
        Compose Arrow with function, or Arrow with Arrow.

        (C -> A) -> (A -> B) ==> (C -> B)

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> (addOne >> double)(2)
        6
        >>> ((lambda x: x + 1) >> double)(2)
        6
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

    def __rshift__[C](self, other: "Arrow[B, C]" | Callable[[B], C]) -> "Arrow[A, C]":
        """Arrow composition.
        Compose function with Arrow, or Arrow with Arrow.

        (A -> B) -> (B -> C) ==> (A -> C)

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> (addOne >> double)(2)
        6
        >>> (addOne >> (lambda x: x * 2))(2)
        6
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

    def __mul__[C, D](self, other: "Arrow[C, D]"):
        """(***) Split the input between the two argument arrows and combine their output.

        (A -> B, C -> D) ==> (A, C) -> (B, D)

           |--> self -->|
        ==>|            |==>
           |--> other ->|

        (x, y) | f * g = (f x, g y)

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> (addOne * double)((5, 10))
        (6, 20)

        >>> (5, 10) | addOne * double
        (6, 20)
        """

        return Arrow(Comb.agg(self.f, other.f))

    def __mod__[C](self, other: "Arrow[A, C]") -> "Arrow[A, tuple[B, C]]":
        """(&&&) Fanout

        (A -> B, A -> C) ==> A -> (B, C)

           |--> self -->|
        -->|            |==>
           |--> other ->|

        x | f % g = (f x, g x)

        This is equivalent to: (lambda x : (x, x)) >> (f * g)


        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> (addOne % double)(10)
        (11, 20)
        """

        def h(x: A):  # pylint: disable=undefined-variable
            return (x, x)

        return Arrow(h) >> (self * other)

    ## Choice ##

    ## TODO (+++)
    # def __add__(self, )

    ## TODO (|||)
    # def __sub__(self, )

    ## Other ##

    # def __or__(self, other: "Arrow[A,B]") -> "Arrow[A, B]":
    #     """
    #     Apply alternate Arrows until the first non-falsy result is found.
    #
    #     >>> none = Arrow(lambda x : None)
    #     >>> addOne = Arrow(lambda x : x + 1)
    #     >>> triple = Arrow(lambda x : x * 3)
    #     >>> (addOne | triple)(1)
    #     2
    #     >>> (none | triple)(1)
    #     3
    #     """
    #
    #     def h(x: A) -> B:  # pylint: disable=undefined-variable
    #         return self.f(x) or other.f(x)
    #
    #     return Arrow(h)
    #
    # def __xor__(self, other: B) -> "Arrow[A | None, B]":
    #     """If input is None, return `other`, else call `self` on input.
    #
    #     >>> addOne = Arrow(lambda x : x + 1)
    #     >>> (addOne ^ 0)(None)
    #     0
    #     >>> (addOne ^ 0)(1)
    #     2
    #     """
    #
    #     def h(x: A | None) -> B:  # pylint: disable=undefined-variable
    #         return self.f(x) if x is not None else other
    #
    #     return Arrow(h)


def first[A, B, T](arrow: "Arrow[A, B]") -> Arrow[tuple[A, T], tuple[B, T]]:
    """
    Send the first component of the input through the argument arrow, and copy the rest unchanged to the output.

    A -> B ==> (A, T) -> (B, T)

    >>> addOne = Arrow(lambda x : x + 1)
    >>> first(addOne)((10, 10))
    (11, 10)
    """

    return arrow * Arrow(Comb.i)


aid = Arrow(Comb.i)


def mapa[I, O](f: Callable[[I], O]):
    """Version of map that works like an arrow.

    >>> list(mapa(lambda x : x + 1)([2, 3, 5, 7, 11]))
    [3, 4, 6, 8, 12]

    >>> (mapa(lambda x : x + 1) >> list)([2, 3, 5, 7, 11])
    [3, 4, 6, 8, 12]

    >>> [2, 3, 5, 7, 11] | mapa(lambda x : x + 1) >> list
    [3, 4, 6, 8, 12]

    """
    return Arrow[Iterable[I], Iterable[O]](lambda xs: map(f, xs))


def mapca[I, O](f: Callable[[I], O]):
    """Concurrent map that works like an arrow.

    >>> list(mapca(lambda x : x + 1)([2, 3, 5, 7, 11]))
    [3, 4, 6, 8, 12]

    """
    return Arrow[Iterable[I], Iterable[O]](lambda xs: Comb.mapc(f, xs))


def reducea[I, O](f: Callable[[O, I], O], z: O):
    """Version of reduce (fold) that works like an arrow.

    >>> from operator import add
    >>> reducea(add, 0)([2, 3, 5, 7, 11])
    28

    `z` stands for "zero", it initializes the reduction.

    >>> reducea(lambda s, n : s + str(n), '')([2, 3, 5, 7, 11])
    '235711'

    """
    return Arrow[Iterable[I], O](lambda xs: functools.reduce(f, xs, z))
