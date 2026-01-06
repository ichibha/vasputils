#!/usr/bin/env python3
from collections import Counter
from functools import reduce
from math import gcd
from pathlib import Path

import numpy as np
from ase.io import read
from pymatgen.io.vasp import Vasprun


def is_converged(vasprun_path: Path) -> bool:
    status = get_status(vasprun_path)
    return True if status == "Converged" else False


def get_status(vasprun_path: Path):
    if not vasprun_path.exists():
        return "Not found"

    try:
        vasprun = Vasprun(vasprun_path)
    except Exception as e:
        return f"Failed to load vasprun.xml: {e}"

    if not vasprun.converged_electronic:
        return "Electronic loop is not converged"
    elif not vasprun.converged_ionic:
        return "Ionic loop is not converged"
    else:
        return "Converged"


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
