from typing import Callable, TypeVar, Type, Optional, Generic

class OptionalError(Exception):
    pass


class NoneValueError(OptionalError):
    pass


class Optional(object):
    """
    implementation of Optional like in the Java
    close to Maybe monad
    """
    def __init__(self, value: object):
        self._value = value

    @staticmethod
    def of(value:object):
        return Optional(value)

    def get(self):
        if self._value is None:
            raise NoneValueError('Called get on empty optional')
        return self._value

    def get_or_else(self, default: object):
        try:
            return self.get()
        except NoneValueError:
            return default

    def get_or_else_get(self, default_callable: callable):
        try:
            return self.get()
        except NoneValueError:
            return default_callable()

    def get_or_raise(self, exception, *args, **kwargs):
        if self._value is None:
            raise exception(*args, **kwargs)
        else:
            return self._value

    def map(self, transform_callable: callable):
        if self._value is None:
            return type(self)(None)
        else:
            return type(self)(transform_callable(self._value))

    def filter(self, transform_callable: callable):
        if transform_callable(self._value):
            return type(self)(None)
        else:
            return type(self)(self._value)

    def flat_map(self, transform_callable: callable):
        if isinstance(self._value, type(self)):
            return self._value.flat_map(transform_callable)
        else:
            return type(self)(self._value).map(transform_callable)

    def if_present(self, func: callable):
        if self._value is not None:
            func(self._value)

    def if_present_or_else(self, apply: callable, apply_else: callable):
        if self._value is not None:
            apply(self._value)
        else:
            apply_else(self._value)

    def or_else_throw(self, e):
        if self._value is not None:
            return self.get()
        else:
            raise Exception(e)

    def is_present(self) -> bool:
        return self._value is not None

    def __bool__(self):
        return self.is_present()

    def __nonzero__(self):
        return self.__bool__()

    def __str__(self):
        if self._value is None:
            return 'Optional empty'
        else:
            return 'Optional of: {}'.format(self._value)

    def __repr__(self):
        return 'Optional({})'.format(repr(self._value))

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Optional) and o._value == self._value

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    @staticmethod
    def empty():
        return Optional(None)

