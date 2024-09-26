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


def get_epsilon(vasprun_path):
    # XMLファイルをパースし、そのルート要素を取得する
    root = ET.parse(vasprun_path).getroot()

    # XML構造内で誘電率テンソルを含むarray要素を取得する
    epsilon_elements = root.findall(".//varray[@name='epsilon']/v")

    # 抽出した誘電率テンソルを格納するための空リストを初期化する
    epsilon_array: list[list[float]] = []

    # epsilon_elementsから各行を取得し、floatリストに変換し、epsilon_arrayに追加する
    for element in epsilon_elements:
        epsilon_array.append(list(map(float, element.text.split())))

    # 誘電率テンソルを3x3のfloat配列として返す
    return epsilon_array


def get_born_charges(vasprun_path):
    # vasprun.xmlファイルをパースし、そのルート要素を取得する
    root = ET.parse(vasprun_path).getroot()

    # XML構造内でボルン有効電荷テンソルを含むarray要素を取得する
    born_charge_elements_array = root.findall(".//array[@name='born_charges']/set")

    # 抽出したボルン有効電荷テンソルを格納するための空リストを初期化する
    born_charges: list[list[list[float]]] = []

    # 原子ごとにループする
    # born_charge_elementsは当該原子のボルン有効電荷テンソルである
    for born_charge_elements in born_charge_elements_array:
        # 所与の原子のボルン有効電荷テンソルを格納するリストを初期化する
        born_charges.append([])

        # born_charge_elementsから各行を取得し、floatリストに変換し、初期化したリストに追加する
        for element in born_charge_elements.findall("v"):
            born_charges[-1].append(list(map(float, element.text.split())))

    # ボルン有効電荷テンソルのリストを返す。
    return born_charges


def calculate_debye_temperature(debye_frequency_thz: float):
    debye_frequency_hz = debye_frequency_thz * 1e12
    debye_temperature = const.h * debye_frequency_hz / const.Boltzmann
    return debye_temperature
