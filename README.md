# craft-bridges

Every bridge for [Craft Unofficial Launcher](https://github.com/YalKouassi/craft-unofficial-launcher),
and their releases, in one repo. A bridge mirrors an upstream app's releases, renamed to the
launcher's contract and with a `craft-app.json` added, so the launcher can install and update the
app. The bridges are unofficial and are not affiliated with or endorsed by the apps' authors or by
ArtCraft.

This is a **shared release repo** (the launcher's spec, section 6): every app's releases are
published here, tagged `<id>-v<version>` (`mailcraft-v0.10.0`), and the launcher lists each app as
`YalKouassi/craft-bridges#<id>`. Launcher 0.11.0 or newer reads it. To see one app's releases,
search the [releases](https://github.com/YalKouassi/craft-bridges/releases) for `<id>-v`.

- `apps/<id>.toml`: one config per app, with `shared = true`. The keys are explained in
  [craft-bridge's README](https://github.com/YalKouassi/craft-bridge#bridgetoml).
- `.github/workflows/sync.yml`: runs every config every 3 hours with craft-bridge's `bridge.py`,
  using this repo's own token.
- `icons/`: icons for apps whose upstream has none the launcher can use.

The **Sync status** issue shows when each bridge last ran and what happened.

Until 2026-11-05 each app had its own `YalKouassi/<id>-for-unofficial-launcher` repo. Those are
archived, so launchers older than 0.11.0 can still read their last releases.

## Modes

- `publish` mirrors upstream's latest release if this repo doesn't have it yet.
- `compare` publishes nothing. It rebuilds each app's last release here and checks that its
  `SHA256SUMS.txt` is identical; for an app with no release yet, it dry-runs upstream's latest.

Scheduled runs use the `HUB_MODE` repository variable (`compare` if unset). Run the workflow by hand
to pick a mode, a few apps (`apps: mailcraft notecraft`), a tag, or `force`.

## Adding an app

1. Check [IGNORED.md](IGNORED.md), which lists apps left out and why.
2. Check that upstream ships something the launcher can install: an `.msi` or `-portable.zip` on
   Windows whose `<id>.exe` has a ProductVersion equal to the tag (or `former_ids` naming the exe),
   and AppImage, `.deb`, `.rpm`, tarball or `.dmg` elsewhere. A `Setup.exe` can't be installed.
3. Add `apps/<id>.toml` with `repo = "YalKouassi/craft-bridges"` and `shared = true`, then run the
   workflow in `compare` mode for that app (it dry-runs).
4. Run it in `publish` mode, and add `{"repo": "YalKouassi/craft-bridges", "app": "<id>"}` to the
   launcher's `index/apps.json`.

App authors who can publish releases themselves should follow
[JOINING.md](https://github.com/YalKouassi/craft-bridge/blob/main/JOINING.md) instead.

## Licence

MIT or Apache-2.0, at your option.
