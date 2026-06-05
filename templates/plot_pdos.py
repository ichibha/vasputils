#!/usr/bin/env python3
import matplotlib.pyplot as plt
from pymatgen.electronic_structure.core import OrbitalType
from pymatgen.electronic_structure.plotter import DosPlotter
from pymatgen.io.vasp import Vasprun

from vasputils import set_plot_style

# DOSのデータをvasprun.xmlからCompleteDosインスタンスとして取得する
vasprun = Vasprun("vasprun.xml")
complete_dos = vasprun.complete_dos

# DosPlotterインスタンスを作成する
plotter = DosPlotter()

# plotterにTotal DOSを加える
plotter.add_dos("Total DOS", complete_dos)

# セルに含まれる元素名でループを回す
for element in vasprun.atomic_symbols:

    # 所与の元素のPDOSを取得する
    pdos = complete_dos.get_element_spd_dos(element)

    # 0=s軌道成分, 1=p軌道成分, 2=d軌道成分, ...のPDOSをplotterに加える
    for m in [0, 1]:
        orbital_type = OrbitalType(m)
        plotter.add_dos(f"{element}({orbital_type})", pdos[orbital_type])

        # フェルミエネルギーの上下10 eVの範囲のTotal DOSとPDOSをプロットする
        plot = plotter.get_plot(xlim=[-10, 10])

# 線色を変更する
color_dict = {
    "Total DOS": "black",
    "Si(s)": "blue",
    "Si(p)": "red",
    "O(s)": "green",
    "O(p)": "orange",
}
for line in plot.get_lines():
    key = str(line.get_label())
    if key in color_dict:
        line.set_color(color_dict[key])

# 凡例の順番をcolor_dictの順にする
handles, labels = plot.get_legend_handles_labels()
ordered_handles = [handles[labels.index(key)] for key in color_dict]
ordered_labels = list(color_dict.keys())
plot.legend(ordered_handles, ordered_labels, fontsize=24)

# プロットを出力する
set_plot_style(label_size=32, xtick_size=24, ytick_size=24)
plt.xlabel(r"$E - E_{\mathrm{Fermi}}$ (eV)")
plt.ylabel("Density of states (states/eV)")
plt.savefig("pdos.pdf")
plt.show()
