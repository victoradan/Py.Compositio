import concurrent.futures
from typing import Callable, Iterable, overload


def identity[T](x: T) -> T:
    return x


def const[T](x: T) -> Callable[[object], T]:
    def f(_):
        return x

    return f


def compose[A, B, C](f: Callable[[A], B], g: Callable[[B], C]):
    """Pure function composition.

    compose(f, g)(x) = g(f(x))

    Note that I don't compose in the usual order seen in methematics.
    Composition is usually (f o g)(x) = f(g(x)).  I don't like that, because
    it's not in the same order as the arrows for which computations flow from
    left to right.  When I see (f o g), I want to apply f first, and then g.

    """

    def c(x: A):
        return g(f(x))

    return c


@overload
def curry[A, R](f: Callable[[A], R]) -> Callable[[A], R]: ...
@overload
def curry[A, B, R](f: Callable[[A, B], R]) -> Callable[[A], Callable[[B], R]]: ...
@overload
def curry[A, B, C, R](f: Callable[[A, B, C], R]) -> Callable[[A], Callable[[B], Callable[[C], R]]]: ...
def curry(f):  # no type here; types are handled by overloads
    def _curried(*args, **kwargs):
        if len(args) + len(kwargs) >= f.__code__.co_argcount:
            return f(*args, **kwargs)
        return lambda *more_args, **more_kwargs: _curried(*args, *more_args, **{**kwargs, **more_kwargs})

    return _curried


def dup[A](x: A) -> tuple[A, A]:
    return (x, x)


def swap[A, B](x: A, y: B) -> tuple[B, A]:
    return (y, x)


def mapc[I, O](f: Callable[[I], O], ls: Iterable[I]):
    """Concurrent map function with ThreadPoolExecutor"""
    with concurrent.futures.ThreadPoolExecutor() as executor:
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


