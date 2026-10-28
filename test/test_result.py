from hypothesis import given
from hypothesis import strategies as st

from compositio import result
import compositio.combinators as C


@C.curry
def append(suffix: str, x: str):
    return x + suffix


@C.curry
def appendM(suffix: str, s: str):
    return result.ok(s + suffix)


@given(st.text())
def test_Result_functor_laws(v: str):
    ## identity
    assert result.ok(v).map(C.i) == result.ok(v)
    assert result.err(v).map(C.i) == result.err(v)

    ## composition
    a1 = append("1")
    a2 = append("2")

    assert result.ok(v).map(a1).map(a2) == result.ok(v).map(C.compose(a2, a1))


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
    assert m @ appendM("s") == result.ok("as")
    assert m @ appendM("s") @ appendM("t") == result.ok("ast")
    assert m @ (lambda s: appendM("s")(s) @ appendM("t")) == result.ok("ast")


def test_sequence():
    r = result.sequence([result.ok(1), result.ok(2), result.ok(3)])
    assert r == result.ok([1, 2, 3])

    r = result.sequence([result.ok(1), result.err("e"), result.ok(3)])
    assert r == result.err("e")

    r = result.sequence([])
    assert r == result.ok([])


def test_traverse():
    r = result.traverse(lambda x: result.ok(x + 1), [1, 2, 3])
    assert r == result.ok([2, 3, 4])

    r = result.traverse(lambda x: result.err(f"e{x}"), [1, 2, 3])
    assert r == result.err("e1")

    r = result.traverse(result.ok, [])
    assert r == result.ok([])


values = st.one_of(st.integers(), st.text(), st.booleans(), st.none())
results = st.one_of(st.builds(result.ok, values), st.builds(result.err, values))


@given(values)
def test_is_ok(v):
    assert result.ok(v).is_ok()
    assert not result.err(v).is_ok()


@given(values, values)
def test_from_ok(v, default):
    assert result.ok(v).from_ok(default) == v
    assert result.err(v).from_ok(default) == default


@given(values, values)
def test_from_err(v, default):
    assert result.ok(v).from_err(default) == default
    assert result.err(v).from_err(default) == v


def test_oks_errs_examples():
    rs = [result.ok(1), result.err("a"), result.ok(2), result.err("b")]
    assert result.oks(rs) == [1, 2]
    assert result.errs(rs) == ["a", "b"]

    assert result.oks([]) == []
    assert result.errs([]) == []


def test_oks_errs_keep_falsy_values():
    """Falsy values are preserved"""
    rs: list[result.Result[int | None, str | bool]] = [result.ok(0), result.err(""), result.ok(None), result.err(False)]
    assert result.oks(rs) == [0, None]
    assert result.errs(rs) == ["", False]


@given(st.lists(results))
def test_oks_errs_partition_results(rs):
    oks, errs = result.partition_results(rs)
    assert result.oks(rs) == oks
    assert result.errs(rs) == errs


@given(st.lists(results))
def test_partition_results(rs):
    oks, errs = result.partition_results(rs)

    assert len(oks) + len(errs) == len(rs)

    ## each side matches the original values, in order
    assert oks == [r.from_ok(None) for r in rs if r.is_ok()]
    assert errs == [r.from_err(None) for r in rs if not r.is_ok()]

    ## rebuilding from both sides recovers all Ok/Err elements
    assert [result.ok(v) for v in oks] == [r for r in rs if r.is_ok()]
    assert [result.err(v) for v in errs] == [r for r in rs if not r.is_ok()]


@given(st.lists(values))
def test_partition_results_homogeneous(vs):
    assert result.partition_results(map(result.ok, vs)) == (vs, [])
    assert result.partition_results(map(result.err, vs)) == ([], vs)


@given(st.lists(results))
def test_partition_results_accepts_iterators(rs):
    assert result.partition_results(iter(rs)) == result.partition_results(rs)
    assert result.oks(iter(rs)) == result.oks(rs)
    assert result.errs(iter(rs)) == result.errs(rs)
