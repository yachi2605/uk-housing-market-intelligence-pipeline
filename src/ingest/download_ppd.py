from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import kagglehub


def copy_dataset_files(src_dir: Path, dst_dir: Path) -> list[Path]:
    dst_dir.mkdir(parents=True, exist_ok=True)

    # copy common dataset file types
    patterns = ["*.csv", "*.txt", "*.zip", "*.parquet"]
    files: list[Path] = []
    for pat in patterns:
        files.extend(src_dir.rglob(pat))

    if not files:
        raise FileNotFoundError(f"No data files found in Kaggle cache folder: {src_dir}")

    copied: list[Path] = []
    for f in files:
        out = dst_dir / f.name
        if out.exists() and out.stat().st_size == f.stat().st_size:
            print(f"✓ Already exists: {out}")
            copied.append(out)
            continue

        print(f"Copying {f} -> {out}")
        shutil.copy2(f, out)
        copied.append(out)

    return copied


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--dataset",
        type=str,
        default="hm-land-registry/uk-housing-prices-paid",
        help="Kaggle dataset slug",
    )
    p.add_argument(
        "--out_dir",
        type=str,
        default="data/raw/kaggle_ppd",
        help="Where to store raw dataset files inside this repo",
    )
    args = p.parse_args()

    # Download to kagglehub cache
    cache_path_str = kagglehub.dataset_download(args.dataset)
    cache_path = Path(cache_path_str)

    print("KaggleHub cache path:", cache_path)

    # Copy into your repo raw folder (so your pipeline is reproducible)
    out_dir = Path(args.out_dir)
    copied = copy_dataset_files(cache_path, out_dir)

    print("\n✓ Files available in repo raw folder:")
    for f in copied:
        print(" -", f)


if __name__ == "__main__":
    main()