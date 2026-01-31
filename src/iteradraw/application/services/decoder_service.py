from PySide6.QtCore import QRunnable, QThreadPool, QObject, Signal

from iteradraw.infrastructure.graphics.image_decoder import ImageDecoder
from iteradraw.interfaces import ICache


class DecodeJob(QRunnable):
    """
    Defines a single decode job.
    """
    class _Signals(QObject):
        finished = Signal(str)
        error = Signal(str, str)

    def __init__(self, cache, path):
        super().__init__()
        self.cache = cache
        self.path = path
        self.signals = self._Signals()

    def run(self):
        try:
            with ImageDecoder(self.cache) as decoder:
                decoder.load_image(image_path=self.path)
            self.signals.finished.emit(f"{self.path} successfully decoded")
        except Exception as e:
            self.signals.error.emit(str(self.path), str(e))

class DecoderService(QObject):
    """

    """
    image_ready = Signal(str)
    image_failed = Signal(str, str)

    def __init__(self, cache: ICache):
        super().__init__()
        self.cache = cache
        self.pool = QThreadPool().globalInstance()
        self.pool.setMaxThreadCount(2)

    def decode_image(self, path):
        job = DecodeJob(cache=self.cache, path=path)
        job.signals.finished.connect(self.image_ready)
        job.signals.error.connect(self.image_failed)
        self.pool.start(job)
