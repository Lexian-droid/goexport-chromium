# GoExport Chromium

A narrowly scoped [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium) 87 build overlay for native PPAPI Adobe Flash automation.

> [!WARNING]
> Chromium 87 and Adobe Flash are end-of-life software with known security risks. This build is intended only for isolated GoExport automation against trusted local content. Do not use it as a general-purpose browser.

## Pinned source

- Chromium: `87.0.4280.141`
- ungoogled-chromium: `87.0.4280.141-1`
- Hosted Linux build recipe: `ungoogled-chromium-portablelinux 87.0.4280.141-1.1`

This repository stores the small GoExport-specific overlay, build tooling, and validation assets. It does not duplicate Chromium's source tree and does not redistribute Adobe Flash Player.

## What the patch changes

Chromium 87 has several independent Flash gates. Merely changing `ContentSettingsInfo::EPHEMERAL` to `PERSISTENT` does not make Flash run automatically.

The isolated patch in `patches/ungoogled-chromium/enable-automatic-ppapi-flash.patch`:

1. Changes the default plugin content setting from `BLOCK` to `ALLOW`.
2. Makes plugin exceptions persistent instead of ephemeral.
3. Stops converting a default Flash `ALLOW` into `DETECT_IMPORTANT_CONTENT`.
4. Defaults `plugins.run_all_flash_in_allow_mode` to true, avoiding click-to-play for an allowed Flash plugin.
5. Defaults `plugins.allow_outdated` to true so a bundled legacy PPAPI library is not rejected solely by Chromium's stale plugin metadata.

The normal PPAPI discovery path remains intact, including:

```text
--ppapi-flash-path=<absolute plugin path>
--ppapi-flash-version=<version>
```

No OS policy, registry entry, global preference, or pre-edited browser profile is required.

## Builds

The release workflow now uses Ungoogled Chromium's Chromium 87 portable-Linux build recipe rather than attempting to assemble a modern host toolchain around the source archive. The GoExport Flash patch is appended as the final platform patch, after Ungoogled Chromium and its platform patches.

Current GitHub-hosted releases provide portable Linux x64. Chromium 87 Windows and macOS packaging need historical self-hosted builders; this is documented in [BUILDING.md](BUILDING.md).

## Runtime

Supply a legally obtained PPAPI Flash library at launch:

```text
chrome --user-data-dir=<temporary-profile> \
  --ppapi-flash-path=<absolute-path-to-pepflashplayer> \
  --ppapi-flash-version=<plugin-version> \
  tests/flash-smoke/index.html
```

The plugin library filename is platform-specific:

- Windows: `pepflashplayer.dll`
- Linux: `libpepflashplayer.so`
- macOS: `PepperFlashPlayer.plugin`

Use a Flash build whose license permits your intended use and redistribution. This project intentionally ships no Adobe binaries.

## Validation

`python3 scripts/verify_patch.py <chromium-src>` verifies the patched invariants directly in the prepared source tree.

`tests/flash-smoke/index.html` provides a deterministic local smoke page. Full validation still requires a compatible PPAPI library:

- Chromium starts.
- The PPAPI library is discovered.
- the SWF embed is not replaced by Chromium's permission blocker.
- the same fresh profile works after restarting Chromium.
- no machine-wide configuration is present or required.

## Licensing

The build overlay and scripts in this repository are released under BSD-3-Clause. Chromium and ungoogled-chromium retain their respective licenses. Adobe Flash Player is not part of this repository.
