#!/usr/bin/env/python3
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
from ase import Atoms
from ase.calculators.vasp import Vasp
from ase.io import read
from vasputils import get_lattice, get_total_energy, is_converged

# matplotlib settings
plt.rcParams["font.size"] = 18
plt.rcParams["figure.titlesize"] = 18
plt.rcParams["axes.labelsize"] = 18
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["legend.fontsize"] = 14
plt.rcParams["figure.autolayout"] = True
plt.rcParams["axes.formatter.useoffset"] = False

# directories
scf_dir = Path("~/vasp_tutorial/electrons_ase/scf").expanduser()
relax_dir = Path("relax")
vcrelax_dir = Path("vcrelax")
pressure_dir = Path("pressure")


def main():
    # ===== 構造最適化 =====
    # relax
    atoms = read(scf_dir / "CONTCAR")
    relax_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(scf_dir / "WAVECAR", relax_dir)
    run_vasp(atoms, relax_dir, isif=2)

    # vcrelax
    atoms = read(relax_dir / "CONTCAR")
    vcrelax_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(relax_dir / "WAVECAR", vcrelax_dir)
    run_vasp(atoms, vcrelax_dir, isif=3)

    # scf/relax/vcrelaxのエネルギー比較
    print("Total energy (eV)")
    print(f"    scf: {get_total_energy(scf_dir / 'vasprun.xml'): .4f}")
    print(f"  relax: {get_total_energy(relax_dir / 'vasprun.xml'): .4f}")
    print(f"vcrelax: {get_total_energy(vcrelax_dir / 'vasprun.xml'): .4f}")

    # ===== 圧力下のvcrelax =====
    # vcrelaxの結果をP=0GPaの結果として「pressure/0」にコピー
    shutil.copytree(vcrelax_dir, pressure_dir / "0", dirs_exist_ok=True)
    previous_directory = pressure_dir / "0"

    # 各圧力の計算
    for pressure_gpa in range(25, 101, 25):
        # 計算ディレクトリを作成
        directory = pressure_dir / str(pressure_gpa)
        directory.mkdir(parents=True, exist_ok=True)

        # 圧力の一段階低い計算から緩和構造と波動関数を継承
        atoms = read(previous_directory / "CONTCAR")
        shutil.copy(previous_directory / "WAVECAR", directory)

        # VASP計算を実行
        run_vasp(atoms, directory, isif=3, pressure_gpa=pressure_gpa)

        # 次のループのため、previous_directoryを更新
        previous_directory = directory

    # 圧力-体積 プロット
    pressures_gpa = list(range(0, 101, 25))
    volumes = [
        get_lattice(pressure_dir / str(p) / "CONTCAR").volume for p in pressures_gpa
    ]
    plt.plot(pressures_gpa, volumes, marker="o")
    plt.xlabel("Pressure (GPa)")
    plt.ylabel("Volume ($\mathrm{\AA}^3$)")
    plt.savefig("pv.pdf")
    plt.close()


def run_vasp(atoms: Atoms, directory: Path, isif: int, pressure_gpa: float = 0):
    if is_converged(directory):
        return

    atoms.calc = Vasp(
        # ase
        directory=directory,
        # functional
        gga="PE",
        # pseudopotentials
        pp="PBE",
        setups=dict(Si="", O=""),
        # cutoff energy
        encut=520,
        # k-mesh
        kspacing=0.3,
        # smearing
        ismear=0,
        sigma=0.03,
        # scf
        prec="Accurate",
        ediff=1e-6,
        nelm=120,
        # ionic steps
        isif=isif,
        ibrion=1,
        ediffg=-1e-2,
        nsw=200,
        pstress=pressure_gpa * 10,  # GPa -> kbar
    )

    atoms.get_potential_energy()


if __name__ == "__main__":
    main()
