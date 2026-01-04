#!/usr/bin/env python3
from collections import Counter
from functools import reduce
from math import gcd
from pathlib import Path

import numpy as np
from ase.io import read
from pymatgen.io.vasp import Vasprun


def is_converged(vasprun_path: Path) -> bool:
    if not vasprun_path.exists():
        return False

    try:
        vasprun = Vasprun(
            vasprun_path,
            parse_dos=False,
            parse_eigen=False,
            parse_projected_eigen=False,
            parse_potcar_file=False,
        )
    except:
        return False

    return vasprun.converged


def get_fu(vasprun_path: Path):
    atoms = read(vasprun_path)
    counts = Counter(atoms.get_chemical_symbols())
    fu = reduce(gcd, counts.values())
    return fu


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
