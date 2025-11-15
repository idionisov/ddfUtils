import re
from typing import Union

import numpy as np
import pandas as pd
import ROOT
import uproot

from .tgraph import graph_to_numpy, graph_to_pandas


def set_stat_option(
    teff:        ROOT.TEfficiency,
    stat_option: str = "normal"
):
    stat_option = stat_option.lower()

    normal_options           = {"normal", "kfnormal"}

    clopper_pearson_options  = {"clopper_pearson", "kfcp", "clopper pearson",
                                "clopper-pearson", "clopper.pearson",
                                "clopper:pearson", "clopperpearson"}
    bayesian_options         = {"bayesian", "kbbayesian"}
    wilson_options           = {"wilson", "kfwilson"}
    feldman_cousings_options = {"feldman_cousins", "kffc",
                                "feldman cousins", "feldman-cousings",
                                "feldman:cousins", "feldman.cousins",
                                "feldmancousins"}
    agresti_coull_options    = {"agresti_coull", "kfac",
                                "agresti coull", "agresti-coull",
                                "agresti:coull", "agresti.coull",
                                "agresticoull"}
    mid_p_interval_options   = {"mid_p_interval", "kmidp",
                                "mid p interval", "mid-p-interval",
                                "mid:p:interval", "mid.p.interval",
                                "midpinterval"}
    jeffrey_options          = {"jeffrey", "kbjeffrey"}
    uniform_prior_options    = {"uniform_prior", "kbuniform",
                                "uniform prior", "uniform-prior",
                                "uniform:prior", "uniform.prior",
                                "uniformprior"}

    if stat_option in normal_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kFNormal)
    elif stat_option in clopper_pearson_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kFCP)
    elif stat_option in bayesian_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kBBayesian)
    elif stat_option in wilson_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kFWilson)
    elif feldman_cousings_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kFFC)
    elif stat_option in agresti_coull_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kFAC)
    elif stat_option in mid_p_interval_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kMidP)
    elif stat_option in jeffrey_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kBJeffrey)
    elif stat_option in uniform_prior_options:
        teff.SetStatisticOption(ROOT.TEfficiency.kBUniform)

    else: raise ValueError(f"Invalid statistic option '{stat_option}'!")



def get_stat_option(teff: ROOT.TEfficiency) -> Union[str, None]:
    stat_option = teff.GetStatisticOption()

    if   stat_option==0:  return "Clopper Pearson"
    elif stat_option==1:  return "Normal"
    elif stat_option==2:  return "Wilson"
    elif stat_option==3:  return "Agresti Coull"
    elif stat_option==4:  return "Feldman Cousins"
    elif stat_option==5:  return "Jeffrey"
    elif stat_option==6:  return "Normal"
    elif stat_option==7:  return "Uniform Prior"
    elif stat_option==8:  return "Bayesian"
    elif stat_option==9:  return "Mid P Interval"
    else:                return None


def get_TEff(
    passed: ROOT.TH1,
    total: ROOT.TH1,
    stat_option: str = "normal",
    cl: float = 0.682689,
    name: str = "",
    title: str = ""
) -> ROOT.TEfficiency:
    if type(passed) != type(total):
        raise ValueError("Passed and Total Histograms are not of the same type!")

    teff = ROOT.TEfficiency(passed, total)
    teff.SetConfidenceLevel(cl)
    set_stat_option(teff, stat_option)
    if name: teff.SetName(name)
    if title: teff.SetTitle(title)

    return teff




