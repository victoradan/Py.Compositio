from hypothesis import given
from hypothesis import strategies as st

from compositio import result
from compositio.combinators import compose, curry

@curry
def append(suffix: str, x: str):
    return x + suffix

@given(st.text())
def test_Result_functor_laws(v):
    ## identity
    assert result.ok(v).map(lambda x: x) == result.ok(v)
    assert result.err(v).map(lambda x: x) == result.err(v)

    ## composition
    a1 = append("1")
    a2 = append("2")

    assert result.ok(v).map(a1).map(a2) == result.ok(v).map(compose(a2, a1))

def test_Result_map_op():

    r = result.ok("a") / append("b")
    assert r == result.ok("ab")

    r = result.err("e") / append("b")
    assert r == result.err("e")

def test_Result_bimap_op():
    r = result.ok("a") // (append("b"), append("c"))
    assert r == result.ok("ab")

    r = result.err("e") // (append("b"), append("c"))
    assert r == result.err("ec")

