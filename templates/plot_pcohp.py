#!/usr/bin/env python3
from itertools import product

import matplotlib.pyplot as plt
from pymatgen.electronic_structure.cohp import CompleteCohp
from pymatgen.electronic_structure.plotter import CohpPlotter

# matplotlib settings
plt.rcParams["font.size"] = 18
plt.rcParams["figure.titlesize"] = 18
plt.rcParams["axes.labelsize"] = 18
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["legend.fontsize"] = 14
plt.rcParams["figure.autolayout"] = True
plt.rcParams["axes.formatter.useoffset"] = False


# COHPを読み込む
completeCohp = CompleteCohp.from_file(
    fmt="LOBSTER",
    filename="COHPCAR.lobster",
    structure_file="POSCAR",
)

# COHPをプロットする軌道の指標
index = "1"

# (Si-3s, O-2s), (Si-3s, O-2p), (Si-3p, O-2s), (Si-3p, O-2p)の
# 混成軌道のCOHPをそれぞれ取得する
cohp_3s_2s = completeCohp.get_orbital_resolved_cohp(
    index,
    "3s-2s",
)
cohp_3s_2p = completeCohp.get_summed_cohp_by_label_and_orbital_list(
    [index] * 3,
    [f"3s-2p{c}" for c in ["x", "y", "z"]],
)
cohp_3p_2s = completeCohp.get_summed_cohp_by_label_and_orbital_list(
    [index] * 3,
    [f"3p{c}-2s" for c in ["x", "y", "z"]],
)
cohp_3p_2p = completeCohp.get_summed_cohp_by_label_and_orbital_list(
    [index] * 9,
    [f"3p{c1}-2p{c2}" for c1, c2 in product(["x", "y", "z"], repeat=2)],
)

# CohpPlotterを初期化する
plotter = CohpPlotter()

# プロッタにCOHPを追加する
plotter.add_cohp(label=f"Si-3s and O-2s", cohp=cohp_3s_2s)
plotter.add_cohp(label=f"Si-3s and O-2p", cohp=cohp_3s_2p)
plotter.add_cohp(label=f"Si-3p and O-2s", cohp=cohp_3p_2s)
plotter.add_cohp(label=f"Si-3p and O-2p", cohp=cohp_3p_2p)

# COHPをプロットする
ax = plotter.get_plot()

# 線色と線種を変更する
lines = ax.lines
lines[0].set_color("lightgray")
lines[0].set_linestyle("dotted")
lines[1].set_color("lightgray")
lines[1].set_linestyle("dashed")
lines[2].set_color("lightgray")
lines[2].set_linestyle("dashdot")
lines[3].set_color("black")
lines[3].set_linestyle("solid")

# プロットを出力
plt.legend()
plt.savefig("pcohp.pdf")
plt.show()
plt.close()