def _teff1d_to_tgraph(teff: ROOT.TEfficiency, name: str = '', title: str = '', suffix: str = '') -> ROOT.TGraphAsymmErrors:
    if teff.GetDimension() != 1:
        raise ValueError("TEfficiency object is not one-dimensional!")

    if not name:
        name  = teff.GetName()
    if not title:
        title = teff.GetTitle()
    if suffix:
        name = f"{name}_{suffix}"

    total_hist = teff.GetTotalHistogram()
    n_bins_x = total_hist.GetNbinsX()

    x   = np.array([total_hist.GetXaxis().GetBinCenter(bin) for bin in range(1, n_bins_x + 1)], dtype=np.float64)
    y   = np.array([teff.GetEfficiency(bin) for bin in range(1, n_bins_x + 1)], dtype=np.float64)
    ex  = np.array([total_hist.GetXaxis().GetBinWidth(bin) / 2 for bin in range(1, n_bins_x + 1)], dtype=np.float64)
    eyl = np.array([teff.GetEfficiencyErrorLow(bin) for bin in range(1, n_bins_x + 1)], dtype=np.float64)
    eyh = np.array([teff.GetEfficiencyErrorUp(bin) for bin in range(1, n_bins_x + 1)], dtype=np.float64)

    graph = ROOT.TGraphAsymmErrors(n_bins_x, x, y, ex, ex, eyl, eyh)
    if name.startswith("gr_"):
        graph.SetName(name)
    else:
        graph.SetName(f"gr_{name}")
    graph.SetTitle(title)

    return graph




def _teff2d_to_tgraph(
    teff: ROOT.TEfficiency,
    name: str = "",
    title: str = "",
    suffix: str = ""
) -> ROOT.TGraph2D:
    if teff.GetDimension() != 2:
        raise ValueError("TEfficiency object is not two-dimensional!")

    if not name:
        name  = teff.GetName()
    if not title:
        title = teff.GetTitle()
    if suffix:
        name = f"{name}_{suffix}"

    total_hist = teff.GetTotalHistogram()
    n_bins_x = total_hist.GetNbinsX()
    n_bins_y = total_hist.GetNbinsY()

    x = []
    y = []
    z = []

    for ix in range(1, n_bins_x + 1):
        for iy in range(1, n_bins_y + 1):
            x.append( total_hist.GetXaxis().GetBinCenter(ix) )
            y.append( total_hist.GetYaxis().GetBinCenter(iy) )
            z.append( teff.GetEfficiency(total_hist.GetBin(ix, iy)) )

    graph = ROOT.TGraph2D(len(x),
        np.array(x, dtype=np.float64),
        np.array(y, dtype=np.float64),
        np.array(z, dtype=np.float64)
    )


    if name.startswith("gr_"):
        graph.SetName(name)
    else:
        graph.SetName(f"gr_{name}")
    graph.SetTitle(title)

    return graph


def teff_to_tgraph(
    teff: ROOT.TEfficiency,
    name: str = "",
    title: str = "",
    suffix: str = ""
):
    if teff.GetDimension() == 1:
        return _teff1d_to_tgraph(teff, name, title, suffix)
    elif teff.GetDimension() == 2:
        return _teff2d_to_tgraph(teff, name, title, suffix)
    else:
        raise ValueError("TEfficiency object cannot be of dimension higher 2!")


def teff2d_to_th2(teff,
    name: str = "",
    title: str = "",
    suffix: str = ""
) -> ROOT.TH2D:
    if teff.GetDimension() != 2:
        raise ValueError("TEfficiency object is not two-dimensional!")

    if not name:  name  = teff.GetName()
    if not title: title = teff.GetTitle()
    if suffix:    name = f"{name}_{suffix}"

    hist = teff.CreateHistogram()
    hist.SetName(name)
    hist.SetTitle(title)

    return hist



def teff_to_numpy(teff: ROOT.TEfficiency, **kwargs):
    gr = teff_to_tgraph(teff)

    return graph_to_numpy(gr, **kwargs)



def teff_to_pandas(teff: ROOT.TEfficiency,
    cols: dict = {"x": "x", "y": "y", "exl": "exl", "exh": "exh", "eyl": "eyl", "eyh": "eyh"},
    **kwargs
):
    return graph_to_pandas(teff_to_tgraph(teff), cols=cols, **kwargs)
