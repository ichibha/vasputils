#!/usr/bin/env python3
import argparse
import functools
import xml.etree.ElementTree as ET

from pymatgen.io.vasp import Vasprun


def get_vasprun_path(parser: argparse.ArgumentParser) -> str:
    parser.add_argument("vasprun_filepath", type=str, help="Path to the vasprun.xml")
    args = parser.parse_args()
    return args.vasprun_filepath


def get_vasprun(parser: argparse.ArgumentParser):
    return Vasprun(get_vasprun_path(parser))


def warn_nonconvergence(vasprun: Vasprun):
    if not vasprun.converged_electronic:
        print("Warning: SCF steps not converged.")
    if not vasprun.converged_ionic:
        print("Warning: Ionic steps not converged.")


def process_vasprun_decorator(description):
    def decorator(process_vasprun):
        @functools.wraps(process_vasprun)
        def wrapper():
            parser = argparse.ArgumentParser(description=description)
            vasprun = get_vasprun(parser)
            warn_nonconvergence(vasprun)
            return process_vasprun(vasprun)

        return wrapper

    return decorator


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
