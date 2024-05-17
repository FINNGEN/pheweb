"""This module health_check contains DAO implementations for HealthDAO"""
import json
import logging
import socket
import requests
from pheweb.serve.components.model import ComponentStatus, total_check
from pheweb.serve.components.health.dao import HealthDAO, HealthSummary
from pheweb.serve.components.health.service import get_status_check
from datetime import datetime, timedelta
from typing import Callable, Optional

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)

REQUEST_TIMEOUT = 10  # 10 seconds


class HealthTrivialDAO(HealthDAO):
    """
    This is a trival check that always returns okay.
    It is meant to be a safe default DAO.
    """

    def get_summary(self, ) -> HealthSummary:
        return HealthSummary(True, {})

    def get_status(self, ) -> ComponentStatus:
        return ComponentStatus(True, [])

def timed_selector(minutes: Optional[int] = None,
                   now: Callable[[], datetime] = lambda: datetime.now()) -> Callable[[Callable[[], any], Callable[[], any]], any]:
    """
    Creates and returns a selector function that decides between two actions based on time elapsed.

    The selector function, when called, executes and returns the result of one of two input functions (a or b)
    depending on the time elapsed since the last time function a was executed. If the elapsed time is greater
    than the specified 'minutes', or if 'minutes' is None (indicating no time restriction), function a is executed.
    Otherwise, function b is executed. The time of the last execution of function a is internally tracked.

    Args:
        minutes (int, optional): The minimum number of minutes that must elapse between successive executions of
                                 function a. If None, function a is executed without time restriction. Defaults to None.
        now (callable, optional): A function that returns the current time. This parameter primarily exists to facilitate
                                  testing with a fixed or mock time. Defaults to `datetime.now`.

    Returns:
        callable: A function that takes two callables (a and b) as its arguments. When called, it selects and executes
                  either a or b based on the elapsed time since the last execution of a as determined by the 'minutes' parameter.

    Example:
        def action_a():
            return "Action A executed"

        def action_b():
            return "Action B executed"

        # Create a timed selector with a 5-minute restriction between executions of action_a
        selector = timed_selector(minutes=5)

        # Immediately executing action_a because it's the first call
        print(selector(action_a, action_b))  # Outputs: "Action A executed"

        # Subsequent calls within 5 minutes will execute action_b
        # If called after 5 minutes, action_a will be executed again.
    """
    state = [None]

    def f(a, b):
        nonlocal state
        last_call_time=state[0]
        current_time = now()
        if minutes is None:
            return a()
        elif last_call_time is None or current_time - last_call_time > timedelta(minutes=minutes):
            state[0] = current_time
            return a()
        else:
            return b()
        
    return f

class HealthSimpleDAO(HealthTrivialDAO):
    """
    This is a simple check that always returns
    the normal checks.
    """
    def __init__(self, minutes=30):
        self.minutes=minutes
        self.selector=[timed_selector(minutes)]
        
    def get_summary(self, ) -> HealthSummary:
        """
        Run the health check and return
        a boolean indicating if the test
        has passed and a map with a map
        of status checks.

        :returns a dictionary with the service statuses
        """
        def run_summary():
            checks = get_status_check()
            messages = dict(map(lambda c: (c.get_name(), total_check(c)), checks))
            is_okay = all(message.is_okay for message in messages.values())
            return HealthSummary(is_okay, messages)
        def okay_summary():
            return HealthSummary(True, {})
        selector=self.selector[0]
        return selector(run_summary, okay_summary)

class HealthNotificationDAO(HealthSimpleDAO):
    """
    Alerting health check.
    """

    def __init__(self, server_name=socket.gethostname(), url=None):
        """
        Make a healthcheck manager.

        """
        self.server_name = server_name
        self.url = url
        self.status = None

    def send(self, messages) -> ComponentStatus:
        """
        Post message with a payload of the messages
        """
        headers = {"Content-type": "application/json"}
        json_data = {"text": json.dumps({"messages": messages})}
        response = requests.post(self.url,
                                 headers=headers,
                                 json=json_data,
                                 timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            result = ComponentStatus(True, [])
        else:
            result = ComponentStatus(False, [f"{response.status_code} {response.text}"])
        return result

    def get_summary(self, ) -> HealthSummary:
        summary = super(HealthNotificationDAO, self).get_summary()
        if (self.status is not None
            and summary.is_okay is False
            and self.url is not None):
            logger.info(summary.to_json())
            self.send(summary.to_json())
        return summary

    def get_status(self, ) -> ComponentStatus:
        """
        get the status

        send a message that the service is starting
        use the sucess of sending this message as
        the status of this component.
        """
        if self.status is None:
            if self.url is None:
                self.status = super(HealthSimpleDAO, self).get_status()
            else:
                start_message = f"starting {self.server_name}"
                self.status = self.send(start_message)
        return self.status


def default_dao():
    """
    Return default DAO implementation.
    """
    return HealthTrivialDAO()
