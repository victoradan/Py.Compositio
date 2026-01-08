from hypothesis import given
from hypothesis import strategies as st

from compositio import maybe as M
from compositio.combinators import compose, curry


@curry
def append(suffix: str, x: str):
    return x + suffix


@curry
def appendM(suffix: str, s: str):
    return M.just(s + suffix)


@given(st.text())
def test_Maybe_functor_laws(v):
    ## identity
    assert M.just(v).map(lambda x: x) == M.just(v)
    assert M.nothing().map(lambda x: x) == M.nothing()

    ## composition
    a1 = append("1")
    a2 = append("2")

    assert M.just(v).map(a1).map(a2) == M.just(v).map(compose(a2, a1))
    assert M.nothing().map(a1).map(a2) == M.nothing().map(compose(a2, a1))


@given(st.text())
def test_Maybe_apply_laws(v):
    ## identity
    assert M.just(v).apply(M.just(lambda x: x)) == M.just(v)
    assert M.nothing().apply(M.just(lambda x: x)) == M.nothing()
    assert M.just(v).apply(M.nothing()) == M.nothing()
    ## homomorphism
    assert M.just(v).apply(M.just(append("1"))) == M.just(append("1")(v))
    assert M.nothing().apply(M.just(append("1"))) == M.nothing()
    assert M.just(v).apply(M.nothing()) == M.nothing()


@given(st.text())
def test_Maybe_bind_laws(v):
    ## Identity
    m = M.just(v)
    assert m.bind(appendM("s")) == appendM("s")(v)
    assert m.bind(M.just) == m

    ## associativity
    g = appendM("s")
    h = appendM("t")

    def gh(s: str):
        return g(s).bind(h)

    assert m.bind(g).bind(h) == m.bind(gh)


def test_Maybe_map_op():
    r = append("b") / M.just("a")
    assert r == M.just("ab")

    r = append("b") / M.nothing()
    assert r == M.nothing()


def test_Maybe_apply_op():
    # m1 = M.just(append("s"))
    # m2 = M.just("a")
    # r = m1 % m2
    assert M.just("a").apply(M.nothing()) == M.nothing()
    assert M.nothing().apply(M.nothing()) == M.nothing()
    assert M.nothing().apply(M.just(append("s"))) == M.nothing()


def test_Maybe_bind_op():
    m = M.just("a")
    assert m @ appendM("s") == M.just("as")
    assert m @ appendM("s") @ appendM("t") == M.just("ast")
    assert m @ (lambda s: appendM("s")(s) @ appendM("t")) == M.just("ast")
    assert M.nothing() @ appendM("s") == M.nothing()


def test_cat_maybes():
    assert M.cat_maybes([]) == []
    assert M.cat_maybes([M.nothing()]) == []
    assert M.cat_maybes([M.just(1), M.nothing()]) == [1]


def test_squence():
    assert M.sequence([]) == M.just([])
    assert M.sequence([M.nothing()]) == M.nothing()
    assert M.sequence([M.just(1), M.just(2)]) == M.just([1, 2])
    assert M.sequence([M.just(1), M.nothing()]) == M.nothing()


def test_both():
    assert M.both(M.just(1), M.just(2)) == M.just((1, 2))
    assert M.both(M.just(1), M.nothing()) == M.nothing()
    assert M.both(M.nothing(), M.just(2)) == M.nothing()
    assert M.both(M.nothing(), M.nothing()) == M.nothing()
