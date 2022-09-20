from typing import TypeVar, Generic, Union, Optional
from collections.abc import Callable

T = TypeVar("T")
P = TypeVar("P")


class Var(Generic[T]):
    def __init__(self, value: T) -> None:
        self.__value__ = value
        self.on_change = set()
        pass

    def __call__(self, value: T):
        self.__old_value__ = self.__value__
        self.__value__ = value
        list(map(lambda f: f(None, self, self.__old_value__, value), self.on_change))

    def __str__(self):
        return "Var({0})".format(self.__value__)

    def __add__(self, other):
        return Var(self.__value__ + other.__value__)

    def __sub__(self, other):
        return Var(self.__value__ - other.__value__)

    def __mul__(self, other):
        return Var(self.__value__ * other.__value__)

    def __pow__(self, other):
        return Var(self.__value__**other.__value__)

    def __truediv__(self, other):
        return Var(self.__value__ / other.__value__)

    def __floordiv__(self, other):
        return Var(self.__value__ // other.__value__)

    def __mod__(self, other):
        return Var(self.__value__ % other.__value__)

    def __lshift__(self, other):
        return Var(self.__value__ << other.__value__)

    def __lshift__(self, other):
        return Var(self.__value__ << other.__value__)

    def __lshift__(self, other):
        return Var(self.__value__ << other.__value__)

    def __rshift__(self, other):
        return Var(self.__value__ >> other.__value__)

    def __and__(self, other):
        return Var(self.__value__ & other.__value__)

    def __or__(self, other):
        return Var(self.__value__ | other.__value__)

    def __or__(self, other):
        return Var(self.__value__ | other.__value__)

    def __xor__(self, other):
        return Var(self.__value__ ^ other.__value__)

    def __invert__(self):
        return Var(~self.__value__)

    def __eq__(self, other):
        return self.__value__ == other.__value__

    def __ne__(self, other):
        return self.__value__ != other.__value__

    def __lt__(self, other):
        return self.__value__ < other.__value__

    def __le__(self, other):
        return self.__value__ <= other.__value__

    def __gt__(self, other):
        return self.__value__ > other.__value__

    def __ge__(self, other):
        return self.__value__ >= other.__value__


class Fn(Var, Generic[T]):
    def __init__(self, __f__: Callable[..., T], **kwargs) -> None:
        self.__f__ = __f__
        self.kwargs = kwargs
        self.on_change = set()
        for (arg_name, arg_var) in self.kwargs.items():

            def cb(an, av):
                def _cb(orig_arg_name, orig_arg_var, prev, next):
                    new_arg_name = an + "." + orig_arg_name if orig_arg_name else an
                    return self.var_changed(new_arg_name, orig_arg_var, prev, next)

                return _cb

            arg_var.on_change.add(cb(arg_name, arg_var))

    def var_changed(self, arg_name, arg_var, prev, next):
        for cb in self.on_change:
            cb(arg_name, arg_var, prev, next)

    def __call__(self) -> T:
        return self.__value__

    def __str__(self):
        return "Fn({0})".format(self.__value__)

    def __getattr__(self, attr):
        if attr == "__value__":
            return self.__f__(**{k: v.__value__ for k, v in self.kwargs.items()})
        else:
            return self.__dict__.get(attr)

    def __setattr__(self, attr, value):
        if attr == "__value__":
            raise ValueError("cannot directly set __value__ for devrived values")
        else:
            self.__dict__[attr] = value


class Seq(Generic[T]):
    def __init__(
        self, __f__: Callable[..., T], length: Optional[int] = None, **kwargs
    ) -> None:
        self.__f__ = __f__
        self.on_change = set()
        self.kwargs = kwargs
        self.length = length

        for (arg_name, arg_var) in self.kwargs.items():

            def cb(an, av):
                def _cb(orig_arg_name, orig_arg_var, prev, next):
                    new_arg_name = an + "." + orig_arg_name if orig_arg_name else an
                    return self.var_changed(new_arg_name, orig_arg_var, prev, next)

                return _cb

            arg_var.on_change.add(cb(arg_name, arg_var))

        pass

    def var_changed(self, arg_name, arg_var, prev, next):
        for cb in self.on_change:
            cb(arg_name, arg_var, prev, next)

    def __getitem__(self, key) -> T:

        if isinstance(key, slice):
            indices = range(*key.indices(self.length))
            return [
                self.__f__(self, **{k: v.__value__ for k, v in self.kwargs.items()})(i)
                for i in indices
            ]

        if type(key) is not int:
            raise ValueError("cannot access collection with non-int index")

        result = self.__f__(self, **{k: v.__value__ for k, v in self.kwargs.items()})(
            key
        )
        return result

    def __getattr__(self, attr):
        if attr == "__value__":
            return self
        else:
            return self.__dict__.get(attr)

    def __len__(self) -> int:
        if type(self.length) == int:
            return self.length
        else:
            raise TypeError("this collection does not specify a length")

    def __iter__(self):
        return SequenceIterator[T](
            self.__f__(self, **{k: v.__value__ for k, v in self.kwargs.items()}),
            length=self.length,
        )

    def __str__(self):
        return "Seq<{0}>".format(self.length if self.length != None else "Unbounded")


class SequenceIterator(Generic[T]):
    """Iterator class"""

    def __init__(self, f: Callable[..., T], length: int = None):
        self.__f__ = f
        self._index = 0
        self._length = length

    def __next__(self) -> T:
        if type(self._length) is not int or self._index < self._length:
            result = self.__f__(self._index)
            self._index += 1
            return result
        elif type(self._length) is int and self._index >= self._length:
            raise StopIteration


def Val(v: Union[Var[T], Fn[T]]) -> T:
    return v.__value__


Element = Union[Var, Seq, Fn]
