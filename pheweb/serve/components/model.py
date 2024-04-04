from dataclasses import dataclass, field, replace
from flask import Blueprint
from typing import List, Optional, Dict
from typing import TypeVar, List, Callable
import abc
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.WARNING)

@dataclass
class ComponentStatus:
    is_okay : bool
    messages : List[str] = field(default_factory=list)
    details : Dict[str,'ComponentStatus'] = field(default_factory=dict)

    @staticmethod
    def from_exception(ex: Exception):
        return ComponentStatus(is_okay=False, messages=[str(ex)])

class ComponentCheck:
    def get_name(self,) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    def get_status(self,) -> ComponentStatus:
        raise NotImplementedError


def total_check(check: ComponentCheck) -> ComponentStatus:
    """
    Make checks are total with respect
    to exceptions.

    If there is an exception a failed status
    is created with the name of the check and
    a message with exception is returned.

    :param check check to run

    :returns a tuple containing (name of check, result of check)
    """
    try:
        status=check.get_status()
    except Exception as ex:
        logger.exception(ex)
        logger.error(ex)
        status=ComponentStatus.from_exception(ex)
    return status

T = TypeVar('T')
def stateful_sublist(n : int) -> Callable[[List[T]], List[T]]:
    """
    Creates a closure function that generates a sublist of a given data
    sequence, maintaining internal state to remember the last index it
    accessed. On each call, it returns the next 'n' elements from the
    data sequence, wrapping around to the beginning of the sequence if
    the end is reached. This allows for iterative, overlapping sublists
    to be retrieved across calls.

    Parameters:
    - n (int): The number of elements to be included in each
      sublist. It is assumed that 'n' is less than or equal to the
      length of the data sequence provided in subsequent calls.

    Returns:
    - inner (function): A function that takes a single argument,
      'data', which is the sequence from which sublists are to be
      extracted. This function maintains the state of 'index', which
      tracks the current position in 'data' for the next sublist to
      begin. It checks the length of 'data' to ensure it is at least
      'n' and asserts an error if 'n' is greater than the length of
      'data'. When called, it returns the next 'n' elements as a
      sublist, adjusting 'index' for the next call, and wraps around
      the sequence if necessary.

    Raises:
    - AssertionError: If 'n' is greater than the length of the data
      sequence provided to the inner function.

    Example:
    >>> data_sequence = [1, 2, 3, 4, 5]
    >>> get_sublist = stateful_sublist(3)
    >>> print(get_sublist(data_sequence))
    [1, 2, 3]
    >>> print(get_sublist(data_sequence))
    [4, 5, 1]
    """
    state = [0]
    def inner(data: List[T]) -> List[T]:
        nonlocal state
        index = state[0]
        length = len(data)
        assert length >= n, f"sublist size n={n} is greater than length={length}"
        if index + n > length:
            result = data[index:index + n] + data[:index + n - length]
        else:
            result = data[index:index + n]
        index = (n + index) % length
        state[0] = index
        return result
    return inner

class CompositeCheck(ComponentCheck):
    
    def __init__(self,
                 checks : Optional[List[ComponentCheck]]=None,
                 max_checks : int = None):
        # wraped in list
        self.subset=[lambda x : x] if max_checks is None else [stateful_sublist(max_checks)]
        self.checks=checks if checks is not None else []

    def get_name(self,) -> str:
        return ",".join(map(lambda check : check.get_name(),self.checks))

    def add_check(self,check: ComponentCheck):
        self.checks.append(check)

    def clear_checks(self):
        self.checks.clear()
    
    def get_status(self,) -> ComponentStatus:
        result=ComponentStatus(is_okay=True)
        failure_names = []
        for check in self.subset[0](self.checks):
            logger.info(f"checking {check}")
            status = total_check(check)
            result.is_okay = status.is_okay and result.is_okay
            if status.is_okay is False:
                failure_names.append(check.get_name())
            result.details[check.get_name()] = replace(status)
        names=",".join(failure_names)
        count=len(failure_names)
        result.messages = [f"""{count} failures : [{names}]"""]
        return result

@dataclass
class ComponentDTO:
    blueprint: Blueprint
    status_check: ComponentCheck
