# Building GoExport Chromium

## Why full builds use self-hosted runners

Chromium 87 is a 2020 codebase with a large checkout and strict host-toolchain expectations. A clean source tree plus build output commonly needs tens of gigabytes, while a release build can run for hours.

As of this project's creation, standard modern GitHub-hosted images are not a reliable target:

- Windows x64: Chromium 87 expects the Visual Studio 2019-era Chromium toolchain. Current hosted images primarily target newer Visual Studio releases.
- macOS x64: Chromium 87 predates current Xcode/macOS SDKs, while older Intel runner images have been retired over time.
- Linux x64: a build is the most feasible of the three, but standard runner disk and six-hour job limits make a clean release build unreliable.

The release workflow therefore pins logical self-hosted labels and keeps the small source-patch validation job on `ubuntu-22.04`. This is deliberate: it does not silently omit a platform or publish an artifact from an unverified partial build.

## Builder labels

Register one ephemeral x64 runner for each label:

- `goexport-chromium-linux-x64`
- `goexport-chromium-windows-x64`
- `goexport-chromium-macos-x64`

Each runner must also carry the standard `self-hosted` and OS labels.

Recommended minimum: 16 CPU cores, 32 GB RAM, 150 GB free disk, and a persistent download cache between ephemeral jobs.

## Host prerequisites

All builders need:

- Git
- Python 3.8 or a compatible Python 3 release
- Ninja
- C/C++ toolchains supported by Chromium 87
- system build dependencies required by the corresponding ungoogled-chromium platform
- enough disk for the downloaded source and `out/GoExport`

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

Cache `build/download-cache` on trusted runners. Do not cache `build/src` across untrusted pull requests because it is executable build input.

## Adobe Flash

No Flash binary is downloaded or packaged. Supply a compatible PPAPI library at runtime with `--ppapi-flash-path` and `--ppapi-flash-version`. Adobe's post-EOL kill switch is inside Adobe's binary, not Chromium's permission code; choose a legally obtained build appropriate to your environment.
