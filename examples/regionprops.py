import napari
import numpy as np
import pandas as pd
from magicgui import magicgui
from napari.types import ImageData, LabelsData
from skimage.measure import regionprops_table

from napari_result_stack import Stored, create_dock_widget

if __name__ == "__main__":
    viewer = napari.Viewer()

    viewer.add_image(np.random.random((100, 100)))  # sample image

    labels = np.zeros((100, 100), dtype=np.int32)
    labels[10:23, 10:23] = 1
    labels[7:23, 80:95] = 2
    labels[77:93, 14:21] = 3
    labels[57:70, 57:70] = 4
    viewer.add_labels(labels)

    # Create a dock widget with a QResultViewer
    create_dock_widget()

    @magicgui
    def run_regionprops(
        img: ImageData, labels: LabelsData
    ) -> Stored[pd.DataFrame]:
        table = regionprops_table(
            labels, img, properties=["label", "area", "mean_intensity"]
        )
        return pd.DataFrame(table)

    @magicgui
    def print_summary(df: Stored[pd.DataFrame]) -> pd.DataFrame:
        out = df.apply([np.mean, np.std])
        print(out)

    viewer.window.add_dock_widget(
        run_regionprops, area="right", name="Regionprops"
    )
    viewer.window.add_dock_widget(
        print_summary, area="right", name="Summarize"
    )
    napari.run()
