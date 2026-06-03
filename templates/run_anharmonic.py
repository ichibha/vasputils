#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

from ase import Atoms
from ase.calculators.vasp import Vasp
from ase.io import read
from vasputils import is_converged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runtype", type=str, choices=["fc2", "fc3", "raman"])
    args = parser.parse_args()
    runtype = str(args.runtype)

    if runtype == "fc2":
        run_fc2()
    elif runtype == "fc3":
        run_fc3()
    elif runtype == "raman":
        run_raman()


def run_fc2():
    for poscar_path in Path().glob("POSCAR_FC2-*"):
        atoms = read(poscar_path)
        directory = poscar_path.with_name(poscar_path.name.removeprefix("POSCAR_"))
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copy("supercell_fc2/WAVECAR", directory)
        run_vasp(atoms, directory, "fc2")


def run_fc3():
    for poscar_path in Path().glob("POSCAR-*"):
        atoms = read(poscar_path)
        directory = poscar_path.with_name(poscar_path.name.replace("POSCAR", "FC3"))
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copy("supercell_fc3/WAVECAR", directory)
        run_vasp(atoms, directory, "fc3")


def run_raman():
    for poscar_path in Path().glob("Raman-POSCAR.*.*.vasp"):
        atoms = read(poscar_path)
        dirname = poscar_path.name.replace("POSCAR.", "").removesuffix(".vasp")
        directory = poscar_path.with_name(dirname)
        run_vasp(atoms, directory, "raman")


def run_vasp(atoms: Atoms, directory: Path, runtype: str):
    if is_converged(directory):
        return

    if runtype == "fc2":
        kmesh = dict(kpts=(2, 2, 2), gamma=True)
        dielectric = dict()
    elif runtype == "fc3":
        kmesh = dict(kpts=(3, 3, 4), gamma=True)
        dielectric = dict()
    elif runtype == "raman":
        kmesh = dict(kspacing=0.3, gamma=True)
        dielectric = dict(lepsilon=True)

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
        **kmesh,
        # smearing
        ismear=0,
        sigma=0.03,
        # scf
        prec="Accurate",
        ediff=1e-8,
        nelm=120,
        # dielectric
        **dielectric
    )

    atoms.get_potential_energy()


if __name__ == "__main__":
    main()
