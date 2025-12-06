from hypothesis import given
from hypothesis import strategies as st

from compositio import writer
from compositio.combinators import compose, curry


@curry
def appendM(suffix: str, x: str):
    return writer.Writer(x + suffix, ["append"])


@given(st.text())
def test_Writer_functor_laws(v):
    ## identity
    assert writer.Writer(v, []).map(lambda x: x) == writer.Writer(v, [])

    ## composition
    @curry
    def append(suffix: str, x: str):
        return x + suffix

    a1 = append("1")
    a2 = append("2")

    assert writer.Writer(v, []).map(a1).map(a2) == writer.Writer(v, []).map(compose(a2, a1))


@given(st.text())
def test_Writer_bind_laws(v):
    ## Identity
    m = writer.Writer.pure(v)
    assert m.bind(appendM("s")) == appendM("s")(v)
    assert m.bind(writer.Writer.pure) == m

    ## associativity
    g = appendM("s")
    h = appendM("t")

    def gh(s: str):
        return g(s).bind(h)

    assert m.bind(g).bind(h) == m.bind(gh)


def test_Writer_bind_op():
    m = writer.Writer.pure("a")
    assert m @ appendM("s") == writer.Writer("as", ["append"])
    assert m @ appendM("s") @ appendM("t") == writer.Writer("ast", ["append", "append"])
    assert m @ (lambda s: appendM("s")(s) @ appendM("t")) == writer.Writer("ast", ["append", "append"])
