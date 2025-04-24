from compositio.arrows import Arrow
from hypothesis import given, strategies as st

@given(st.integers())
def test_arrow_composition(val):
    """Test the composition of arrows."""

    def add(x: int) -> int:
        return x + 1

    def mul(x: int) -> int:
        return x * 2

    addA = Arrow(add)
    mulA = Arrow(mul)

    # Test the composition of arrows
    assert (addA @ mulA)(val) == addA.f(mulA.f(val))
    assert (mulA @ addA)(val) == mulA.f(addA.f(val))
    # Test the composition of an arrow and a function
    assert (addA @ mul)(val) == addA.f(mul(val))
    assert (mul @ addA)(val) == mul(addA.f(val))
