import pytest

from config.helper import key_must_exist, singleton, str_to_int_list


class TestKeyMustExist:
    def test_existing_key(self):
        # Test for an existing key
        assert key_must_exist("a")

    def test_non_existing_key(self):
        # Test for a non-existing key
        with pytest.raises(ValueError, match="key does not exist"):
            key_must_exist("non_existing_key")


class TestSingletonDecorator:
    @singleton
    class SingletonDummyClass:
        def __init__(self, *args, **kwargs):
            pass

    def test_singleton_instance(self):
        # Test whether multiple instances of singleton class return the same object
        instance1 = self.SingletonDummyClass()
        instance2 = self.SingletonDummyClass()
        assert instance1 is instance2


class TestStrToIntList:
    def test_empty_string(self):
        # Test for an empty string
        assert str_to_int_list("") == []

    def test_single_integer(self):
        # Test for a single integer string
        assert str_to_int_list("5") == [5]

    def test_multiple_integers(self):
        # Test for a string containing multiple integers separated by commas
        assert str_to_int_list("1,2,3,4,5") == [1, 2, 3, 4, 5]

    def test_invalid_input(self):
        # Test for invalid input type
        with pytest.raises(ValueError, match="invalid literal"):
            str_to_int_list("1,2,3,a,5")

    def test_negative_numbers(self):
        # Test for negative numbers
        assert str_to_int_list("-1,-2,-3,-4,-5") == [-1, -2, -3, -4, -5]

    def test_whitespace(self):
        # Test for string containing whitespace
        assert str_to_int_list(" 1 ,  2 , 3 , 4 , 5 ") == [1, 2, 3, 4, 5]
