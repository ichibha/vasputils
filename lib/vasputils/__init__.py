from pathlib import Path

import numpy as np
from ase.io import read
from pymatgen.io.vasp import Vasprun


def is_converged(vasprun_path: Path):
    if vasprun_path.exists():
        try:
            return Vasprun(vasprun_path).converged
        except:
            return False
    else:
        return False


def get_forces(vasprun_path: Path) -> np.ndarray:
    atoms = read(vasprun_path)
    forces = atoms.get_forces()
    return forces

    # # 各原子の力場をベクトルとして表示
    # for i, force in enumerate(forces):
    #     print(f"{i+1:3}: {force[0]:+.3e}  {force[1]:+.3e}  {force[2]:+.3e}")

    # # 各原子の力場の大きさを計算
    # magnitudes = np.linalg.norm(forces, axis=1)


def get_force_magnitudes(vasprun_path: Path) -> np.ndarray:
    forces = get_forces(vasprun_path)
    magnitudes = np.linalg.norm(forces, axis=1)
    return magnitudes


def get_maximum_force_magnitude(vasprun_path: Path) -> tuple[int, float]:
    magnitudes = get_force_magnitudes(vasprun_path)
    index = magnitudes.argmax()
    magnitude = magnitudes[index]
    return index, magnitude
