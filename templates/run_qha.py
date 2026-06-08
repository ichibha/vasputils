#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path

import numpy as np
from ase import Atoms
from ase.calculators.vasp import Vasp
from ase.io import read
from matplotlib import pyplot as plt

from vasputils import are_forces_converged, get_lattice, get_total_energy, is_converged

# matplotlib settings
plt.rcParams["font.size"] = 18
plt.rcParams["figure.titlesize"] = 18
plt.rcParams["axes.labelsize"] = 18
plt.rcParams["xtick.labelsize"] = 14
plt.rcParams["ytick.labelsize"] = 14
plt.rcParams["legend.fontsize"] = 14
plt.rcParams["figure.autolayout"] = True
plt.rcParams["axes.formatter.useoffset"] = False

# global variables
atoms_vcrelax = read("POSCAR")
scales = np.arange(0.95, 1.05 + 1e-8, 0.01)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runtype", type=str, choices=["relax", "ev", "harmonic", "all"])
    args = parser.parse_args()
    runtype = str(args.runtype)

    if runtype in ("relax", "all"):
        for scale in scales:
            run_relax(scale)

    if runtype in ("ev", "all"):
        write_ev()

    if runtype in ("harmonic", "all"):
        for scale in scales:
            run_harmonic(scale)


def run_relax(scale: float):
    atoms = atoms_vcrelax.copy()
    atoms.set_cell(atoms_vcrelax.cell * scale, scale_atoms=True)
    directory = Path(f"scale_{scale:.2f}", "relax")
    run_vasp(atoms, directory, "relax")


def write_ev():
    # e-v.datを作成
    volumes = []
    energies = []
    for scale in scales:
        directory = Path(f"scale_{scale:.2f}", "relax")
        volumes.append(get_lattice(directory / "CONTCAR").volume)
        energies.append(get_total_energy(directory / "vasprun.xml"))

    with open("e-v.dat", "w") as fout:
        fout.write("# Volume(A^3) Energy(eV)\n")
        for volume, energy in zip(volumes, energies):
            fout.write(f"{volume} {energy}\n")

    # e-v.datをプロット
    volumes, energies = np.loadtxt("e-v.dat", unpack=True)
    plt.plot(volumes, energies, marker="o")
    plt.axvline(
        get_lattice("POSCAR").volume, label="scale=1.0", color="k", linestyle="dotted"
    )
    plt.xlabel("Volume ($\mathrm{\AA}^3$)")
    plt.ylabel("Total energy (eV)")
    plt.legend()
    plt.savefig("e-v.pdf")
    plt.close()


def run_harmonic(scale: float):
    # 変位構造とスーパーセルを生成
    root_directory = Path(f"scale_{scale:.2f}")
    shutil.copy(root_directory / "relax" / "CONTCAR", root_directory / "POSCAR")
    subprocess.run("phonopy -d --dim 3 3 2 --nac", shell=True, cwd=root_directory)

    # スーパーセルの計算
    run_vasp(
        atoms=read(root_directory / "SPOSCAR"),
        directory=root_directory / "supercell",
        runtype="forceset",
    )

    # スーパーセルの力場が十分に小さいことを確認
    vasprun_path = Path(root_directory, "supercell", "vasprun.xml")
    if not are_forces_converged(vasprun_path, 1e-3):
        print("Forces are not converged.")
        return

    # 変位構造の力場を計算
    for poscar_path in root_directory.glob("POSCAR-*"):
        atoms = read(poscar_path)
        directory = poscar_path.with_name(poscar_path.name.replace("POSCAR", "FC2"))
        directory.mkdir(exist_ok=True)
        shutil.copy(root_directory / "relax" / "WAVECAR", directory)
        run_vasp(atoms, directory, runtype="forceset")

    # FORCESETSを作成
    subprocess.run("phonopy -f FC2-*/vasprun.xml", shell=True, cwd=root_directory)

    # BORNをコピー
    shutil.copy("BORN", root_directory)

    # ポスト解析のパラメータ
    mesh = "16 16 16"  # for histgram and integral
    sigma = "0.1"  # for histgram
    band = "0 0 0  0 0 1/2  1/3 1/3 1/2  1/3 1/3 0  1/2 0 1/2  1/2 0 0"  # for bands
    labels = r"$\Gamma$ A H K L M"  # for bands
    tmin, tmax, tstep = "0", "2000", "5"  # for temperature dependence

    # フォノンDOSを作成
    subprocess.run(
        f"phonopy-load -ps --mesh {mesh} --sigma {sigma}",
        shell=True,
        cwd=root_directory,
    )

    # フォノンPDOSを作成
    subprocess.run(
        "phonopy-load -ps --mesh 16 16 16 --sigma 0.1 --pdos auto",
        shell=True,
        cwd=root_directory,
    )

    # フォノンバンドを作成
    subprocess.run(
        f"phonopy-load -ps --band {band} --band_labels {labels}",
        shell=True,
        cwd=root_directory,
    )

    # フォノンバンド+DOSを作成
    subprocess.run(
        f"phonopy-load -ps --band {band} --band_labels {labels} --mesh {mesh} --sigma {sigma}",
        shell=True,
        cwd=root_directory,
    )

    # 熱力学的特性
    subprocess.run(
        f"phonopy-load -tps --mesh {mesh} --sigma {sigma} --tmin {tmin} --tmax {tmax} --tstep {tstep}",
        shell=True,
        cwd=root_directory,
    )


def run_vasp(atoms: Atoms, directory: Path, runtype: str):
    if is_converged(directory):
        return

    if runtype == "relax":
        kpts = (6, 6, 4)
        relaxation = dict(isif=2, ibrion=1, ediffg=-1e-3, nsw=200)
    elif runtype == "forceset":
        kpts = (2, 2, 2)
        relaxation = dict()

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
        kpts=kpts,
        gamma=True,
        # smearing
        ismear=0,
        sigma=0.03,
        # scf
        prec="Accurate",
        ediff=1e-8,
        nelm=120,
        # relaxation
        **relaxation,
    )

    atoms.get_potential_energy()


if __name__ == "__main__":
    main()
