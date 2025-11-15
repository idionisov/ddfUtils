from typing import Union

import numpy as np
import pandas as pd
import ROOT
import uproot

from .helpers import _np_array

# =====================================
# Type Checking Functions
# =====================================

def is_root_type(obj, root_type, exclude=None):
    exclude = exclude or []
    return isinstance(obj, root_type) and not any(isinstance(obj, e) for e in exclude)

def is_uproot_type(obj, uproot_type, exclude=None):
    exclude = exclude or []
    if not hasattr(obj, "classname"):
        return False
    return uproot.Model.is_instance(obj, uproot_type) and not any(uproot.Model.is_instance(obj, e) for e in exclude)


def is_TH1(obj, option: str = "r") -> bool:
    root_check = lambda o: is_root_type(o, ROOT.TH1, exclude=[ROOT.TH2, ROOT.TH3, ROOT.TProfile, ROOT.TProfile2D, ROOT.TProfile3D])
    uproot_check = lambda o: is_uproot_type(o, "TH1", exclude=["TH2","TH3","TProfile","TProfile2D","TProfile3D"])
    if option.lower() in ("root", "r"):
        return root_check(obj)
    elif option.lower() in ("uproot", "ur"):
        return uproot_check(obj)
    else:
        return root_check(obj) or uproot_check(obj)

def is_TProfile(obj, option: str = "r") -> bool:
    root_check   = lambda o: is_root_type(o, ROOT.TProfile, exclude=[ROOT.TProfile2D, ROOT.TProfile3D])
    uproot_check = lambda o: is_uproot_type(o, "TProfile",  exclude=["TProfile2D", "TProfile3D"])
    if option.lower() in ("root", "r"):
        return root_check(obj)
    elif option.lower() in ("uproot", "ur"):
        return uproot_check(obj)
    else:
        return root_check(obj) or uproot_check(obj)


def is_TH2(obj, option: str = "r") -> bool:
    root_check   = lambda o: is_root_type(o, ROOT.TH2, exclude=[ROOT.TH3, ROOT.TProfile2D, ROOT.TProfile3D])
    uproot_check = lambda o: is_uproot_type(o, "TH2",  exclude=["TH3", "TProfile"])
    if option.lower() in ("root", "r"):
        return root_check(obj)
    elif option.lower() in ("uproot", "ur"):
        return uproot_check(obj)
    else:
        return root_check(obj) or uproot_check(obj)


def is_TProfile2D(obj, option: str = "r") -> bool:
    root_check   = lambda o: is_root_type(o, ROOT.TProfile2D, exclude=[ROOT.TProfile3D])
    uproot_check = lambda o: is_uproot_type(o, "TProfile2D",  exclude=["TProfile3D"])
    if option.lower() in ("root", "r"):
        return root_check(obj)
    elif option.lower() in ("uproot", "ur"):
        return uproot_check(obj)
    else:
        return root_check(obj) or uproot_check(obj)

# =====================================
# Conversion Functions
# =====================================

def _slice_axis(edges, xmin=None, xmax=None):
    lo = 0 if xmin is None else np.searchsorted(edges, xmin, side='left')
    hi = len(edges) if xmax is None else np.searchsorted(edges, xmax, side='right')

    return lo, hi


def _get_root_th1(hist: ROOT.TH1,
    xmin: Union[float, int, None] = None,
    xmax: Union[float, int, None] = None
):
    x_axis = hist.GetXaxis()
    n_bins = hist.GetNbinsX()

    xs, ys, x_bin_edges, exs, eys = [], [], [], [], []

    for i_bin in range(1, n_bins + 1):
        low  = x_axis.GetBinLowEdge(i_bin)
        up   = x_axis.GetBinUpEdge(i_bin)

        if xmin is not None and low < xmin:
            continue
        if xmax is not None and up > xmax:
            continue

        center = x_axis.GetBinCenter(i_bin)
        width  = (up - low) / 2.0
        val    = hist.GetBinContent(i_bin)
        err    = hist.GetBinError(i_bin)

        xs.append(center)
        ys.append(val)
        x_bin_edges.append(low)
        exs.append(width)
        eys.append(err)

    x_bin_edges.append(x_axis.GetBinUpEdge(n_bins))

    return _np_array(xs), _np_array(ys), _np_array(x_bin_edges), _np_array(exs), _np_array(eys)

def _get_uproot_th1(hist,
    xmin: Union[float, int, None] = None,
    xmax: Union[float, int, None] = None
):
    y, x_bin_edges = hist.to_numpy()
    ey = hist.errors()
    x = 0.5 * (x_bin_edges[:-1] + x_bin_edges[1:])
    ex = 0.5 * (x_bin_edges[1:] - x_bin_edges[:-1])

    mask = np.ones_like(x, dtype=bool)
    if xmin is not None:
        mask &= x_bin_edges[:-1] >= xmin
    if xmax is not None:
        mask &= x_bin_edges[1:] <= xmax

    filtered_edges = x_bin_edges[:-1][mask].tolist()

    if np.any(mask):
        last_index = np.where(mask)[0][-1] + 1
        filtered_edges.append(x_bin_edges[last_index])

    return x[mask], y[mask], _np_array(filtered_edges), ex[mask], ey[mask]



