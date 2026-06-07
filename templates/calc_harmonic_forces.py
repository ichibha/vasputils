#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path


def main():
    for poscar_path in Path().glob("POSCAR-*"):
        dirname = poscar_path.name.replace("POSCAR", "FC2")
        directory = poscar_path.with_name(dirname)
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copy(poscar_path, directory / "POSCAR")
        shutil.copy("supercell/INCAR", directory)
        shutil.copy("supercell/KPOINTS", directory)
        shutil.copy("supercell/POTCAR", directory)
        shutil.copy("supercell/WAVECAR", directory)
        subprocess.run("mpirun vasp_std | tee vasp.out", shell=True)


if __name__ == "__main__":
    main()
