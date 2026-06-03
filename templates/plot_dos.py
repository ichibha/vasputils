#!/usr/bin/env python3
import matplotlib.pyplot as plt
from pymatgen.electronic_structure.plotter import DosPlotter
from pymatgen.io.vasp import Vasprun

# vasprun.xmlからDOSのデータをCompleteDosクラスとして読み込む
vasprun = Vasprun("vasprun.xml")
complete_dos = vasprun.complete_dos

# plotterにTotal DOSを加える
plotter = DosPlotter()
plotter.add_dos("Total DOS", complete_dos)

# 線色を青に変更する
plot = plotter.get_plot(xlim=[-10, 10])
lines = plot.get_lines()
lines[0].set_color("black")

# 凡例を削除する
plot.get_legend().remove()

# 軸ラベルを変更する
plt.xlabel(r"$E - E_{\mathrm{Fermi}}$ (eV)", fontsize=32)
plt.ylabel("Density of states (states/eV)", fontsize=32)

# 目盛りのフォントサイズを変更する
plt.xticks(fontsize=24)
plt.yticks(fontsize=24)

# 描画領域にフィットするように図の大きさを自動的に調節する
plt.tight_layout()

# プロットをファイル出力する
plt.savefig("dos.pdf")

# プロットを画面出力する
plt.show()
