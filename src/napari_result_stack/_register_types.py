from magicgui import register_type

from napari_result_stack.types import Stored, StoredValueComboBox


def register_all():
    register_type(
        Stored,
        widget_type=StoredValueComboBox,
        # choices=Stored._get_choice,
        return_callback=Stored._store_value,
    )
