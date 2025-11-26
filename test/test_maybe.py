from hypothesis import given
from hypothesis import strategies as st

from compositio import maybe
from compositio.combinators import compose, curry


@given(st.text())
def test_Maybe_functor_laws(v):
    ## identity
    assert maybe.just(v).map(lambda x: x) == maybe.just(v)
    assert maybe.nothing().map(lambda x: x) == maybe.nothing()

    ## composition
    @curry
    def append(suffix: str, x: str):
        return x + suffix

    a1 = append("1")
    a2 = append("2")

    assert maybe.just(v).map(a1).map(a2) == maybe.just(v).map(compose(a2, a1))
    assert maybe.nothing().map(a1).map(a2) == maybe.nothing().map(compose(a2, a1))


@given(st.text())
def test_Maybe_bind_laws(v):
    @curry
    def appendM(suffix: str, s: str):
        return maybe.just(s + suffix)

    ## Identity
    m = maybe.just(v)
    assert m.bind(appendM("s")) == appendM("s")(v)
    assert m.bind(maybe.just) == m

    ## associativity
    g = appendM("s")
    h = appendM("t")

    def gh(s: str):
        return g(s).bind(h)

    assert m.bind(g).bind(h) == m.bind(gh)
