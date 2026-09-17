#!/usr/bin/env python3
"""Package Chromium build output without adding a Flash binary."""

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=("linux", "windows", "macos"), required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()

    stage = args.destination / f"goexport-chromium-87-{args.platform}-x64"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    if args.platform == "windows":
        patterns = ("chrome.exe", "chromedriver.exe", "*.dll", "*.pak", "*.bin",
                    "locales", "resources")
    elif args.platform == "macos":
        patterns = ("Chromium.app", "chromedriver")
    else:
        patterns = ("chrome", "chromedriver", "chrome_sandbox", "*.so", "*.pak",
                    "*.bin", "locales", "resources")

    copied = 0
    for pattern in patterns:
        for item in args.out_dir.glob(pattern):
            target = stage / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)
            copied += 1
    if copied == 0:
        raise RuntimeError(f"No build outputs found in {args.out_dir}")

    args.destination.mkdir(parents=True, exist_ok=True)
    if args.platform == "windows":
        shutil.make_archive(str(stage), "zip", root_dir=stage.parent, base_dir=stage.name)
    else:
        shutil.make_archive(str(stage), "gztar", root_dir=stage.parent, base_dir=stage.name)
    print(stage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
