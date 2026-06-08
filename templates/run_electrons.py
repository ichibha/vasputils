#!/usr/bin/env python3
import shutil
from pathlib import Path

from ase import Atoms
from ase.calculators.vasp import Vasp
from ase.io import read
from vasputils import is_converged

# directories
scf_dir = Path("scf")
resume_dir = Path("resume")
dos_dir = Path("dos")
bands_dir = Path("bands")
dielectric_dir = Path("dielectric")


def main():
    # 構造を読み込み
    atoms = read(Path("~/vasp_tutorial/str/sio2_mp6930.vasp").expanduser())

    # scf
    run_vasp(atoms, scf_dir)

    # resume
    resume_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(scf_dir / "WAVECAR", resume_dir)
    run_vasp(atoms, resume_dir)

    # dos
    dos_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(scf_dir / "CHGCAR", dos_dir)
    run_vasp(atoms, dos_dir)

    # bands
    bands_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy("KPOINTS.bands", bands_dir / "KPOINTS")
    shutil.copy(scf_dir / "CHGCAR", bands_dir)
    run_vasp(atoms, bands_dir)

    # dielectric
    dielectric_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(scf_dir / "WAVECAR", dielectric_dir)
    run_vasp(atoms, dielectric_dir)


def run_vasp(atoms: Atoms, directory: Path):
    if is_converged(directory):
        return

    if directory in (dos_dir):
        kspacing = 0.15
    else:
        kspacing = 0.30

    if directory in (dos_dir):
        smear = dict(ismear=-5, sigma=None)
    else:
        smear = dict(ismear=0, sigma=0.03)

    if directory in (dos_dir, bands_dir):
        isym = 0
        icharg = 11
    else:
        isym = None
        icharg = None

    if directory in (dos_dir):
        dos = dict(lorbit=11, emin=-20, emax=20, nedos=2000)
    else:
        dos = dict()

    if directory in (dielectric_dir):
        dielectric = dict(lepsilon=True)
    else:
        dielectric = dict()

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
        kspacing=kspacing,
        # smearing
        **smear,
        # scf
        prec="Accurate",
        ediff=1e-6,
        nelm=120,
        isym=isym,
        icharg=icharg,
        # dos
        **dos,
        # dielectric
        **dielectric
    )

    atoms.get_potential_energy()


if __name__ == "__main__":
    main()
