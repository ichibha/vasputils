#!/usr/bin/env python3
from pathlib import Path

import numpy as np
from ase.io import read
from pymatgen.core import Structure
from pymatgen.io.vasp import Vasprun
from vasputils._status import Status


def is_converged(vasprun_path: Path) -> bool:
    status = get_status(vasprun_path)

    if status == Status.CONVERGED:
        return True
    elif status == Status.IS_DIRECTORY:
        raise ValueError(f"{vasprun_path} is directory, not vasprun.xml.")
    else:
        return False


def get_status(vasprun_path: Path):
    if not vasprun_path.exists():
        return Status.NOT_FOUND
    elif vasprun_path.is_dir():
        return Status.IS_DIRECTORY

    try:
        vasprun = Vasprun(vasprun_path)
    except Exception:
        return Status.LOAD_FAILED

    if not vasprun.converged_electronic:
        return Status.ELECTRONIC_NOT_CONVERGED
    elif not vasprun.converged_ionic:
        return Status.IONIC_NOT_CONVERGED
    else:
        return Status.CONVERGED


def get_fu(vasprun_path: Path):
    vasprun = Vasprun(vasprun_path)
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
