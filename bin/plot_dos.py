#!/usr/bin/env python3
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from pymatgen.electronic_structure.plotter import DosPlotter
from vasputils import (
    add_vasprun_path_argument,
    cast_vasprun_path,
    get_vasprun,
    set_plot_style,
)


def main():
    parser = argparse.ArgumentParser()
    add_vasprun_path_argument(parser)
    parser.add_argument("--emin", type=float, default=-10)
    parser.add_argument("--emax", type=float, default=+10)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    plot(
        vasprun_path=cast_vasprun_path(args.vasprun_path),
        emin=args.emin,
        emax=args.emax,
        show=args.show,
    )


def plot(vasprun_path: Path, emin: float, emax: float, show: bool):
    # vasprun.xmlからDOSのデータをCompleteDosクラスとして読み込む
    vasprun = get_vasprun(vasprun_path, parse_dos=True)
    complete_dos = vasprun.complete_dos

    # plotterにTotal DOSを加える
    plotter = DosPlotter()
    plotter.add_dos("Total DOS", complete_dos)

    # 線色を青に変更する
    plot = plotter.get_plot(xlim=[emin, emax])
    lines = plot.get_lines()
    lines[0].set_color("black")

    # 凡例を削除する
    plot.get_legend().remove()

    # プロット図を出力
    set_plot_style()
    plt.xlabel(r"$E - E_{\mathrm{Fermi}}$ (eV)", fontsize=32)
    plt.ylabel("Density of states (states/eV)", fontsize=32)
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.legend().remove()
    plt.savefig("dos.pdf")

    if show:
        plt.show()

    plt.close()
