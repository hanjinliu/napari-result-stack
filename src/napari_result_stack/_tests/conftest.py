import pytest

from napari_result_stack.types import Stored, StoredMeta


@pytest.fixture
def stored():
    """
    Provide a ``Stored`` type and cleanup the instance list after the test.

    Following two tests both use ``Stored[int]`` but the second one will not
    be contaminated with the variables defined in the first one.

    >>> def test_something_1(stored):
    ...     @magicgui
    ...     def func1(): -> stored[int]:
    ...         ...

    >>> def test_something_2(stored):
    ...     @magicgui
    ...     def func2(): -> stored[int]:
    ...         ...

    """

    class _DummpyStorage(Stored):
        _dummy_keys = set()

        @classmethod
        def _class_getitem(cls, value):
            out = Stored._class_getitem(value)
            _DummpyStorage._dummy_keys.add(out._hash_key())
            return out

    try:
        yield _DummpyStorage
    finally:
        key_to_pop = []
        for key in StoredMeta._instances.keys():
            if key in _DummpyStorage._dummy_keys:
                key_to_pop.append(key)
        for key in key_to_pop:
            StoredMeta._instances.pop(key)
