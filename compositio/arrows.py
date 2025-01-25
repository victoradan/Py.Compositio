"""
Revise operators?

|   apply 
**  arrow composition
*   arrow and func composition
^   if none else
@   invoke while none

"""

from typing import Callable, Iterable
from functools import reduce

from .combinators import identity, mapc


class Arrow[X, Y]:
    f: Callable[[X], Y]

    def __init__(self, func: Callable[[X], Y]):
        self.f = func

    def __rrshift__(self, x: X):
        """Arrow application.

        x >> F, invokes the `F` Arrow on `x`.

        x >> F = F.f(x)

        >>> 10 >> Arrow(lambda x : x + 1)
        11

        """
        return self.f(x)

    @staticmethod
    def first[I, O](arrow: "Arrow[I, O]"):
        """
        Send the first component of the input through the argument arrow, and copy the rest unchanged to the output.

        I -> O ==> (I, T) -> (O, T)
        """

        return arrow + Arrow(identity)

    def __mul__[O](self, other: "Arrow[Y, O]"):
        """Arrow composition

        (I -> O) -> (O -> P) ==> (I -> P)
        """

        def h(x: X):  # pylint: disable=undefined-variable
            return other.f(self.f(x))

        return Arrow(h)

    def __add__[I2, O2](self, other: "Arrow[I2, O2]"):
        """Split the input between the two argument arrows and combine their output.

        (I -> O, I2 -> O2) ==> (I, I2) -> (O, O2)

           |--> self -->|
        ==>|            |==>
           |--> other ->|

        (x, y) >> f + g = (f x, g y)

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> (5, 10) >> addOne + double
        (6, 20)
        """

        def h(xy: tuple[X, I2]):  # pylint: disable=undefined-variable
            return self.f(xy[0]), other.f(xy[1])

        return Arrow(h)

    def __sub__[O2](self, other: "Arrow[X, O2]"):
        """Fanout: send the input to both argument arrows and combine their output.

        (I -> O, I -> P) ==> I ->  (O, P)

           |--> self -->|
        -->|            |==>
           |--> other ->|

        x >> f - g = (f x, g x)

        This is equivalent to: (lambda x : (x, x)) % (f + g)

        Mnemonic: The - sign means that we process a single input.

        >>> addOne = Arrow(lambda x : x + 1)
        >>> double = Arrow(lambda x : x * 2)
        >>> 10 >> addOne - double
        (11, 20)

        """

        def h(x: X):  # pylint: disable=undefined-variable
            return (x, x)

        return Arrow(h) * (self + other)

    def __or__(self, other: "Arrow[X,Y]"):
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

        def h(x: X) -> Y:  # pylint: disable=undefined-variable
            return self.f(x) or other.f(x)

        return Arrow(h)

    def __xor__(self, other: "Arrow[None, Y]") -> "Arrow[X | None, Y]":
        """If input is None, call `other`, else call `self` on it.

        >>> addOne = Arrow(lambda x : x + 1)
        >>> zero = Arrow(lambda _ : 0)
        >>> None >> (addOne ^ zero)
        0
        >>> 1 >> (addOne ^ zero)
        2
        """
        return Arrow(lambda x: other.f(x) if x is None else self.f(x))

    def __mod__[H](self, other: Callable[[Y], H]):
        """Function and Arrow composition; function after.

        --> self --> f -->

        If f and g are pure functions, then
        Arrow(f) % g  ==  Arrow(f) * Arrow(g)

        Mnemonic: The two circles of the % symbol remind you that on one side
        is an arrow, and the other side is a pure function.

        >>> addOne = Arrow(lambda x : x + 1)
        >>> 10 >> addOne % (lambda x : x * 2)  # This lambda is not an arrow.
        22

        """
        return self * Arrow(other)

    def __rmod__[H](self, other: Callable[[H], X]):
        """Function and Arrow composition; function before.

        --> f --> self -->

        If f and g are pure functions, then
        f % Arrow(g)  ==  Arrow(f) * Arrow(g)

        Note that the direction of the data flow (from left to right) is
        preserved, since `other` appears before `self` in the code.  It's just
        that `other` is a pure function that doesn't support `__mod__`, so
        `__rmod__` of the following object (self) kicks in.

        >>> double = Arrow(lambda x : x * 2)
        >>> 10 >> (lambda x : x + 1) % double  # This lambda is not an arrow.
        22

        """
        return Arrow(other) * self


idA = Arrow(identity)


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
    return Arrow[Iterable[I], Iterable[O]](lambda xs: mapc(f, xs))


def mapA(a: Arrow):
    """Version of map that works like an arrow and takes an arrow instead of a
    function.

    >>> addOne = Arrow(lambda x : x + 1)
    >>> [2, 3, 5, 7, 11] >> mapA(addOne) >> Arrow(list)
    [3, 4, 6, 8, 12]

    """
    return mapa(a.f)


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


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    def add2(x: int):
        return x + 2

    def mul3(x: int):
        return x * 3

    def none(x: int) -> int | None:
        return None

    def maybeAdd3(x: int) -> int | None:
        return x + 3

    r = idA.f(3)
    r = 2 >> idA
    r = identity(3)

    r = (2, 2) >> Arrow(add2) + idA % mul3 % mul3
    print(r)
    r = (1, 1) >> Arrow.first(Arrow(add2))
    print(r)
    m = Arrow(none) | Arrow(maybeAdd3)
    print(2 >> m)
