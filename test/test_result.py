from hypothesis import given
from hypothesis import strategies as st

from compositio import result
from compositio.combinators import compose, curry


@curry
def append(suffix: str, x: str):
    return x + suffix


@curry
def appendM(suffix: str, s: str):
    return result.ok(s + suffix)


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

    r = append("b") / result.ok("a")
    assert r == result.ok("ab")

    r = append("b") / result.err("e")
    assert r == result.err("e")


def test_Result_bimap_op():
    r = (append("b"), append("c")) // result.ok("a")
    assert r == result.ok("ab")

    r = (append("b"), append("c")) // result.err("e")
    assert r == result.err("ec")


@given(st.text())
def test_Result_bind_laws(v):
    ## Identity
    m = result.ok(v)
    assert m.bind(appendM("s")) == appendM("s")(v)
    assert m.bind(result.ok) == m

    ## associativity
    g = appendM("s")
    h = appendM("t")

    def gh(s: str):
        return g(s).bind(h)

    assert m.bind(g).bind(h) == m.bind(gh)


def test_Result_bind_op():
    m = result.ok("a")
    assert m >> appendM("s") == result.ok("as")
    assert m >> appendM("s") >> appendM("t") == result.ok("ast")
    assert (m >> appendM("s")) >> appendM("t") == result.ok("ast")
    assert m >> (lambda s: appendM("s")(s) >> appendM("t")) == result.ok("ast")
