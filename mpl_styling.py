import matplotlib.pyplot as plt
import mplhep
from typing import Optional, Union

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


def add_label(
    loc: Union[str, int] = "top-left",
    supp_loc: Optional[Union[str, int]] = "top-right",
    mainText: str = "SND@LHC",
    extraText: str = "",
    suppText: str = "",
    lumi: Optional[float] = None,
    lumi_unit: str = "fb^{-1}",
    com: Optional[float] = 13.6,
    style: str = "standard",  # "standard" -> "0.991 fb^-1 (13.6 TeV)"
                              # "formal"   -> "\int L dt = 0.991 fb^-1, \sqrt{s} = 13.6 TeV"
    font: Optional[str] = None,
    fontsize: Optional[Union[str, float]] = 14,
    pad: float = 0.0,
    ax=None,
):
    if ax is None:
        ax = plt.gca()

    base_fs = fontsize if isinstance(fontsize, (int, float)) else 14

    # 1. Choose between Standard HEP layout and Formal Math layout
    if style == "standard":
        # The clean, universal LHC style: "0.991 fb⁻¹ (13.6 TeV)"
        parts = []
        if lumi is not None:
            parts.append(f"{lumi:.3f} {lumi_unit}")
        if com is not None:
            parts.append(f"({com} TeV)" if lumi is not None else f"{com} TeV")
        physics_str = " ".join(parts)
    else:
        # Formal equation style
        parts = []
        if lumi is not None:
            parts.append(rf"$\int\mathcal{{L}}\,\mathrm{{d}}t = {lumi:.3f}\ \mathrm{{{lumi_unit}}}$")
        if com is not None:
            parts.append(rf"$\sqrt{{s}} = {com}\ \mathrm{{TeV}}$")
        physics_str = ", ".join(parts)

    if suppText and physics_str:
        full_supp = f"{suppText} {physics_str}"
    else:
        full_supp = physics_str or suppText

    # 2. Render Experiment badge
    loc_to_int = {"top-left": 0, "inside-left": 1, "inside-left-multiline": 2, 0: 0, 1: 1, 2: 2}
    mplhep.label.exp_text(
        text=extraText,
        exp=mainText,
        supp="",
        loc=loc_to_int.get(loc, 0),
        ax=ax,
        fontname=font,
        fontsize=base_fs,
        exp_weight="bold",
        pad=pad,
    )

    # 3. Render Right-Hand Physics Label cleanly aligned
    if full_supp and supp_loc is not None:
        pos_coords = {
            "top-right": {"x": 1.0 + pad, "y": 1.01 + pad, "ha": "right", "va": "bottom"},
            "top-left": {"x": 0.0 - pad, "y": 1.01 + pad, "ha": "left", "va": "bottom"},
            "inside-right": {"x": 0.97 - pad, "y": 0.95 - pad, "ha": "right", "va": "top"},
            "inside-left": {"x": 0.03 + pad, "y": 0.88 - pad, "ha": "left", "va": "top"},
        }
        cfg = pos_coords.get(supp_loc, pos_coords["top-right"])

        ax.text(
            cfg["x"],
            cfg["y"],
            full_supp,
            transform=ax.transAxes,
            ha=cfg["ha"],
            va=cfg["va"],
            fontsize=base_fs * 0.95,
            fontweight="normal",
            fontname=font,
        )
