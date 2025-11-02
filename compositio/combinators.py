import concurrent.futures
from typing import Callable, Iterable, overload


def const[T](x: T) -> Callable[[object], T]:
    return lambda _: x


def i[T](x: T) -> T:
    """Identity"""
    return x


def it[T](x: T) -> tuple[T, T]:
    return (x, x)


def l[A](a: A, _: object) -> A:
    """First"""
    return a


def r[B](_: object, b: B) -> B:
    """Second"""
    return b


def w[A, B](f: Callable[[A, A], B]) -> Callable[[A], B]:
    """f(a, a) -> f(a)"""
    return lambda a: f(a, a)


def c[A, B, C](f: Callable[[A, B], C]) -> Callable[[B, A], C]:
    """Swap

    f(a, b) -> f(b, a)
    """
    return lambda b, a: f(a, b)


def s[A, B, C](f: Callable[[A, B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """ """
    return lambda x: f(x, g(x))


def d[A, B, C, D](f: Callable[[A, B], C], g: Callable[[D], B]) -> Callable[[A, D], C]:
    return lambda x, y: f(x, g(y))


## b
def compose[A, B, C](f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Composition.

    compose(g, f)(x) = g(f(x))

    """

    def c(x: A):
        return f(g(x))

    return c


def b1[A, B, C, D](f: Callable[[C], D], g: Callable[[A, B], C]) -> Callable[[A, B], D]:
    return lambda a, b: f(g(a, b))


def psi[A, B, C](f: Callable[[B, B], C], g: Callable[[A], B]) -> Callable[[A, A], C]:
    return lambda x, y: f(g(x), g(y))


def phi[A, B, C, D](f: Callable[[A], C], g: Callable[[C, D], B], h: Callable[[A], D]) -> Callable[[A], B]:
    return lambda x: g(f(x), h(x))


@overload
def curry[A, R](f: Callable[[A], R]) -> Callable[[A], R]: ...
@overload
def curry[A, B, R](f: Callable[[A, B], R]) -> Callable[[A], Callable[[B], R]]: ...
@overload
def curry[A, B, C, R](
    f: Callable[[A, B, C], R],
) -> Callable[[A], Callable[[B], Callable[[C], R]]]: ...
def curry(f):  # no type here; types are handled by overloads
    def _curried(*args, **kwargs):
        if len(args) + len(kwargs) >= f.__code__.co_argcount:
            return f(*args, **kwargs)
        return lambda *more_args, **more_kwargs: _curried(*args, *more_args, **{**kwargs, **more_kwargs})

    return _curried


def agg[A, B, C, D](f: Callable[[A], B], g: Callable[[C], D]) -> Callable[[tuple[A, C]], tuple[B, D]]:
    return lambda xy: (f(xy[0]), g(xy[1]))


def mapc[I, O](f: Callable[[I], O], ls: Iterable[I], max_workers: int = 4) -> Iterable[O]:
    """Concurrent map function with ThreadPoolExecutor"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        return executor.map(f, ls)


def mapcm[I, O](f: Callable[[I], O], ls: Iterable[I], max_workers: int = 4) -> Iterable[O]:
    """Maybe concurrent map function with ThreadPoolExecutor, if len(ls) > 1."""
    match ls:
        case list() if len(ls) < 2:
            return map(f, ls)
        case _:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                return executor.map(f, ls)


def until[I](pred: Callable[[I], bool], func: Callable[[I], I], val: I):
    """Apply `func` to `val` while `pred` predicate is not true.

    >>> until(lambda x: len(x) > 4, lambda x: x + [1], [1, 2])
    [1, 2, 1, 1, 1]
    >>> until(lambda x: x > 10, lambda x: x + 1, 4)
    11
    """
    while not pred(val):
        val = func(val)
    return val
