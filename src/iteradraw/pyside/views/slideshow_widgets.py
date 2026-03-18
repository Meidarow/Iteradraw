from PySide6.QtCore import Slot, Qt, QPointF
from PySide6.QtGui import QPainter, QPixmap, QPalette, QColor
from PySide6.QtWidgets import QWidget



class ImageViewerWidget(QWidget):
    """
    Slideshow-screen widget.

    Acts as a simple image viewer, with essential user interactions
    through key bindings.

    Expected behavior:
        - Arbitrary image loads without distortion at a compatible resolution;
        - Image's top corner is positioned to divide the blank-space in half
        to either side of the image (letter/pillar-box);
        - Transformation matrices are used to compute translation and scale changes
        made by the user;

    Constraints:
        - Only knows and owns the currently displayed image and its matrix;
        - Does not keep track of image index/order;

    Key Interactions:
        - Zoom: User can change scale incrementally via mouse-wheel and + or -;
        - Translation: User can drag the image at any scale with the left mouse
        button pressed;

    Context menu actions:
        - Open image in file explorer;
        - Show image in containing folder;
    """

    def __init__(self, /, parent=None, cache = "ICache"):
        super().__init__(parent)
        self._scale_factor = 1
        self.cache = cache
        self.palette = QPalette()
        self.palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(self.palette)
        self._image = QPixmap()

    @Slot()
    def set_image(self, image_path):
        self._image.load(image_path)
        self.update()

    def paintEvent(self, arg_0):
        """
        Scales and paints the image, given current window size.
        Uses smooth transform for scaling as fasttransform uses aliased scaling, creating blobby shapes.
        """
        self._update_vertex()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(self._vertex, self._image.scaled(self.rect().size(),
                                                            aspectMode=Qt.AspectRatioMode.KeepAspectRatio,
                                                            mode =Qt.TransformationMode.SmoothTransformation))

    def _update_vertex(self):
        """
        Calculates QPoint to paint image letter/pillar-boxed to fit screen.
        """
        pillar_width = abs(self.width() -  self._image.scaled(self.rect().size(),
                                                                  Qt.AspectRatioMode.KeepAspectRatio).width())/2
        letterbox_height = abs(self.height() - self._image.scaled(self.rect().size(),
                                                                      Qt.AspectRatioMode.KeepAspectRatio).height())/2
        self._vertex = QPointF(pillar_width, letterbox_height)

    def _scale_image(self, width, height):
        pass