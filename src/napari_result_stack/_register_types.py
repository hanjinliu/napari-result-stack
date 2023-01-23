from magicgui import register_type

from napari_result_stack.types import Stored


def register_all():
    register_type(
        Stored, choices=Stored._get_choice, return_callback=Stored._store_value
    )
