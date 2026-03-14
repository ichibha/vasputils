#!/usr/bin/env python3
import argparse
from argparse import ArgumentParser
from os import PathLike
from pathlib import Path
from typing import Iterable

import numpy as np
from ase.io import read
from pymatgen.core import Structure
from pymatgen.io.vasp import Vasprun
from vasputils._status import Status


def get_vasprun(
    vasprun_path: Path,
    parse_dos=False,
    parse_eigen=False,
    parse_projected_eigen=False,
    parse_potcar_file=False,
):
    return Vasprun(
        vasprun_path,
        parse_dos=parse_dos,
        parse_eigen=parse_eigen,
        parse_projected_eigen=parse_projected_eigen,
        parse_potcar_file=parse_potcar_file,
    )


def is_converged(vasprun_path: Path):
    status = get_status(vasprun_path)
    if status == Status.CONVERGED:
        return True
    else:
        return False


def are_forces_converged(vasprun_path: Path, threshold: float):
    force_magnitudes = get_force_magnitudes(vasprun_path)
    return force_magnitudes.max() <= threshold


def get_status(vasprun_path: Path):
    if not vasprun_path.exists():
        return Status.NOT_FOUND

    try:
        vasprun = get_vasprun(vasprun_path)
    except Exception:
        return Status.LOAD_FAILED

    if not vasprun.converged_electronic:
        return Status.ELECTRONIC_NOT_CONVERGED
    elif not vasprun.converged_ionic:
        return Status.IONIC_NOT_CONVERGED
    else:
        return Status.CONVERGED


def get_fu(vasprun_path: Path):
    vasprun = get_vasprun(vasprun_path)
    comp = vasprun.final_structure.composition
    return comp.num_atoms / comp.reduced_composition.num_atoms


def get_total_energy(vasprun_path: Path) -> float:
    atoms = read(vasprun_path)
    total_energy = atoms.get_potential_energy()
    return total_energy


def get_forces(vasprun_path: Path) -> np.ndarray:
    atoms = read(vasprun_path)
    forces = atoms.get_forces()
    return forces


def get_force_magnitudes(vasprun_path: Path) -> np.ndarray:
    forces = get_forces(vasprun_path)
    magnitudes = np.linalg.norm(forces, axis=1)
    return magnitudes


def get_lattice(poscar_path: Path):
    return Structure.from_file(poscar_path).lattice


def cast_vasprun_paths(vasprun_paths: Iterable[PathLike]):
    return [p / "vasprun.xml" if p.is_dir() else p for p in map(Path, vasprun_paths)]


def add_vasprun_paths_argument(parser: ArgumentParser):
    parser.add_argument(
        "vasprun_paths",
        type=str,
        nargs="+",
        help="Paths of vasprun.xml or directory containing vasprun.xml",
    )


def print_parameter_template(parameter_name: str):
    parser = argparse.ArgumentParser()
    add_vasprun_paths_argument(parser)
    args = vars(parser.parse_args())
    vasprun_paths = cast_vasprun_paths(args.get("vasprun_paths"))

    for vasprun_path in vasprun_paths:
        print(vasprun_path, end=": ")
        nelect = get_parameter_value(parameter_name, vasprun_path)
        print(nelect if nelect else get_status(vasprun_path))


def get_parameter_value(parameter_name: str, vasprun_path: Path):
    if is_converged(vasprun_path):
        vasprun = get_vasprun(vasprun_path)
        nelect = vasprun.parameters[parameter_name]
        return int(nelect)
    else:
        return None
