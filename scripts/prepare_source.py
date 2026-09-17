#!/usr/bin/env python3
"""Fetch, prepare, and patch the pinned ungoogled-chromium source tree."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config/source.json").read_text(encoding="utf-8"))
PATCH = ROOT / "patches/ungoogled-chromium/enable-automatic-ppapi-flash.patch"


def run(*args: str, cwd: Path | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()

    work = args.work_dir.resolve()
    uc = work / "ungoogled-chromium"
    source = work / "src"
    cache = work / "download-cache"
    work.mkdir(parents=True, exist_ok=True)

    if not uc.exists():
        run(
            "git", "clone", "--depth", "1", "--branch",
            CONFIG["ungoogled_chromium_ref"],
            CONFIG["ungoogled_chromium_repository"], str(uc),
        )

    actual = (uc / "chromium_version.txt").read_text(encoding="utf-8").strip()
    if actual != CONFIG["chromium_version"]:
        raise RuntimeError(f"Pinned source mismatch: expected {CONFIG['chromium_version']}, got {actual}")

    if not args.skip_download:
        cache.mkdir(parents=True, exist_ok=True)
        run(sys.executable, "utils/downloads.py", "retrieve", "-c", str(cache),
            "-i", "downloads.ini", cwd=uc)
        if source.exists():
            shutil.rmtree(source)
        run(sys.executable, "utils/downloads.py", "unpack", "-c", str(cache),
            "-i", "downloads.ini", "--", str(source), cwd=uc)

    if not source.exists():
        raise RuntimeError(f"Chromium source directory does not exist: {source}")

    run(sys.executable, "utils/prune_binaries.py", str(source), "pruning.list", cwd=uc)
    run(sys.executable, "utils/patches.py", "apply", str(source), "patches", cwd=uc)
    run(
        sys.executable, "utils/domain_substitution.py", "apply",
        "-r", "domain_regex.list", "-f", "domain_substitution.list",
        "-c", str(work / "domsubcache.tar.gz"), str(source), cwd=uc,
    )
    run("git", "apply", "--check", str(PATCH), cwd=source)
    run("git", "apply", str(PATCH), cwd=source)
    run(sys.executable, str(ROOT / "scripts/verify_patch.py"), str(source))
    print(source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
