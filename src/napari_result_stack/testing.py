from contextlib import contextmanager

from napari_result_stack.types import Stored, StoredMeta


@contextmanager
def temp_storage():
    """
    Provide a Stored type and cleanup the instance list outside the context.

    In the following example, storage will be safely removed.

    >>> def test_something():
    ...     with temp_storage():
    ...         @magicgui
    ...         def func1(): -> stored[int]:
    ...             ...
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
