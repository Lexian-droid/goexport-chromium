#!/usr/bin/env python3
"""Build and package the pinned GoExport Chromium source on a prepared builder."""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=("linux", "windows", "macos"), required=True)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    parser.add_argument("--work-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--skip-prepare", action="store_true")
    args = parser.parse_args()

    expected = {"Linux": "linux", "Windows": "windows", "Darwin": "macos"}[platform.system()]
    if expected != args.platform:
        raise RuntimeError(f"--platform {args.platform} does not match host {platform.system()}")

    if not args.skip_prepare:
        run(sys.executable, str(ROOT / "scripts/prepare_source.py"),
            "--work-dir", str(args.work_dir))

    source = args.work_dir.resolve() / "src"
    out = source / "out" / "GoExport"
    out.mkdir(parents=True, exist_ok=True)

    gn = shutil.which("gn")
    if not gn:
        bootstrap = source / "tools/gn/bootstrap/bootstrap.py"
        run(sys.executable, str(bootstrap), "--skip-generate-buildfiles",
            "-j", str(args.jobs), "-o", str(out), cwd=source)
        gn = str(out / ("gn.exe" if args.platform == "windows" else "gn"))

    gn_args = [
        "is_debug=false",
        "is_official_build=true",
        "is_component_build=false",
        "symbol_level=0",
        "blink_symbol_level=0",
        # Official Chromium 87 builds default to PGO phase 2, but the standalone
        # source archive does not contain Google's matching profile data.
        "chrome_pgo_phase=0",
        # Ungoogled Chromium's build configuration expects this Chromium 87
        # Safe Browsing switch even when Safe Browsing is compiled out.
        "safe_browsing_mode=0",
        "enable_plugins=true",
        "enable_nacl=false",
        "enable_widevine=false",
        "proprietary_codecs=false",
    ]
    (out / "args.gn").write_text("\n".join(gn_args) + "\n", encoding="utf-8")
    run(gn, "gen", str(out), "--fail-on-unused-args", cwd=source)

    ninja = shutil.which("autoninja") or shutil.which("ninja")
    if not ninja:
        raise RuntimeError("ninja or autoninja must be available on PATH")
    run(ninja, "-C", str(out), "-j", str(args.jobs), "chrome", "chromedriver", cwd=source)
    run(sys.executable, str(ROOT / "scripts/package.py"), "--platform", args.platform,
        "--out-dir", str(out), "--destination", str(ROOT / "dist"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
