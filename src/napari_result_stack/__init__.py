__version__ = "0.0.1"

from napari_result_stack._register_types import register_all
from napari_result_stack.widgets import QResultViewer

register_all()

del register_all


__all__ = ["QResultViewer"]
