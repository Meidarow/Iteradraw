"""
Segmented-least-recently-accessed Cache implementation (final)

"""
import threading

class ByteCache(ICache):
    """
    SLRU cache implementation for images, specifically storing them as bytes.
    """

    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def __contains__(self, item):
        with self._lock:
            return item in self._data

    def get(self, key):
        with self._lock:
            return self._data.get(key, None)

    def put(self, key, data):
        with self._lock:
            self._data[key] = data
