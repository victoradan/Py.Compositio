from hypothesis import given
from hypothesis import strategies as st

from compositio import writer
from compositio.combinators import compose, curry


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


def test_Writer_bind_op():
    @curry
    def append(suffix: str, x: str):
        return writer.Writer(x + suffix, ["append"])

    r = writer.Writer("a", ["new"]).bind(append("b"))
    assert r == writer.Writer("ab", ["new", "append"])
