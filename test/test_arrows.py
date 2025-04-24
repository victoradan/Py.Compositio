from hypothesis import given
from hypothesis import strategies as st

from compositio.arrows import Arrow


def add1(x: int) -> int:
    return x + 1


def mul2(x: int) -> int:
    return x * 2


@given(st.integers())
def test_arrow_composition(val):
    """Test the composition of arrows."""

    addA = Arrow(add1)
    mulA = Arrow(mul2)

    # Test the composition of arrows
    assert (addA @ mulA)(val) == addA.f(mulA.f(val))
    assert (mulA @ addA)(val) == mulA.f(addA.f(val))
    # Test the composition of an arrow and a function
    assert (addA @ mul2)(val) == addA.f(mul2(val))
    assert (mul2 @ addA)(val) == mul2(addA.f(val))


@given(st.integers())
def test_arrow_pipe(val):
    """Test the pipe operator for arrows."""

    addA = Arrow(add1)
    mulA = Arrow(mul2)

    assert (val >> addA) == addA.f(val)
    assert (val >> mulA) == mulA.f(val)
    assert (val >> addA >> mulA) == mulA.f(addA.f(val))
    assert (val >> mulA >> addA) == addA.f(mulA.f(val))
