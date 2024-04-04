import pytest

from pheweb.serve.components.health.health_check import timed_selector

@pytest.mark.unit
def test_timed_selector_one() -> None:
    selector=timed_selector(10)
    assert 1 == selector(lambda: 1,lambda : 2)
    assert 2 == selector(lambda: 1,lambda : 2)

@pytest.mark.unit
def test_timed_selector_zero() -> None:
    selector=timed_selector(0)
    assert 1 == selector(lambda: 1,lambda : 2)
    assert 1 == selector(lambda: 1,lambda : 2)

@pytest.mark.unit
def test_timed_selector_none() -> None:
    selector=timed_selector(None)
    assert 1 == selector(lambda: 1,lambda : 2)
    assert 1 == selector(lambda: 1,lambda : 2)
