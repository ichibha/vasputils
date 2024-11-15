#!/usr/bin/env python3
import argparse
import functools
import os
import re
import shutil
from glob import glob

from pymatgen.core.structure import Structure
from pymatgen.io.vasp import Vasprun


def process_vasprun_decorator(description):
    def decorator(process_vasprun):
        @functools.wraps(process_vasprun)
        def wrapper():
            parser = argparse.ArgumentParser(description=description)
            parser.add_argument("vasprun_path", type=str, help="vasprun.xml path")
            args = parser.parse_args()
            vasprun = Vasprun(args.vasprun_path)
            return process_vasprun(vasprun)

        return wrapper

    return decorator


def process_poscar_decorator(description):
    def decorator(process_poscar):
        @functools.wraps(process_poscar)
        def wrapper():
            parser = argparse.ArgumentParser(description=description)
            parser.add_argument("poscar_path", type=str, help="POSCAR path")
            args = parser.parse_args()
            return process_poscar(args.poscar_path)

        return wrapper

    return decorator


def search_directories(pattern: str, root_directory: str):
    directories = [
        os.path.abspath(path)
        for path in glob(os.path.join(root_directory, "*"))
        if os.path.isdir(path) and re.match(pattern, os.path.basename(path))
    ]
    return sorted(directories)


def search_numbered_directories(root_directory: str):
    return search_directories("^[0-9]+$", root_directory)


def prepare_vasp_input(
    directory: str,
    incar: str,
    poscar: str,
    potcar: str,
    kpoints: str,
    wavecar: str = None,
    softlink: bool = False,
):
    try:
        os.makedirs(directory)
    except Exception as e:
        raise Exception(f"Failed to create {directory}:", e)
    copy = os.symlink if softlink else shutil.copy
    copy(os.path.abspath(poscar), os.path.join(directory, "POSCAR"))
    copy(os.path.abspath(incar), os.path.join(directory, "INCAR"))
    copy(os.path.abspath(potcar), os.path.join(directory, "POTCAR"))
    copy(os.path.abspath(kpoints), os.path.join(directory, "KPOINTS"))
    if wavecar:
        copy(os.path.abspath(wavecar), os.path.join(directory, "WAVECAR"))
