#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path

from ase import Atoms
from ase.calculators.vasp import Vasp
from ase.io import read
from vasputils import are_forces_converged, is_converged


def main():
    # 変位構造を生成
    subprocess.run("phonopy -d --dim 3 3 2 --nac", shell=True)

    # スーパーセルの計算
    run_vasp(atoms=read("SPOSCAR"), directory=Path("supercell"))

    # スーパーセルの力場が十分に小さいことを確認
    vasprun_path = Path("supercell", "vasprun.xml")
    if not are_forces_converged(vasprun_path, 1e-3):
        print("Forces are not converged.")
        return

    # 変位構造の力場を計算
    for poscar_path in Path().glob("POSCAR-*"):
        atoms = read(poscar_path)
        directory = poscar_path.with_name(poscar_path.name.replace("POSCAR", "FC2"))
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copy("supercell/WAVECAR", directory)
        run_vasp(atoms=atoms, directory=directory)

    # FORCESETSを作成
    subprocess.run("phonopy -f FC2-*/vasprun.xml", shell=True)

    # ポスト解析のパラメータ
    mesh = "16 16 16"  # for histgram and integral
    sigma = "0.1"  # for histgram
    band = "0 0 0  0 0 1/2  1/3 1/3 1/2  1/3 1/3 0  1/2 0 1/2  1/2 0 0"  # for bands
    labels = r"$\Gamma$ A H K L M"  # for bands
    tmin, tmax, tstep = "0", "2000", "5"  # for temperature dependence

    # フォノンDOSを作成
    subprocess.run(f"phonopy-load -ps --mesh {mesh} --sigma {sigma}", shell=True)

    # フォノンPDOSを作成
    subprocess.run(
        "phonopy-load -ps --mesh 16 16 16 --sigma 0.1 --pdos auto", shell=True
    )

    # フォノンバンドを作成
    subprocess.run(f"phonopy-load -ps --band {band} --band_labels {labels}", shell=True)

    # フォノンバンド+DOSを作成
    subprocess.run(
        f"phonopy-load -ps --band {band} --band_labels {labels} --mesh {mesh} --sigma {sigma}",
        shell=True,
    )

    # 熱力学的特性
    subprocess.run(
        f"phonopy-load -tps --mesh {mesh} --sigma {sigma} --tmin {tmin} --tmax {tmax} --tstep {tstep}",
        shell=True,
    )


def run_vasp(atoms: Atoms, directory: Path):
    if is_converged(directory):
        return

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
        kpts=(2, 2, 2),
        gamma=True,
        # smearing
        ismear=0,
        sigma=0.03,
        # scf
        prec="Accurate",
        ediff=1e-8,
        nelm=120,
    )

    atoms.get_potential_energy()


if __name__ == "__main__":
    main()
