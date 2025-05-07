from hypothesis import given
from hypothesis import strategies as st

from compositio import result
from compositio.combinators import compose, curry


@given(st.text())
def test_Result_functor_laws(v):
    ## identity
    assert result.ok(v).map(lambda x: x) == result.ok(v)
    assert result.err(v).map(lambda x: x) == result.err(v)

    ## composition
    @curry
    def append(suffix: str, x: str):
        return x + suffix

    a1 = append("1")
    a2 = append("2")

    assert result.ok(v).map(a1).map(a2) == result.ok(v).map(compose(a1, a2))
