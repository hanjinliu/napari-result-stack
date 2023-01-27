__version__ = "0.0.1"

from napari_result_stack._register_types import register_all
from napari_result_stack.factory import get_factories
from napari_result_stack.types import Stored
from napari_result_stack.widgets import QResultViewer, create_dock_widget

register_all()

del register_all


__all__ = ["QResultViewer", "get_factories", "Stored", "create_dock_widget"]
