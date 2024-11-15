import pytest

from pheweb.serve.components.model import stateful_sublist

@pytest.mark.unit
def test_stateful_sublist() -> None:
    """Test optional float.

    @return: None
    """
    test_1_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    test_2_list = [1, 2]
    empty_list = []

    get_next = stateful_sublist(3)
    assert get_next(test_1_list) == [1, 2, 3]
    assert get_next(test_1_list) == [4, 5, 6]
    assert get_next(test_1_list) == [7, 8, 9]
    assert get_next(test_1_list) == [10, 1, 2]
    assert get_next(test_1_list) == [3, 4, 5]
    assert get_next(test_1_list) == [6, 7, 8]
    assert get_next(test_1_list) == [9, 10, 1]
    assert get_next(test_1_list) == [2, 3, 4]

    with pytest.raises(AssertionError) as excinfo:
        assert get_next(empty_list) == [1,2,1]
    assert "sublist size n=3 is greater than length=0" in str(excinfo.value)

    with pytest.raises(AssertionError) as excinfo:
        assert get_next(empty_list) == [1,2,1]
    assert "sublist size n=3 is greater than length=0" in str(excinfo.value)
    
        
    get_next = stateful_sublist(2)
    assert get_next(test_2_list) == [1, 2]
    assert get_next(test_2_list) == [1, 2]


    get_next = stateful_sublist(1)
    assert get_next(test_2_list) == [1]
    assert get_next(test_2_list) == [2]
    assert get_next(test_2_list) == [1]
    assert get_next(test_2_list) == [2]

