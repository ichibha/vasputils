#!/usr/bin/env python3
import argparse
import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable

import numpy as np
from ase.io import read
from matplotlib import pyplot as plt
from pymatgen.core import Structure
from pymatgen.io.vasp import Vasprun
from vasputils._status import Status


def cast_vasprun_path(vasprun_path: os.PathLike):
    vasprun_path = Path(vasprun_path)

    if vasprun_path.is_dir():
        return vasprun_path / "vasprun.xml"
    else:
        return vasprun_path


def cast_vasprun_paths(vasprun_paths: Iterable[os.PathLike]):
    return list(map(cast_vasprun_path, vasprun_paths))


def get_vasprun(
    vasprun_path: os.PathLike,
    parse_dos=False,
    parse_eigen=False,
    parse_projected_eigen=False,
    parse_potcar_file=False,
):
    return Vasprun(
        cast_vasprun_path(vasprun_path),
        parse_dos=parse_dos,
        parse_eigen=parse_eigen,
        parse_projected_eigen=parse_projected_eigen,
        parse_potcar_file=parse_potcar_file,
    )


def is_converged(vasprun_path: os.PathLike):
    vasprun_path = cast_vasprun_path(vasprun_path)
    status = get_status(vasprun_path)
    return status == Status.CONVERGED


def are_forces_converged(vasprun_path: os.PathLike, threshold: float):
    vasprun_path = cast_vasprun_path(vasprun_path)
    force_magnitudes = get_force_magnitudes(vasprun_path)
    return force_magnitudes.max() <= threshold


def get_status(vasprun_path: os.PathLike):
    vasprun_path = cast_vasprun_path(vasprun_path)

    if not vasprun_path.exists():
        return Status.NOT_FOUND

    try:
        vasprun = get_vasprun(vasprun_path)
    except Exception:
        return Status.LOAD_FAILED

    if not vasprun.converged_electronic:
        return Status.ELECTRONIC_NOT_CONVERGED
    elif not vasprun.converged_ionic:
        return Status.IONIC_NOT_CONVERGED
    else:
        return Status.CONVERGED


def get_fu(vasprun_path: os.PathLike):
    vasprun_path = cast_vasprun_path(vasprun_path)
    vasprun = get_vasprun(vasprun_path)
    comp = vasprun.final_structure.composition
    return comp.num_atoms / comp.reduced_composition.num_atoms


def get_total_energy(vasprun_path: os.PathLike) -> float:
    vasprun_path = cast_vasprun_path(vasprun_path)
    atoms = read(vasprun_path)
    total_energy = atoms.get_potential_energy()
    return total_energy


def get_forces(vasprun_path: os.PathLike) -> np.ndarray:
    vasprun_path = cast_vasprun_path(vasprun_path)
    atoms = read(vasprun_path)
    forces = atoms.get_forces()
    return forces


def get_force_magnitudes(vasprun_path: os.PathLike) -> np.ndarray:
    vasprun_path = cast_vasprun_path(vasprun_path)
    forces = get_forces(vasprun_path)
    magnitudes = np.linalg.norm(forces, axis=1)
    return magnitudes


def get_lattice(poscar_path: os.PathLike):
    return Structure.from_file(poscar_path).lattice


def add_vasprun_path_argument(parser: ArgumentParser):
    parser.add_argument(
        "vasprun_path",
        type=str,
        help="Path of vasprun.xml file or directory containing vasprun.xml file",
        nargs="?",
        default="vasprun.xml",
    )


def add_vasprun_paths_argument(parser: ArgumentParser):
    parser.add_argument(
        "vasprun_paths",
        type=str,
        nargs="*",
        help="Paths of vasprun.xml file or directories containing vasprun.xml files",
        default=["vasprun.xml"],
    )


def print_parameter_template(param_name: str):
    parser = argparse.ArgumentParser()
    add_vasprun_paths_argument(parser)
    args = vars(parser.parse_args())
    vasprun_paths = cast_vasprun_paths(args.get("vasprun_paths"))

    for vasprun_path in vasprun_paths:
        print(vasprun_path, end=": ")

        param_value = get_parameter_value(param_name, vasprun_path)
        if param_value is None:
            print(get_status(vasprun_path))
        else:
            print(param_value)


def get_parameter_value(param_name: str, vasprun_path: os.PathLike):
    vasprun_path = cast_vasprun_path(vasprun_path)

    if is_converged(vasprun_path):
        vasprun = get_vasprun(vasprun_path)
        param_value = vasprun.parameters[param_name]
        return param_value
    else:
        return None


def set_plot_style(
    title_size=18, label_size=18, xtick_size=14, ytick_size=14, legend_size=14
):
    plt.rcParams["font.size"] = 18
    plt.rcParams["figure.titlesize"] = title_size
    plt.rcParams["axes.labelsize"] = label_size
    plt.rcParams["xtick.labelsize"] = xtick_size
    plt.rcParams["ytick.labelsize"] = ytick_size
    plt.rcParams["legend.fontsize"] = legend_size
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams["axes.formatter.useoffset"] = False