def _th1_to_numpy(hist, **kwargs):
    if is_TH1(hist, "root") or is_TProfile(hist, "root"):
        return _get_root_th1(hist, **kwargs)
    elif is_TH1(hist, "uproot") or is_TProfile(hist, "uproot"):
        return _get_uproot_th1(hist, **kwargs)
    else:
        raise ValueError("Object is not a ROOT.TH1, uproot.TH1, ROOT.TProfile or uproot.TProfile instance!")



def _get_root_th2(hist: ROOT.TH2,
    xmin: Union[float, int, None] = None,
    xmax: Union[float, int, None] = None,
    ymin: Union[float, int, None] = None,
    ymax: Union[float, int, None] = None
):
    x_axis = hist.GetXaxis()
    y_axis = hist.GetYaxis()
    nx = x_axis.GetNbins()
    ny = y_axis.GetNbins()

    x_bins = []
    for i in range(1, nx+1):
        low = x_axis.GetBinLowEdge(i)
        up  = x_axis.GetBinUpEdge(i)
        if xmin is not None and low <= xmin:
            continue
        if xmax is not None and up >= xmax:
            continue
        x_bins.append(i)

    y_bins = []
    for j in range(1, ny+1):
        low = y_axis.GetBinLowEdge(j)
        up  = y_axis.GetBinUpEdge(j)
        if ymin is not None and low <= ymin:
            continue
        if ymax is not None and up >= ymax:
            continue
        y_bins.append(j)

    x_centers = np.array([x_axis.GetBinCenter(i) for i in x_bins], dtype=np.float64)
    y_centers = np.array([y_axis.GetBinCenter(j) for j in y_bins], dtype=np.float64)
    x_edges   = np.array([x_axis.GetBinLowEdge(x_bins[0])] + [x_axis.GetBinUpEdge(i) for i in x_bins], dtype=np.float64)
    y_edges   = np.array([y_axis.GetBinLowEdge(y_bins[0])] + [y_axis.GetBinUpEdge(j) for j in y_bins], dtype=np.float64)
    x_errs    = 0.5 * (x_edges[1:] - x_edges[:-1])
    y_errs    = 0.5 * (y_edges[1:] - y_edges[:-1])

    values = np.zeros((len(y_bins), len(x_bins)), dtype=np.float64)
    z_errs = np.zeros_like(values)

    for ix, i_bin in enumerate(x_bins):
        for iy, j_bin in enumerate(y_bins):
            values[iy, ix] = hist.GetBinContent(i_bin, j_bin)
            z_errs[iy, ix] = hist.GetBinError(i_bin, j_bin)

    return x_centers, y_centers, values, x_edges, y_edges, x_errs, y_errs, z_errs


def _get_uproot_th2(hist,
    xmin: Union[float, int, None] = None,
    xmax: Union[float, int, None] = None,
    ymin: Union[float, int, None] = None,
    ymax: Union[float, int, None] = None
):
    x_edges_full = hist.member("fXaxis").edges()
    y_edges_full = hist.member("fYaxis").edges()
    values_full  = hist.values()
    z_errs_full  = hist.errors()

    x_mask = np.ones(len(x_edges_full)-1, dtype=bool)
    y_mask = np.ones(len(y_edges_full)-1, dtype=bool)

    if xmin is not None:
        x_mask &= x_edges_full[:-1] > xmin
    if xmax is not None:
        x_mask &= x_edges_full[1:] < xmax
    if ymin is not None:
        y_mask &= y_edges_full[:-1] > ymin
    if ymax is not None:
        y_mask &= y_edges_full[1:] < ymax

    x_indices = np.where(x_mask)[0]
    y_indices = np.where(y_mask)[0]

    values = values_full[np.ix_(y_indices, x_indices)]
    z_errs = z_errs_full[np.ix_(y_indices, x_indices)]

    x_edges = x_edges_full[x_indices[0]: x_indices[-1]+2]
    y_edges = y_edges_full[y_indices[0]: y_indices[-1]+2]

    x_centers = 0.5 * (x_edges[:-1] + x_edges[1:])
    y_centers = 0.5 * (y_edges[:-1] + y_edges[1:])
    x_errs = 0.5 * (x_edges[1:] - x_edges[:-1])
    y_errs = 0.5 * (y_edges[1:] - y_edges[:-1])

    return x_centers, y_centers, values, x_edges, y_edges, x_errs, y_errs, z_errs


def _th2_to_numpy(hist, **kwargs):
    if is_TH2(hist, "root") or is_TProfile2D(hist, "root"):
        return _get_root_th2(hist, **kwargs)
    elif is_TH2(hist, "uproot") or is_TProfile2D(hist, "uproot"):
        return _get_uproot_th2(hist, **kwargs)
    else:
        raise ValueError(f"Object {type(hist)} is not supported!")



def hist_to_numpy(obj, **kwargs):
    if "th2" in str(type(obj)).lower():
        return _th2_to_numpy(obj, **kwargs)
    elif "th1" in str(type(obj)).lower():
        return _th1_to_numpy(obj, **kwargs)
    else:
        raise ValueError(f"Object {type(obj)} is not supported!")


def hist_to_pandas(hist,
    cols: dict = {"x": "x", "y": "y", "ex": "ex", "ey": "ey"},
    **kwargs
):
    if not (is_TH1(hist, "any") or is_TProfile(hist, "any")):
        raise ValueError(f"Type {type(hist)} is not supported!")

    x, y, _, ex, ey = _th1_to_numpy(hist, **kwargs)
    df = pd.DataFrame({cols["x"]: x, cols["y"]: y, cols["ex"]: ex, cols["ey"]: ey})
    return df
