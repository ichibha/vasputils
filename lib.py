#!/usr/bin/env python3
import argparse
import functools
import os
import re
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


def get_pymatgen_structure(poscar_path: str):
    # POSCARファイルの存在確認
    if not os.path.exists(poscar_path):
        raise FileNotFoundError(f"{poscar_path} not found.")
    # POSCARを読み込む
    try:
        return Structure.from_file(poscar_path)
    except Exception as e:
        raise RuntimeError(f"Failed to read {poscar_path}: {e}")


def search_numbered_directories(root_directory: str):
    return search_directories("^[0-9]+$", root_directory)


def search_directories(pattern: str, root_directory: str):
    directories = [
        os.path.abspath(directory)
        for directory in glob(os.path.join(root_directory, "*"))
        if re.match(pattern, os.path.basename(directory))
    ]
    return sorted(directories)
