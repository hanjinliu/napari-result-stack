import napari
import numpy as np
from magicgui import magicgui
from napari.types import ImageData
from napari_macrokit import get_macro

from napari_result_stack import Stored, create_dock_widget

if __name__ == "__main__":
    viewer = napari.Viewer()
    create_dock_widget()
    macro = get_macro("example")

    @magicgui
    @macro.record
    def random_image(shape: tuple[int, int] = (80, 100)) -> ImageData:
        return np.random.random(shape).astype(dtype=np.float32)

    @magicgui
    @macro.record
    def average(img: ImageData) -> Stored[float]:
        return float(img.mean())

    @magicgui
    @macro.record
    def subtract_constant_value(
        img: ImageData, const: Stored[float]
    ) -> ImageData:
        return img - const

    @magicgui
    def show_macro() -> Stored[str]:
        return repr(macro)

    viewer.window.add_dock_widget(
        random_image, area="right", name="Random Image"
    )
    viewer.window.add_dock_widget(average, area="right", name="Average")
    viewer.window.add_dock_widget(
        subtract_constant_value, area="right", name="Subtract"
    )
    viewer.window.add_dock_widget(show_macro, area="right", name="Show macro")

    napari.run()
