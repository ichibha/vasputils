#!/usr/bin/env python3
import argparse

from pymatgen.io.vasp import Vasprun


def get_vasprun(parser: argparse.ArgumentParser):
    parser.add_argument("vasprun_filepath", type=str, help="Path to the vasprun.xml")
    args = parser.parse_args()
    return Vasprun(args.vasprun_filepath)


def warn_nonconvergence(vasprun: Vasprun):
    if not vasprun.converged_electronic:
        print("Warning: SCF steps not converged.")
    if not vasprun.converged_ionic:
        print("Warning: Ionic steps not converged.")
