import sys

# Suppress broken JupyROOT RCanvas drawer in Jupyter notebooks
for _mod in list(sys.modules.values()):
    if hasattr(_mod, "RCanvasAvailable"):
        _mod.RCanvasAvailable = lambda: False
    if hasattr(_mod, "GetRCanvasDrawers"):
        _mod.GetRCanvasDrawers = lambda: []

try:
    _ip = get_ipython()
    if _ip is not None and hasattr(_ip, "events"):
        _ip.events.callbacks["post_execute"] = [
            _cb for _cb in _ip.events.callbacks.get("post_execute", [])
            if "CaptureDrawnPrimitives" not in getattr(_cb, "__qualname__", "")
        ]
except Exception:
    pass

from .converters import *
from .fileio import *
from .plotting import *
from .utils import root_test_objects
