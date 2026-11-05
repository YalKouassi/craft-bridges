# craft-bridges

Every bridge for [Craft Unofficial Launcher](https://github.com/YalKouassi/craft-unofficial-launcher)
in one repo. A bridge mirrors an upstream app's releases into a
`YalKouassi/<id>-for-unofficial-launcher` repo, renamed to the launcher's contract and with a
`craft-app.json` added, so the launcher can install and update the app. The bridges are
unofficial and are not affiliated with or endorsed by the apps' authors or by ArtCraft.

- `apps/<id>.toml`: one config per app. The keys are explained in
  [craft-bridge's README](https://github.com/YalKouassi/craft-bridge#bridgetoml).
- `.github/workflows/sync.yml`: runs every config every 3 hours with craft-bridge's `bridge.py`.
- `icons/`: icons for apps whose upstream has none the launcher can use.

Each `*-for-unofficial-launcher` repo now only hosts its releases. The launcher's index keeps
pointing at those repos, so nothing changes for users.

The **Sync status** issue shows when each bridge last ran and what happened.

## Modes

- `publish` mirrors upstream's latest release if the bridge repo doesn't have it yet. It needs the
  `BRIDGES_TOKEN` secret: a fine-grained token with **Contents: read and write** on the
  `*-for-unofficial-launcher` repos (this repo's own `GITHUB_TOKEN` can't write to other repos).
- `token-check` creates and deletes a draft release in each bridge repo, to prove `BRIDGES_TOKEN`
  can write to it. Publishes nothing.
- `compare` publishes nothing. It rebuilds the release each bridge repo published last and checks
  that its `SHA256SUMS.txt` is identical; for an app with no release yet, it dry-runs upstream's
  latest.

Scheduled runs use the `HUB_MODE` repository variable (`compare` if unset). Run the workflow by hand
to pick a mode, a few apps (`apps: mailcraft notecraft`), a tag, or `force`.

## Adding an app

1. Check that upstream ships something the launcher can install: an `.msi` or `-portable.zip` on
   Windows whose `<id>.exe` has a ProductVersion equal to the tag (or `former_ids` naming the exe),
   and AppImage, `.deb`, `.rpm`, tarball or `.dmg` elsewhere. A `Setup.exe` can't be installed.
2. Create the empty public repo `YalKouassi/<id>-for-unofficial-launcher` and add it to the
   `BRIDGES_TOKEN` token's repositories.
3. Add `apps/<id>.toml`, then run the workflow in `compare` mode for that app (it dry-runs).
4. Run it in `publish` mode, and add the repo to the launcher's `index/apps.json`.

Apps left out, and why, are listed in [IGNORED.md](IGNORED.md).

App authors who can publish releases themselves should follow
[JOINING.md](https://github.com/YalKouassi/craft-bridge/blob/main/JOINING.md) instead.

## Licence

MIT or Apache-2.0, at your option.
