#!/usr/bin/env python3
import argparse
import functools
import os
import xml.etree.ElementTree as ET

import scipy.constants as const
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


def calculate_debye_temperature(debye_frequency_thz: float):
    debye_frequency_hz = debye_frequency_thz * 1e12
    debye_temperature = const.h * debye_frequency_hz / const.Boltzmann
    return debye_temperature
