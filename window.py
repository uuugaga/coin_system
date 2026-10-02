import ctypes
import win32gui

WINDOW_TITLE = "Albion Online Client"


def enable_dpi_awareness():
    """
    Make this process DPI aware.

    Without this Windows virtualizes the coordinates returned by GetWindowRect
    and GetClientRect on any display that is not at 100% scaling, while
    ImageGrab keeps capturing real physical pixels. The two then disagree and
    every click and every OCR region is offset by the scaling factor.
    """
    try:
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


# Must run before anything queries window geometry, so it is done at import
# time rather than left to the caller.
enable_dpi_awareness()


def find_window(title=WINDOW_TITLE):
    """
    Return the handle of the game window, or raise if it is not open.

    The old code let a failed lookup through as handle 0, which silently turned
    every coordinate into a desktop coordinate instead of a window one.
    """
    handle = win32gui.FindWindow(None, title)
    if not handle:
        raise RuntimeError(
            f'Game window "{title}" not found. Make sure Albion Online is '
            f'running, or run debug/diagnose.py to list the open windows.'
        )
    return handle


def get_client_rect(handle):
    """
    Return (left, top, width, height) of the client area in screen coordinates.

    The client area is the rendered game image. GetWindowRect would instead
    include the title bar and the resize borders, which shifts the origin down
    by the title bar height and inflates the width and height that every ratio
    in position.py is measured against.
    """
    _, _, width, height = win32gui.GetClientRect(handle)
    left, top = win32gui.ClientToScreen(handle, (0, 0))
    return left, top, width, height


def get_window_rect(handle):
    """Return (left, top, width, height) of the whole window, borders included."""
    left, top, right, bottom = win32gui.GetWindowRect(handle)
    return left, top, right - left, bottom - top
