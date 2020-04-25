import time
from decimal import Decimal, ROUND_UP
from functools import wraps
from decorator import decorator
from functools import singledispatch


def exception(logger, reraise=False):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur

    @param logger: The logging object
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"There was an exception in {func.__name__}")
            if reraise:
                raise

        return wrapper

    return decorator


@decorator
def warn_slow(func, logging, timelimit=60, *args, **kw):
    t0 = time.time()
    result = func(*args, **kw)
    dt = time.time() - t0
    if dt > timelimit:
        logging.warn('%s took %d seconds', func.__name__, dt)
    else:
        logging.info('%s took %d seconds', func.__name__, dt)
    return result


def parse(str, default):
    return try_parse(default, str)


@singledispatch
def try_parse(default, str):
    try:
        return type(default)(str)
    except:
        pass
    return default


@try_parse.register(Decimal)
def try_parse_decimal(default, str):
    try:
        return Decimal(str.replace(",", "."))
    except:
        pass
    return default