from mmap import mmap, ACCESS_READ
from pathlib import Path

from PIL import Image

class ImageDecoder:
    """
    Implements a Pillow-SIMD-based image decoder.

    """
    def __init__(self, cache) -> None:
        self.cache = cache

    def __enter__(self) -> "ImageDecoder":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False

    def load_image(self, image_path: str | Path) -> None:
        path = Path(image_path)
        # suffix = path.suffix.lower()
        # if suffix in {".jp2", ".j2k", ".jpx"}:
        #     image = self.load_raw_image_glymur(path)
        # else:
        raw_bytes = self.load_raw_image_psimd(path)
        self.cache.put(path, raw_bytes)

    @staticmethod
    def load_raw_image_psimd(path: Path) -> bytes:
        """Load image with pillow-simd, return as array"""
        with open(path, "rb") as f:
            with mmap(f.fileno(), 0, access=ACCESS_READ) as m:
                with Image.open(m) as img:
                    return img.convert("RGBA").tobytes()

    # def load_raw_image_glymur(path: Path) -> np.ndarray:
    #     TODO move from pyav to glymur for jp2

    #     """Load image with imageio.v3 with pyav, return as array"""
    #     # PYAV returns a list of frames; we want the first (and only) one.
    #     import av  # imported lazily – only needed for JP2
    #
    #     container = av.open(str(path))
    #     frame = next(container.decode(video=0))  # first frame
    #     container.close()
    #     image = frame.to_ndarray(format="rgb24")  # (h, w, 3) uint8
    #     return image