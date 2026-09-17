# Building GoExport Chromium

## GitHub-hosted build experiment

The release workflow attempts all three x64 builds on current GitHub-hosted images:

- Linux: `ubuntu-24.04`
- Windows: `windows-2025`
- macOS Intel: `macos-15-intel`

This is intentionally an experiment against real current runners. Chromium 87 is a 2020 codebase, so failures caused by modern Python, compiler, SDK, system-library, disk, or six-hour job limits are expected to be fixed from the resulting logs rather than hidden behind nonexistent runner labels.

The Linux job removes several unrelated preinstalled SDK directories to recover build space. Windows and macOS initially run without destructive cleanup so their actual free-space and toolchain failures remain visible.

## Host prerequisites

A local builder needs:

- Git
- Python 3
- Ninja
- a C/C++ toolchain accepted by Chromium 87
- system build dependencies required by the corresponding ungoogled-chromium platform
- enough disk for Chromium source and `out/GoExport`

Platform-specific packaging projects remain useful references:

- [Portable Linux](https://github.com/ungoogled-software/ungoogled-chromium-portablelinux)
- [Windows](https://github.com/ungoogled-software/ungoogled-chromium-windows)
- [macOS](https://github.com/ungoogled-software/ungoogled-chromium-macos)

## Build command

```text
python scripts/build.py --platform <linux|windows|macos> --jobs <count>
```

The script:

1. clones ungoogled-chromium tag `87.0.4280.141-1`;
2. downloads Chromium `87.0.4280.141`;
3. prunes binaries and applies the upstream ungoogled patch series;
4. applies the isolated GoExport Flash patch;
5. verifies the source invariants;
6. generates an official non-component build;
7. builds Chromium and ChromeDriver;
8. packages a portable archive without Flash.

## Cache

Cache `build/download-cache` only on trusted runners. Do not cache `build/src` across untrusted pull requests because it is executable build input.

## Adobe Flash

No Flash binary is downloaded or packaged. Supply a compatible PPAPI library at runtime with `--ppapi-flash-path` and `--ppapi-flash-version`. Adobe's post-EOL kill switch is inside Adobe's binary, not Chromium's permission code; choose a legally obtained build appropriate to your environment.
