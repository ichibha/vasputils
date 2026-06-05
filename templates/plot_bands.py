#!/usr/bin/env/python3
import matplotlib.pyplot as plt
from pymatgen.electronic_structure.plotter import BSPlotter
from pymatgen.io.vasp.outputs import BandStructure, Vasprun

from vasputils import set_plot_style

# vasprun.xmlからバンド分散データを読み込む
vasprun = Vasprun("vasprun.xml")
band_structure: BandStructure = vasprun.get_band_structure()

# BandStructureインスタンスでプロッターを初期化する
plotter = BSPlotter(band_structure)

# フェルミエネルギーの上下20eVの範囲でバンド分散をプロットする
plot = plotter.get_plot(ylim=[-20, 20])

# フェルミレベルをプロットする
plt.axhline(0, color="black", linestyle="dotted")
plot.get_legend().remove()  # 凡例を削除

set_plot_style()
plt.xlabel("")  # x軸ラベルを削除
plt.ylabel(r"$E - E_{\mathrm{Fermi}}$ (eV)")
plt.savefig("bands.pdf")
plt.show()
plt.close()
