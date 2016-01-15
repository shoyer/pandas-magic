import inspect
import types

import pandas as pd
from pandas import DataFrame

from .methods import (frame_methods, indexer_methods, agg_methods,
                      groupby_methods)

__all__ = ['injected', 'is_thunk', 'add_magic']


def injected(df, thunk):
    """Evaluate a thunk in the context of DataFrame

    >>> df = pd.DataFrame({'x': [0, 1, 2]}, index=['a', 'b', 'c'])
    >>> injected(df, lambda: x ** 2)
    a    0
    b    1
    c    4
    Name: x, dtype: int64
    """
    new_globals = thunk.func_globals.copy()
    new_globals.update(df)
    new_thunk = types.FunctionType(thunk.func_code, new_globals, thunk.func_name,
                                   thunk.func_defaults, thunk.func_closure)
    return new_thunk()


def is_thunk(f):
    """A thunk is a function that takes no arguments
    """
    return callable(f) and not inspect.getargspec(f).args


def _maybe_add_magic(obj):
    if isinstance(obj, pd.DataFrame):
        return MagicFrame(obj)
    if isinstance(obj, pd.core.groupby.GroupBy):
        return MagicGroupBy(obj)
    return obj


def add_magic(obj):
    """Add macro magic to the given object
    """
    result = _maybe_add_magic(obj)
    if result is obj:
        raise TypeError('cannot make object of type %r magical' % type(obj))
    return result


# _original_finalize = pd.DataFrame.__finalize__

# def

_original___new__ = pd.DataFrame.__new__

def _patched_new(*args, **kwargs):
    return add_magic(_original___new__(*args, **kwargs))


def install_magic():
    pd.DataFrame.__new__ = types.MethodType(
        _patched_new, None, pd.DataFrame)
    # pd.DataFrame.magic = property(add_magic)


class BaseMagic(object):
    _attr_whitelist = ['_obj_', '_df_']

    def __init__(self, obj):
        self._obj_ = obj

    def __getattr__(self, name):
        return getattr(self._obj_, name)

    def __setattr__(self, name, value):
        if name in self._attr_whitelist:
            object.__setattr__(self, name, value)
        setattr(self._obj_, name, value)

    def __dir__(self):
        return dir(self._obj_)

    def _eval(self, expr):
        if is_thunk(expr):
            expr = injected(self._df_, expr)
        return expr

    def __repr__(self):
        return repr(self._obj_)


def _magic_wrapped(method_name):
    def f(self, *args, **kwargs):
        if args:
            args = (self._eval(args[0]),) + args[1:]
        method = getattr(self._obj_, method_name)
        result = method(*args, **kwargs)
        return _maybe_add_magic(result)
    return f


def add_magic_wrapped_methods(methods):
    def f(cls):
        for method in methods:
            setattr(cls, method, _magic_wrapped(method))
        return cls
    return f


def _magic_indexer(name):
    def getter(self):
        prop = getattr(self._obj_, name)
        return MagicIndexer(self._df_, prop)
    return getter


@add_magic_wrapped_methods(frame_methods + indexer_methods + agg_methods)
class MagicFrame(BaseMagic, DataFrame):
    def __init__(self, df):
        self._obj_ = self._df_ = df

    loc = property(_magic_indexer('loc'))
    iloc = property(_magic_indexer('iloc'))
    ix = property(_magic_indexer('ix'))
    T = property(_magic_wrapped('transpose'))


@add_magic_wrapped_methods(indexer_methods)
class MagicIndexer(BaseMagic):
    def __init__(self, df, obj):
        self._df_ = df
        self._obj_ = obj


@add_magic_wrapped_methods(frame_methods + agg_methods + groupby_methods)
class MagicGroupBy(BaseMagic):
    def _eval(self, expr):
        if is_thunk(expr):
            return lambda df: injected(df, expr)
        return expr
