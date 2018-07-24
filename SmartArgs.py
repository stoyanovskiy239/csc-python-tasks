from copy import deepcopy
from functools import namedtuple, wraps

Isolated = namedtuple('Isolated', '')
# @smart_args
# def func(*, x = Isolated())
#
# Force `func` to work with a deep copy of passed `x`.
# If `x` is not passed, `KeyError` is raised.

Evaluated = namedtuple('Evaluated', 'evaluate')
# @smart_args
# def func(*, x = Evaluated(func_without_args))
#
# Default value of `x`, defined by call of `func_without_args`, will be
# evaluated on each call of `func` (if `x` is not passed in that call).
# Use of `Evaluated(Isolated)` raises `AssertionError`.


def smart_args(func):
    """Decorate `func` to provide support of `Isolated` and `Evaluated`.

    Args:
        func ('function'): function to decorate

    Returns:
        function: `wrapper` for `func`, decorated with `functools.wraps`

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrap `func` and tweak its keyword arguments.

        This function looks for use of `Isolated` and `Evaluated` among
        default values (defval) of `func`'s keyword arguments (kwargs).

        All kwargs with `Isolated` defval are assigned to deep copies
        of corresponding passed values. It's assumed that all such kwargs
        were passed, therefore lack of one triggers raise of `KeyError`.

        All kwargs with `Evaluated(func_without_args)` defval, that weren't
        passed in current call of `func` are assigned to return values
        of corresponding `func_without_args()` calls.
        If it appears, that `Isolated` has been passed into `Evaluated` as
        `func_without_args`, `AssertionError` is raised.

        Args:
            args (tuple): positional arguments of `func` call
            kwargs (dict): keyword arguments of `func` call

        Returns:
            function: call `func(*args, **kwargs)` with tweaked `kwargs`

        """

        for key, def_kwarg in func.__kwdefaults__.items():
            if isinstance(def_kwarg, Isolated):
                kwargs[key] = deepcopy(kwargs[key])
            elif (key not in kwargs) and isinstance(def_kwarg, Evaluated):
                assert not isinstance(def_kwarg.evaluate, Isolated)
                kwargs[key] = def_kwarg.evaluate()
        return func(*args, **kwargs)

    return wrapper
