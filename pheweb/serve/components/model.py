from dataclasses import dataclass, field
from flask import Blueprint
from typing import List, Optional, Dict
import abc
import logging
import time

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)

@dataclass
class ComponentStatus:
    is_okay : bool
    messages : List[str] = field(default_factory=list)
    details : Dict[str,'ComponentStatus'] = field(default_factory=dict)
    time: Optional[float] = None

    @staticmethod
    def from_exception(ex: Exception,time : Optional[float]=None):
        logger.exception(ex)
        return ComponentStatus(is_okay=False, messages=str(ex), time=time)

class ComponentCheck:
    def get_name(self,) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    def get_status(self,) -> ComponentStatus:
        raise NotImplementedError


    
class CompositeCheck(ComponentCheck):
    
    def __init__(self, checks : Optional[List[ComponentCheck]]=None):
        self.checks=checks if checks is not None else []

    def get_name(self,) -> str:
        return ",".join(map(lambda check : check.get_name(),self.checks))

    def add_check(self,check: ComponentCheck):
        self.checks.append(check)

    def clear_checks(self):
        self.checks.clear()
    
    def get_status(self,) -> ComponentStatus:
        result=ComponentStatus(is_okay=True)
        component_start = time.perf_counter()
        failure_names = []
        for check in self.checks:
            check_start = time.perf_counter()
            status = check.get_status()
            check_end = time.perf_counter()            
            if status.time is None:
                status.time = check_end - check_start
            result.is_okay = status.is_okay and result.is_okay
            if result.is_okay is False:
                failure_names.append(check.get_name())
            result.details[check.get_name()] = status
        component_end = time.perf_counter() 
        result.time=component_end - component_start
        names=",".join(failure_names)
        count=len(failure_names)
        result.messages = [f"""{count} failures : [{names}]"""]
        return result

    
@dataclass
class ComponentDTO:
    blueprint: Blueprint
    status_check: ComponentCheck
