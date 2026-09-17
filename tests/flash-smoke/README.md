# Flash smoke test

Place a small, legally redistributable test movie at `fixture.swf`, then serve this directory over HTTP:

```bash
python3 -m http.server 8765 --directory tests/flash-smoke
```

Launch the custom browser with a new temporary profile and your PPAPI library:

```text
chrome --user-data-dir=<empty-profile> --ppapi-flash-path=<plugin> --ppapi-flash-version=<version> http://127.0.0.1:8765/
```

Expected result:

1. The page title reports `PASS: PPAPI Flash detected`.
2. The object is not replaced by Chromium's Flash permission UI.
3. Restart Chromium with the same command and profile; the result remains unchanged.
4. Repeat with a second empty profile to prove the behavior comes from the executable defaults rather than repaired preferences.
5. Confirm no OS policy, registry, or global Chromium configuration was created.

Plugin detection proves Chromium discovered and advertised PPAPI Flash. Successful playback of `fixture.swf` proves the plugin binary itself can execute; this matters because some Adobe binaries contain their own post-EOL kill switch.
