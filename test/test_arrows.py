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
def test_arrow__call__(v):
    assert addA.f(v) == addA(v)


@given(st.integers())
def test_arrow_composition(v: int):
    """Test the composition of arrows."""
    # Composition of arrows
    assert (addA >> mulA)(v) == mulA.f(addA.f(v))
    assert (mulA >> addA)(v) == addA.f(mulA.f(v))
    # Composition of an arrow and a function
    assert (addA >> mul2)(v) == mul2(addA.f(v))
    assert (mul2 >> addA)(v) == addA.f(mul2(v))
    # Composition of more than two arrows
    assert (addA >> mulA >> addA)(v) == addA.f(mulA.f(addA.f(v)))


@given(st.integers())
def test_arrow_pipe(v: int):
    """Test Arrow application with pipe operator."""
    assert (v | addA) == addA.f(v)
    assert (v | mulA) == mulA.f(v)
    assert (v | addA | mulA) == mulA.f(addA.f(v))
    assert (v | mulA | addA) == addA.f(mulA.f(v))


@given(st.integers(), st.integers())
def test_arrow_mul(v: int, w: int):
    """Test ***."""

    assert (addA * mulA)((v, w)) == (addA.f(v), mulA.f(w))
    assert (mulA * addA)((v, w)) == (mulA.f(v), addA.f(w))


@given(st.integers())
def test_arrow_mod(v: int):
    """Test &&&."""

    assert (addA % mulA)(v) == (addA.f(v), mulA.f(v))
    assert (mulA % addA)(v) == (mulA.f(v), addA.f(v))


# @given(st.integers(min_value=0))
# def test_arrow_or(v: int):
#     """Test the or operator for arrows."""
#
#     def add(x: int) -> int | None:
#         return x + 1
#
#     addA = Arrow(add)
#     nullA = Arrow(null)
#     assert (addA | nullA)(v) == addA.f(v)
#     assert (nullA | addA)(v) == addA.f(v)


# def test_arrow_xor():
#     """Test the xor operator for arrows."""
#     assert (addA ^ 123)(1) == addA.f(1)
#     assert (addA ^ 123)(None) == 123
