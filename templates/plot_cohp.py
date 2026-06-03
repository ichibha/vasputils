#!/usr/bin/env python3
import matplotlib.pyplot as plt
from pymatgen.electronic_structure.cohp import CompleteCohp
from pymatgen.electronic_structure.plotter import CohpPlotter


def drawCohp(completeCohp: CompleteCohp, index: int):
    # 指標を文字列に変換する
    index: str = str(index)

    # CohpPlotterを初期化する
    plotter = CohpPlotter()

    # plotterに結合ペアのCOHPを追加する
    plotter.add_cohp(f"Si-O", completeCohp.get_cohp_by_label(index))

    # COHPをプロットする
    plotter.get_plot()

    # データの種類に応じてxラベルと図名を変更する
    if completeCohp.are_coops:
        xlabel = "$-$COOP"
        figure_name = "coop.pdf"
    elif completeCohp.are_cobis:
        xlabel = "$-$COBI"
        figure_name = "cobi.pdf"
    else:
        xlabel = "$-$COHP"
        figure_name = "cohp.pdf"

    plt.xlabel(xlabel, fontsize=32)
    plt.ylabel(r"$E - E_{\mathrm{Fermi}}$ (eV)", fontsize=32)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.savefig(figure_name)
    plt.show()
    plt.close()

# COHPを読み込む
completeCohp = CompleteCohp.from_file(
    fmt="LOBSTER",
    filename="COHPCAR.lobster",
    structure_file="POSCAR",
)

# COOPを読み込む
completeCoop = CompleteCohp.from_file(
    fmt="LOBSTER",
    filename="COOPCAR.lobster",
    structure_file="POSCAR",
    are_coops=True,
)

# COBIを読み込む
completeCobi = CompleteCohp.from_file(
    fmt="LOBSTER",
    filename="COBICAR.lobster",
    structure_file="POSCAR",
    are_cobis=True,
)

drawCohp(completeCohp, 1)
drawCohp(completeCoop, 1)
drawCohp(completeCobi, 1)
