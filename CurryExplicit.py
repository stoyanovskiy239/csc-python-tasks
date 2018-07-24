def curry_explicit(func, arity):
    """Apply currying to target function.

    This function makes `curried` function from `func` and freezes its arity.
    Passing negative `arity` raises `AssertionError`.

    Args:
        func ('function'): function to apply currying
        arity (int): required arity

    Returns:
        function: curried `func` with frozen `arity`

    """
    assert arity >= 0

    def curried(*args):
        """Curried version of `func`.

        Partial application is supported.
        Return value will be received as soon as number of passed arguments
        will be equal to `arity`.
        Exceeding `arity` raises `TypeError`.

        """
        n_of_args = len(args)
        if n_of_args < arity:
            return lambda *more_args: curried(*args, *more_args)
        if n_of_args == arity:
            return func(*args)
        raise TypeError(curry_error(func, arity, n_of_args))

    return curried


def uncurry_explicit(func, arity):
    """Apply uncurrying to target function.

    This function makes `uncurried` function with fixed arity from `func`.
    Passing negative `arity` raises `AssertionError`.

    Args:
        func ('function'): function to apply uncurrying
        arity (int): required arity

    Returns:
        function: uncurried `func` with frozen `arity`

    """
    assert arity >= 0

    def uncurried(*args):
        """Uncurried version of `func`.

        Excess or lack of arguments according to `arity` raises `TypeError`.

        """
        n_of_args = len(args)
        if n_of_args != arity:
            raise TypeError(uncurry_error(func, arity, n_of_args))
        if arity < 2:
            return func(*args)
        reduced = func(args[0])
        for arg in args[1:]:
            reduced = reduced(arg)
        return reduced

    return uncurried


# error messages format templates
ERR_MSG1 = '{}() takes {} argument{} but {} {} given'
ERR_MSG2 = '{}() missing {} arguments'


def curry_error(func, arity, n_of_args):
    """Auxiliary function for error message formatting."""
    verb = 'were' if n_of_args > 1 else 'was'
    _s = '' if arity is 1 else 's'
    return ERR_MSG1.format(func.__name__, arity, _s, n_of_args, verb)


def uncurry_error(func, arity, n_of_args):
    """Auxiliary function for error message formatting."""
    if n_of_args > arity:
        return ERR_MSG1.format(func.__name__, arity, 's', n_of_args, 'were')
    return ERR_MSG2.format(func.__name__, (arity - n_of_args))
