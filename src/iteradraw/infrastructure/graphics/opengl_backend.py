import multiprocessing
import weakref
from collections import deque
from pathlib import Path

import moderngl_window as mglw
import moderngl_window.context.glfw
import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget


"""
OpenGL Backend for Draw-This.

This module defines the moderngl slideshow implementation.
It has one class and one function:

- RenderWindow:
Subclass of moderngl_window.WindowConfig, provides a series of methods to
control the slideshow, texture rendering, and accepts user commands.

- start_slideshow_ogl:
Runs a moderngl-based slideshow in a multiprocess.Process.

Usage
-----
This file is imported as a package according to the following:
    from drawthis import RenderWindow, start_slideshow_ogl
"""


class RenderTab(QOpenGLWidget):
    def __init__(self):
        super().__init__()


class RenderWindow(mglw.WindowConfig):
    """
    Subclass of moderngl_window.WindowConfig, additionally holds
    an image deque for the slideshow, a multiprocessing.Queue for
    cross-process communication and methods to dislpay images
    according to format.
    """

    gl_version = (3, 3)

    def __init__(self, queue, **kwargs):
        """
        Set queue, essential since class is limited to running
        on a subprocess, and image deque, for two-way navigation.
        """
        super().__init__(**kwargs)
        self.queue = queue
        self.images = None

        self._setup_shaders()
        self._setup_vao()

    # Event handlers

    def on_key_event(self, key, action, modifiers: KeyModifiers) -> None:
        """
        Cycle textures forwards with RIGHT_ARROW.
        Cycle textures backwards with LEFT_ARROW.
        End slideshow with LETTER_Q.
        """
        # TODO Remove IFs, implement function dict.
        # key_bindings_dict = {
        #
        # }
        if key == self.wnd.keys.RIGHT and action == self.wnd.keys.ACTION_PRESS:
            self.images.rotate(1)
            self._set_texture(self.images[0])

        if key == self.wnd.keys.LEFT and action == self.wnd.keys.ACTION_PRESS:
            self.images.rotate(-1)
            self._set_texture(self.images[0])

        if key == self.wnd.keys.Q and action == self.wnd.keys.ACTION_PRESS:
            self.on_close()

    def on_resize(self, width: int, height: int) -> None:
        """Rescale image to fit preserving aspect ratio"""
        if getattr(self, "_texture", None) is not None:
            self._scale_image()

    def on_render(self, time: float, frametime: float) -> None:
        """Render texture on the VAO"""
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.vao.render()

    def on_close(self) -> None:
        """Close window and signal resources end"""
        self.queue.put("session_ended")
        self.wnd.is_closing = True

    # Accessors

    @property
    def scaled_vertices(self):
        """Return horizontal and vertical scales to FIT image to window"""
        quad_scale_x, quad_scale_y = self.quad_scale
        return np.asarray(
            [
                # Maps UV coordinates to scaled NDC coordinates
                # (v coordinates are flipped to skip transposing images in PIL)
                -quad_scale_x,
                -quad_scale_y,
                0.0,
                1.0,
                quad_scale_x,
                -quad_scale_y,
                1.0,
                1.0,
                -quad_scale_x,
                quad_scale_y,
                0.0,
                0.0,
                quad_scale_x,
                quad_scale_y,
                1.0,
                0.0,
            ],
            dtype="f4",
        )

    # Private helpers

    def _setup_shaders(self):
        """Compile shaders"""
        try:
            self.prog = self.ctx.program(
                vertex_shader=parse_shader("basic.vert"),
                fragment_shader=parse_shader("basic.frag"),
            )
        except Exception as e:
            logger.error(
                msg=f"Unexpected error when compiling shaders: {e}",
                exc_info=True,
            )
            raise

    def _setup_vao(self):
        """Index triangles to quad and prepare the VA for displaying images"""
        # Defines the index order for two triangles that make up the quad
        ibo = self.ctx.buffer(np.asarray([0, 1, 2, 2, 1, 3], dtype="i4"))
        self.quad_scale = (1.0, 1.0)
        # Maps UV coordinates to NDC coordinates
        # (v coordinates are flipped to skip transposing images in PIL)
        self.vbo = self.ctx.buffer(self.scaled_vertices)
        self.vao = self.ctx.vertex_array(
            self.prog, [(self.vbo, "2f 2f", "in_vert", "in_uv")], ibo
        )

    def _set_texture(self, path: str | Path) -> None:
        """Load image from disk, send to GPU and scale to fit window"""
        image, image_size = load_image(path)
        self._texture = self.ctx.texture(image_size, 4, data=image)
        self._texture.use(location=0)
        self.prog["tex"].value = 0
        self.wnd.title = str(path)
        self._scale_image()
        logger.debug(f"Loaded image: {path}")

    def _scale_image(self) -> None:
        """Correct viewport to window size and scale quad"""
        # Calculates aspect ratios
        image_ar = self._texture.width / self._texture.height
        fb_width, fb_height = self.wnd.buffer_size
        window_ar = fb_width / fb_height

        # Re-scale the viewport to new window dimensions
        self.ctx.viewport = (0, 0, fb_width, fb_height)

        self._scale_quad_vertices(window_ar=window_ar, image_ar=image_ar)

    def _scale_quad_vertices(self, window_ar: float, image_ar: float) -> None:
        """Scale the UV to NDC mapping to preserve aspect ratio"""
        # Define scaling axis and scale
        if image_ar > window_ar:
            # Image is wider than window, fit by width
            self.quad_scale = (1.0, window_ar / image_ar)
        else:
            # Image is taller than window, fit by height
            self.quad_scale = (image_ar / window_ar, 1.0)

        # Refreshes VBO with scaled vertices
        self.vbo.write(self.scaled_vertices)


# Functions

def start_slideshow_ogl(
    queue: multiprocessing.Queue = None,
    geometry: tuple[int, int, int, int] = (960, 1080, 960, 0),
    **kwargs,
) -> None:
    """On change crawls folders and initializes the slideshow in child process

    Args:
        queue:
        geometry: String specifying windowed/fullscreen modes
    """
    if queue is None:
        raise ValueError(
            "SignalQueue must exist for the child process to run."
        )

    # Instantiate child process and pass SignalQueue into it for communication
    context = multiprocessing.get_context("spawn")
    slideshow = context.Process(
        target=run_render_window,
        args=(
            queue,
            geometry,
        ),
    )
    slideshow.start()


def run_render_window(
    queue: multiprocessing.Queue, geometry: tuple[int, int, int, int]
) -> None:
    """Run OpenGL window and signal resources-start to block Frontend"""
    config = window_factory(queue, geometry)

    # Queue event in SignalQueue
    config.queue.put("session_started")

    # Initialize image queue and display first image
    config.load_images()
    mglw.run_window_config_instance(config)


def window_factory(
    queue: multiprocessing.Queue,
    geometry: tuple[int, int, int, int],
) -> RenderWindow:
    window = mglw.context.glfw.Window(visible=False)

    width, height, hor_offset, vert_offset = geometry
    window.size = width, height
    window.position = hor_offset, vert_offset

    window.visible = True

    window.print_context_info()
    mglw.activate_context(window=window)
    timer = mglw.Timer()
    config = RenderWindow(ctx=window.ctx, wnd=window, timer=timer, queue=queue)

    # Keep weakref to give GC freedom to collect
    window._config = weakref.ref(config)

    # Swap buffers once before staring the main loop.
    # This can trigger additional resize events reporting
    # a more accurate buffer size
    window.swap_buffers()
    window.set_default_viewport()
    return config
