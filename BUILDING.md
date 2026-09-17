# Building GoExport Chromium

## Hosted Linux x64 release

GitHub Actions uses the exact Chromium 87 platform build recipe from:

- `ungoogled-chromium-portablelinux 87.0.4280.141-1.1`

That recipe supplies the legacy Docker build stages, portable-Linux GN flags, platform patches, and packaging behavior expected by Ungoogled Chromium 87. The workflow copies GoExport's Flash patch into the platform patch series so it is applied after both the base Ungoogled Chromium and platform-specific patches.

The build runs on `ubuntu-24.04` only as a Docker host. The compiler and build dependencies are defined by the historical platform recipe, not the current Ubuntu image.

## Windows x64

The matching `ungoogled-chromium-windows 87.0.4280.141-1.1` recipe requires:

- Visual Studio 2019-era C++ tools;
- Python 2.7 with `pypiwin32`;
- Python 3;
- historical LLVM and Node build inputs.

Those requirements are not reliably obtainable or supportable on current GitHub-hosted Windows images. In particular, the platform recipe downloads a 2020 LLVM snapshot and invokes Python 2 Chromium scripts. This repository intentionally does not label a current hosted runner as a working Windows build.

To create a Windows build, use a dedicated self-hosted Windows VM with the toolchain specified by the pinned platform recipe. Copy the GoExport Flash patch into that recipe's `patches/goexport/` directory and append this line to `patches/series`:

```text
goexport/enable-automatic-ppapi-flash.patch
```

## macOS x64

Ungoogled Chromium's macOS platform repository has no `87.0.4280.141` recipe. Its final Chromium 87 recipes are older point releases and require Xcode 8–9 plus Python 2.7. Current `macos-15-intel` runners ship a much newer Xcode and cannot provide a reliable Chromium 87 build environment.

A macOS release therefore requires a self-hosted Intel macOS builder with the historical Xcode/Python environment, using the closest supported Chromium 87 macOS platform recipe. It must be released under that actual Chromium version, not falsely labeled as `87.0.4280.141`.

## Local Linux build

Use the pinned platform project:

```bash
git clone --branch 87.0.4280.141-1.1 --recurse-submodules \
  https://github.com/ungoogled-software/ungoogled-chromium-portablelinux.git
cd ungoogled-chromium-portablelinux
mkdir -p patches/goexport
cp /path/to/enable-automatic-ppapi-flash.patch patches/goexport/
printf '\ngoexport/enable-automatic-ppapi-flash.patch\n' >> patches/series
./docker-build.sh
```

The archive is created under `build/`. No Adobe Flash binary is downloaded or packaged.

## Validation

Run the resulting executable against `tests/flash-smoke/index.html` with a legally obtained PPAPI Flash library supplied through `--ppapi-flash-path` and `--ppapi-flash-version`. Verify that the plugin is detected, the page does not show the Flash permission block, and it still works after a full browser restart using a new profile.
