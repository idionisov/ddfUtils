import numpy as np
import ROOT

_rng = np.random.default_rng(seed=42)

def _fill_uniform_random(hist, low=0, high=10):
    """
    Fill a ROOT histogram with random integers in [low, high).
    """

    for idx in range(1, hist.GetNbinsX() + 1):
        if hist.GetDimension() == 1:
            hist.SetBinContent(idx, _rng.integers(low, high))
        elif hist.GetDimension() == 2:
            for idy in range(1, hist.GetNbinsY() + 1):
                hist.SetBinContent(idx, idy, _rng.integers(low, high))
    return hist

# ------------------ 1D Hist ------------------ #

def make_TH1(
    n_bins_x: int   = 10,
    xmin:     float = 0.,
    xmax:     float = 10.,
    name:     str = "hist1d",
    title:    str = ";x;y",
    fill_random: bool = True
):
    h = ROOT.TH1F(name, title, n_bins_x, xmin, xmax)

    if fill_random:
        _fill_uniform_random(h)
    return h

def make_eff_hists_1d(
    n_bins_x: int = 10,
    xmin:     float = 0.,
    xmax:     float = 10.
):
    """
    Create test 1D histograms for passed and total events.
    """

    h_total  = make_TH1(n_bins_x, xmin, xmax, name='h_total',  title='Total Histogram',  fill_random=False)
    h_passed = make_TH1(n_bins_x, xmin, xmax, name='h_passed', title='Passed Histogram', fill_random=True)

    for i in range(1, n_bins_x+1):
        passed = h_passed.GetBinContent(i)
        total  = int(passed * _rng.uniform(1, 1.3))

        h_total.SetBinContent(i, total)

    return h_passed, h_total

# ------------------ 2D Hist ------------------ #

def make_TH2(
    n_bins_x: int = 10,
    xmin:     float = 0.,
    xmax:     float = 10.,
    n_bins_y: int = 10,
    ymin:     float = 0.,
    ymax:     float = 10.,
    name:     str = "hist2d",
    title:    str = ";x;y;z",
    fill_random: bool = True
):
    h = ROOT.TH2F(name, title, n_bins_x, xmin, xmax, n_bins_y, ymin, ymax)
    if fill_random:
        _fill_uniform_random(h)
    return h

def make_eff_hists_2d(
    n_bins_x: int   = 10,
    xmin:     float = 0.,
    xmax:     float = 10.,
    n_bins_y: int   = 10,
    ymin:     float = 0.,
    ymax:     float = 10.,
):
    """
    Create test 2D histograms for passed and total events.
    """

    h_total  = make_TH2(n_bins_x, xmin, xmax, n_bins_y, ymin, ymax, name='h_total_2d',  title='Total Histogram',  fill_random=False)
    h_passed = make_TH2(n_bins_x, xmin, xmax, n_bins_y, ymin, ymax, name='h_passed_2d', title='Passed Histogram', fill_random=True)

    for ix in range(1, n_bins_x+1):
        for iy in range(1, n_bins_y+1):
            passed = h_passed.GetBinContent(ix, iy)
            total  = int(passed * _rng.uniform(1, 1.3))

            h_total.SetBinContent(ix, iy, total)

    return h_passed, h_total


# ------------------ TProfiles ------------------ #


def make_TProfile_1d(
    n_bins_x: int = 10,
    xmin:     float = 0.,
    xmax:     float = 10.,
    name:     str   = 'tprofile_1d',
    title:    str   = ';x;y',
    n_entries: int = 1000,
    noise:    float = 0.2
):
    pr = ROOT.TProfile(name, title, n_bins_x, xmin, xmax)

    for _ in range(n_entries):
        x = _rng.uniform(xmin, xmax)
        y = np.sin(x) + _rng.normal(0, noise)
        pr.Fill(x, y)
    return pr


def make_TProfile_2d(
    n_bins_x: int = 30,
    xmin:     float = 0.,
    xmax:     float = 10.,
    n_bins_y: int = 30,
    ymin:     float = 0.,
    ymax:     float = 10.,
    name:     str = 'tprofile_2d',
    title:    str = ';x;y;z',
    n_entries: int = 5000,
    noise:    float = 0.1
):
    pr = ROOT.TProfile2D(name, title, n_bins_x, xmin, xmax, n_bins_y, ymin, ymax)

    for _ in range(n_entries):
        x = _rng.uniform(xmin, xmax)
        y = _rng.uniform(ymin, ymax)
        z = np.sin(x) * np.cos(y) + _rng.normal(0, noise)
        pr.Fill(x, y, z)
    return pr


# ------------------ TGraphs ------------------ #


def make_TGraph(nPoints: int = 10):
    x = np.linspace(1, 10, nPoints)
    y = np.sin(x)

    x  = np.array(x,  dtype=np.float64)
    y  = np.array(y,  dtype=np.float64)

    gr = ROOT.TGraph(nPoints, x, y)
    return gr



def make_TGraphErrors(nPoints: int = 10):
    x = np.linspace(1, 10, nPoints)
    y = np.sin(x)

    ex = np.full(nPoints, 0.15)
    ey = np.random.uniform(0.05, 0.1, nPoints)

    x  = np.array(x,  dtype=np.float64)
    y  = np.array(y,  dtype=np.float64)
    ex = np.array(ex, dtype=np.float64)
    ey = np.array(ey, dtype=np.float64)

    gr = ROOT.TGraphErrors(nPoints, x, y, ex, ey)
    return gr



def make_TGraphAsymmErrors(nPoints: int = 10):
    x = np.linspace(1, 10, nPoints)
    y = np.sin(x)

    exl = np.random.uniform(0.1, 0.2, nPoints)
    exh = np.random.uniform(0.1, 0.2, nPoints)
    eyl = np.random.uniform(0.05, 0.1, nPoints)
    eyh = np.random.uniform(0.05, 0.1, nPoints)

    gr = ROOT.TGraphAsymmErrors(
        nPoints, x, y, exl, exh, eyl, eyh
    )
    return gr


def make_TGraph2D(nPoints: int = 10):
    X, Y = np.meshgrid(
        np.linspace(-5, 5, int(np.sqrt(nPoints))),
        np.linspace(-5, 5, int(np.sqrt(nPoints)))
    )
    Z = np.sin(np.sqrt(X**2 + Y**2))

    x = X.flatten()
    y = Y.flatten()
    z = Z.flatten()

    x = np.array(x, dtype=np.float64)
    y = np.array(y, dtype=np.float64)
    z = np.array(z, dtype=np.float64)

    gr = ROOT.TGraph2D(nPoints, x, y, z)
    return gr
