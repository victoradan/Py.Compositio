from hypothesis import given
from hypothesis import strategies as st

from compositio.arrows import Arrow


def null(_: int) -> int | None:
    return None


def add1(x: int) -> int:
    return x + 1


def mul2(x: int) -> int:
    return x * 2


addA = Arrow(add1)
mulA = Arrow(mul2)


@given(st.integers())
def test_arrow_composition(v):
    """Test the composition of arrows."""

    # Test the composition of arrows
    assert (addA @ mulA)(v) == addA.f(mulA.f(v))
    assert (mulA @ addA)(v) == mulA.f(addA.f(v))
    # Test the composition of an arrow and a function
    assert (addA @ mul2)(v) == addA.f(mul2(v))
    assert (mul2 @ addA)(v) == mul2(addA.f(v))


@given(st.integers())
def test_arrow_pipe(v):
    """Test the pipe operator for arrows."""

    assert (v >> addA) == addA.f(v)
    assert (v >> mulA) == mulA.f(v)
    assert (v >> addA >> mulA) == mulA.f(addA.f(v))
    assert (v >> mulA >> addA) == addA.f(mulA.f(v))


@given(st.integers(), st.integers())
def test_arrow_add(v, w):
    """Test the addition of arrows.
    (x, y) >> f + g = (f x, g y)
    """

    assert (addA + mulA)((v, w)) == (addA.f(v), mulA.f(w))
    assert (mulA + addA)((v, w)) == (mulA.f(v), addA.f(w))


@given(st.integers())
def test_arrow_sub(v):
    """Test the subtraction of arrows.
    x >> f - g = (f x, g x)
    """

    assert (addA - mulA)(v) == (addA.f(v), mulA.f(v))
    assert (mulA - addA)(v) == (mulA.f(v), addA.f(v))


@given(st.integers())
def test_arrow_or(v):
    """Test the or operator for arrows."""

    def add(x: int) -> int | None:
        return x + 1

    addA = Arrow(add)
    nullA = Arrow(null)
    assert (addA | nullA)(v) == addA.f(v)
    assert (nullA | addA)(v) == addA.f(v)


def test_arrow_xor():
    """Test the xor operator for arrows."""
    assert (addA ^ 123)(1) == addA.f(1)
    assert (addA ^ 123)(None) == 123
