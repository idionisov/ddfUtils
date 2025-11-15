from typing import Union

import numpy as np
import pandas as pd
import ROOT
import uproot

from .helpers import _is_uproot, _np_array

mplm = {
   "o":  20,   # ROOT: Full circle → Matplotlib: Circle
   "s":  21,   # ROOT: Full square → Matplotlib: Square
   "D":  22,   # ROOT: Full diamond → Matplotlib: Diamond
   "^":  23,   # ROOT: Full triangle up → Matplotlib: Triangle up
   "v":  24,   # ROOT: Full triangle down → Matplotlib: Triangle down
   "<":  25,   # ROOT: Full triangle left → Matplotlib: Triangle left
   ">":  26,   # ROOT: Full triangle right → Matplotlib: Triangle right
   "p":  27    # ROOT: Star → Matplotlib: Pentagon
}

def get_TGraphErrors(
    x, y, ex, ey,
    title: str = "",
    x_title: str = "",
    y_title: str = ""
) -> ROOT.TGraphErrors:
    N  = len(x)

    x  = np.array(x,  dtype=np.float64)
    y  = np.array(y,  dtype=np.float64)
    ex = np.array(ex, dtype=np.float64)
    ey = np.array(ey, dtype=np.float64)

    graph = ROOT.TGraphErrors(N, x, y, ex, ey)
    graph.SetTitle(title)
    graph.GetXaxis().SetTitle(x_title)
    graph.GetYaxis().SetTitle(y_title)

    return graph

# =====================================
# Type Checking Functions
# =====================================


def _is_tgraph(obj, type_name: str, exclude: tuple = (), option: str = "") -> bool:
    """
    Generic check for TGraph types, both ROOT and uproot.

    Parameters
    ----------
    obj : object
        Object to check.
    type_name : str
        Main TGraph type, e.g., "TGraph", "TGraphAsymmErrors", "TGraph2D".
    exclude : tuple
        Types to exclude from check.
    option : str
        "uproot" to only check uproot, "all"/"both" to check both, default ROOT only.
    """

    def is_root_type(o):
        cls = getattr(ROOT, type_name, None)
        if cls is None:
            return False
        if isinstance(o, cls) and not isinstance(o, tuple(getattr(ROOT, e) for e in exclude if hasattr(ROOT, e))):
            return True
        return False

    def is_uproot_type(o):
        if not hasattr(o, "classname"):
            return False
        if uproot.Model.is_instance(o, type_name) and all(not uproot.Model.is_instance(o, e) for e in exclude):
            return True
        return False

    option = option.lower()
    if option == "uproot":
        return is_uproot_type(obj)
    elif option in ("all", "both"):
        return is_root_type(obj) or is_uproot_type(obj)
    else:
        return is_root_type(obj)



def is_TGraph(obj, option=""):
    return _is_tgraph(
        obj, "TGraph",
        exclude=("TGraphErrors", "TGraphAsymmErrors", "TGraph2D", "TGraph2DErrors", "TGraph2DAsymmErrors"),
        option=option
    )

def is_TGraphErrors(obj, option=""):
    return _is_tgraph(obj, "TGraphErrors", option=option)

def is_TGraphAsymmErrors(obj, option=""):
    return _is_tgraph(obj, "TGraphAsymmErrors", option=option)

def is_TGraph2D(obj, option=""):
    return _is_tgraph(obj, "TGraph2D", exclude=("TGraph2DErrors", "TGraph2DAsymmErrors"), option=option)




# ----------------------------------------------------------------------
# Root extractors
# ----------------------------------------------------------------------


def _apply_mask(x, *arrays, xmin=None, xmax=None):
    mask = np.ones_like(x, dtype=bool)
    if xmin is not None:
        mask &= x >= xmin
    if xmax is not None:
        mask &= x <= xmax

    return (x[mask],) + tuple(x[mask] for x in arrays)

def _apply_mask_2d(x, y, *arrays, xmin=None, xmax=None, ymin=None, ymax=None):
    mask = np.ones_like(x, dtype=bool)

    if xmin is not None:
        mask &= x >= xmin
    if xmax is not None:
        mask &= x <= xmax
    if ymin is not None:
        mask &= y >= ymin
    if ymax is not None:
        mask &= y <= ymax

    return (x[mask], y[mask]) + tuple(arr[mask] for arr in arrays)

def _get_root_TGraph(graph):
    x = _np_array(graph.GetX())
    y = _np_array(graph.GetY())

    return x, y

def _get_root_TGraphErrors(graph):
    x, y = _get_root_TGraph(graph)
    ex = _np_array(graph.GetEX())
    ey = _np_array(graph.GetEY())

    return x, y, ex, ey

def _get_root_TGraphAsymmErrors(graph):
    x, y = _get_root_TGraph(graph)
    exl = _np_array(graph.GetEXlow())
    exh = _np_array(graph.GetEXhigh())
    eyl = _np_array(graph.GetEYlow())
    eyh = _np_array(graph.GetEYhigh())
    return x, y, exl, exh, eyl, eyh

def _get_root_TGraph2D(graph):
    x = _np_array(graph.GetX())
    y = _np_array(graph.GetY())
    z = _np_array(graph.GetZ())
    return x, y, z

# ----------------------------------------------------------------------
# Uproot extractors
# ----------------------------------------------------------------------

def _get_uproot_TGraph(obj):
    return (
        _np_array(obj.member("fX")),
        _np_array(obj.member("fY"))
    )

