#!/usr/bin/env python3
from pathlib import Path

import numpy as np
from ase.io import read
from pymatgen.core import Structure
from pymatgen.io.vasp import Vasprun
from vasputils._status import Status


def is_converged(_vasprun_path_or_directory: Path):
    if _vasprun_path_or_directory.is_dir():
        vasprun_path = _vasprun_path_or_directory / "vasprun.xml"
    else:
        vasprun_path = _vasprun_path_or_directory

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
