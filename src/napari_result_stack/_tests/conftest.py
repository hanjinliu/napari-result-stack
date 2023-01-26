import pytest

from napari_result_stack.testing import temp_storage


@pytest.fixture
def stored():
    with temp_storage() as st:
        yield st
