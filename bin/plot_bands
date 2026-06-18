#!/usr/bin/env python3
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from pymatgen.electronic_structure.plotter import BSPlotter
from pymatgen.io.vasp.outputs import BandStructure

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
    # vasprun.xmlからバンド分散データを読み込む
    vasprun = get_vasprun(vasprun_path, parse_dos=True, parse_eigen=True)
    band_structure: BandStructure = vasprun.get_band_structure()

    # BandStructureインスタンスでプロッターを初期化する
    plotter = BSPlotter(band_structure)

    # フェルミエネルギーの上下20eVの範囲でバンド分散をプロットする
    plot = plotter.get_plot(ylim=[emin, emax])

    # フェルミレベルをプロットする
    plt.axhline(0, color="black", linestyle="dotted")
    plot.get_legend().remove()  # 凡例を削除

    # プロット図を出力する
    set_plot_style()
    plt.xlabel("")  # x軸ラベルを削除
    plt.ylabel(r"$E - E_{\mathrm{Fermi}}$ (eV)")
    plt.savefig(vasprun_path.with_name("bands.pdf"))

    if show:
        plt.show()

    plt.close()


if __name__ == "__main__":
    main()
