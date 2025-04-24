from hypothesis import given
from hypothesis import strategies as st

from compositio.arrows import Arrow


def add1(x: int) -> int:
    return x + 1


def mul2(x: int) -> int:
    return x * 2


addA = Arrow(add1)
mulA = Arrow(mul2)


@given(st.integers())
def test_arrow_composition(val):
    """Test the composition of arrows."""

    # Test the composition of arrows
    assert (addA @ mulA)(val) == addA.f(mulA.f(val))
    assert (mulA @ addA)(val) == mulA.f(addA.f(val))
    # Test the composition of an arrow and a function
    assert (addA @ mul2)(val) == addA.f(mul2(val))
    assert (mul2 @ addA)(val) == mul2(addA.f(val))


@given(st.integers())
def test_arrow_pipe(val):
    """Test the pipe operator for arrows."""

    assert (val >> addA) == addA.f(val)
    assert (val >> mulA) == mulA.f(val)
    assert (val >> addA >> mulA) == mulA.f(addA.f(val))
    assert (val >> mulA >> addA) == addA.f(mulA.f(val))


def test_arrow_add():
    """Test the addition of arrows.
    (x, y) >> f + g = (f x, g y)
    """

    assert (addA + mulA)((1, 2)) == (addA.f(1), mulA.f(2))
    assert (mulA + addA)((1, 2)) == (mulA.f(1), addA.f(2))


def test_arrow_sub():
    """Test the subtraction of arrows.
    x >> f - g = (f x, g x)
    """

    assert (addA - mulA)(1) == (addA.f(1), mulA.f(1))
    assert (mulA - addA)(1) == (mulA.f(1), addA.f(1))
