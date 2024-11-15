import abc
import typing

X = typing.TypeVar('X')


def nvl(value: typing.Optional[str],
        f: typing.Callable[[str], X]) -> typing.Optional[X]:
    """
    Wrapper to convert strings to a given type, where the
    empty string, or None is returned as None.

    :param value: string representing type X
    :param f: function from string to type X
    :return: X or None
    """
    if value is None:
        result = None
    elif value == "":
        result = None
    else:
        result = f(value)
    return result


def na(f: typing.Callable[[str], X]) -> typing.Callable[[str], typing.Optional[X]]:
    """
    Wrapper to handle NA values.
    """
    return lambda value: None if value == 'NA' or value == 'na' else f(value)


def only_ascii(value: str) -> str:
    """
    Remove non-ascci characters.
    """
    return "".join(char for char in value if ord(char) < 128)


class JSONifiable(object):
    @abc.abstractmethod
    def json_rep(self):
        """
           Return an object that can be jsonencoded.
        """
        raise NotImplementedError


class Kwargs(object):
    @abc.abstractmethod
    def kwargs_rep(self) -> typing.Dict[str, typing.Any]:
        """
           Return constructor parameters for object
           for shallow cloning.
        """
        raise NotImplementedError