def _get_uproot_TGraphErrors(obj):
    x, y = _get_uproot_TGraph(obj)
    return (x, y,
        _np_array(obj.member("fEX")),
        _np_array(obj.member("fEY")),
    )

def _get_uproot_TGraphAsymmErrors(obj):
    x, y = _get_uproot_TGraph(obj)
    return (x, y,
        _np_array(obj.member("fEXlow")),
        _np_array(obj.member("fEXhigh")),
        _np_array(obj.member("fEYlow")),
        _np_array(obj.member("fEYhigh")),
    )

def _get_uproot_TGraph2D(obj):
    return (
        _np_array(obj.member("fX")),
        _np_array(obj.member("fY")),
        _np_array(obj.member("fZ")),
    )

# ----------------------------------------------------------------------
# Combined extractors
# ----------------------------------------------------------------------

def _get_TGraph2D(obj):
    if is_TGraph2D(obj, "all"):
        if _is_uproot(obj):
            return _get_uproot_TGraph2D(obj)
        else:
            return _get_root_TGraph2D(obj)
    else:
        raise ValueError(f"Unsupported object type: {type(obj)}!")

def _get_TGraphAsymmErrors(obj):
    if is_TGraphAsymmErrors(obj, "all"):
        if _is_uproot(obj):
            return _get_uproot_TGraphAsymmErrors(obj)
        else:
            return _get_root_TGraphAsymmErrors(obj)
    else:
        raise ValueError(f"Unsupported object type: {type(obj)}!")


def _get_TGraphErrors(obj):
    if is_TGraphErrors(obj, "all"):
        if _is_uproot(obj):
            return _get_uproot_TGraphErrors(obj)
        else:
            return _get_root_TGraphErrors(obj)
    else:
        raise ValueError(f"Unsupported object type: {type(obj)}!")


def _get_TGraph(obj):
    if is_TGraph(obj, "all"):
        if _is_uproot(obj):
            return _get_uproot_TGraph(obj)
        else:
            return _get_root_TGraph(obj)
    else:
        raise ValueError(f"Unsupported object type: {type(obj)}!")



def graph_to_numpy(obj,
    xmin: Union[float, None] = None,
    xmax: Union[float, None] = None,
    ymin: Union[float, None] = None,
    ymax: Union[float, None] = None
):
    """
    Converts a ROOT or uproot TGraph object into a numpy array.

    Supports TGraph, TGraphErrors, TGraphAsymmErrors, and TGraph2D in both
    ROOT and uproot formats.

    Parameters
    ----------
    obj : TGraph-like
        Any supported ROOT or uproot graph object.

    Returns
    -------
    x, y [TGraph]
    x, y, ex, ey [TGraphErrors]
    x, y, exl, exh, eyl, eyh [TGraphAsymmErrors]
    x, y, z [TGraph2D]

    Raises
    ------
    ValueError
        If the graph type is unsupported.
    """
    is_2d = False
    if is_TGraphAsymmErrors(obj, "all"):
        output = _get_TGraphAsymmErrors(obj)

    elif is_TGraphErrors(obj, "all"):
        output = _get_TGraphErrors(obj)

    elif is_TGraph(obj, "all"):
        output = _get_TGraph(obj)

    elif is_TGraph2D(obj, "all"):
        is_2d = True
        output = _get_TGraph2D(obj)

    else:
        raise ValueError(f"Type {type(obj)} not supported!")

    if is_2d:
        output = _apply_mask_2d(output[0], output[1], *output[2:], xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
    else:
        output = _apply_mask(output[0], *output[1:], xmin=xmin, xmax=xmax)

    return output

def graph_to_pandas(obj,
    cols: dict = {
        "x":   "x",
        "y":   "y",
        "z":   "z",
        "ex":  "ex",
        "ey":  "ey",
        "exl": "exl",
        "exh": "exh",
        "eyl": "eyl",
        "eyh": "eyh",
    },
    **kwargs
):
    """
    Convert a ROOT or uproot TGraph object into a pandas DataFrame.

    Supports TGraph, TGraphErrors, TGraphAsymmErrors, and TGraph2D in both
    PyROOT and uproot formats. The function auto-detects the graph type and
    returns only the relevant columns (e.g. x,y[,z], error terms).

    Parameters
    ----------
    obj : TGraph-like
        Any supported ROOT or uproot graph object.
    cols : dict, optional
        Mapping of internal column names to DataFrame column names.

    Returns
    -------
    pandas.DataFrame
        Data extracted from the graph.

    Raises
    ------
    ValueError
        If the graph type is unsupported.
    """

    if is_TGraphAsymmErrors(obj, "all"):
        x, y, exl, exh, eyl, eyh = graph_to_numpy(obj, **kwargs)

        return pd.DataFrame({
            cols["x"]:   x,   cols["y"]:   y,
            cols["exl"]: exl, cols["exh"]: exh,
            cols["eyl"]: eyl, cols["eyh"]: eyh
        })


    if is_TGraphErrors(obj, "all"):
        x, y, ex, ey = graph_to_numpy(obj, **kwargs)

        return pd.DataFrame({
            cols["x"]:  x,  cols["y"]:  y,
            cols["ex"]: ex, cols["ey"]: ey,
        })


    if is_TGraph(obj, "all"):
        x, y = graph_to_numpy(obj, **kwargs)

        return pd.DataFrame({cols["x"]: x, cols["y"]: y})


    if is_TGraph2D(obj, "all"):
        x, y, z = graph_to_numpy(obj, **kwargs)

        return pd.DataFrame({cols["x"]: x, cols["y"]: y, cols["z"]: z})


    raise ValueError(f"Type {type(obj)} not supported!")
