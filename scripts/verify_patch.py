#!/usr/bin/env python3
"""Verify the GoExport Flash invariants in a prepared Chromium 87 tree."""

import argparse
from pathlib import Path


CHECKS = {
    "components/content_settings/core/browser/content_settings_registry.cc": [
        'Register(ContentSettingsType::PLUGINS, "plugins", CONTENT_SETTING_ALLOW,',
        "ContentSettingsInfo::PERSISTENT,",
    ],
    "chrome/browser/plugins/plugin_info_host_impl.cc": [
        "RegisterBooleanPref(prefs::kPluginsAllowOutdated, true);",
        "RegisterBooleanPref(prefs::kRunAllFlashInAllowMode, true);",
    ],
}

FORBIDDEN = {
    "chrome/browser/plugins/plugin_utils.cc": [
        "ALLOW-by-default is obsolete and should be treated as DETECT.",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    failures: list[str] = []

    for relative, needles in CHECKS.items():
        text = (args.source / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                failures.append(f"{relative}: missing {needle!r}")

    for relative, needles in FORBIDDEN.items():
        text = (args.source / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle in text:
                failures.append(f"{relative}: obsolete Flash demotion remains: {needle!r}")

    if failures:
        print("\n".join(failures))
        return 1

    print("Verified Chromium 87 automatic Flash permission invariants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
