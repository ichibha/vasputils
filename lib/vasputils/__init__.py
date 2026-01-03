from pathlib import Path

from pymatgen.io.vasp import Vasprun


def is_converged(vasprun_path: Path):
    if vasprun_path.exists():
        try:
            return Vasprun(vasprun_path).converged
        except:
            return False
    else:
        return False
