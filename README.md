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

- `apps/<id>.toml`: one config per app (keys [below](#appsidtoml)).
- `bridge.py`: the tool that mirrors a release (Python 3.11+, standard library only), with
  `tests/` and `tools/`.
- `.github/workflows/sync.yml`: checks every config every 15 minutes (only apps with a new
  upstream release get a job) with this repo's own token, and
  keeps `latest.json` (each app's newest tag) up to date. The launcher reads that file when
  GitHub's API refuses it.
- [JOINING.md](JOINING.md): how app authors make their own releases follow the contract, so they
  need no bridge.
- `icons/`: icons for apps whose upstream has none the launcher can use.

The **Sync status** issue shows when each bridge last ran and what happened.

## Modes

- `publish` mirrors upstream's latest release if this repo doesn't have it yet.
- `compare` publishes nothing. It rebuilds each app's last release here and checks that its
  `SHA256SUMS.txt` is identical; for an app with no release yet, it dry-runs upstream's latest.

Scheduled runs use the `HUB_MODE` repository variable (`compare` if unset). Run the workflow by hand
to pick a mode, a few apps (`apps: mailcraft notecraft`), a tag, or `force`.

## Adding an app

1. Check [IGNORED.md](IGNORED.md), which lists apps left out and why.
2. Check that upstream ships something the launcher can install: an `.msi` or `-portable.zip` on
   Windows, and AppImage, `.deb`, `.rpm`, tarball or `.dmg` elsewhere. A `Setup.exe` can't be
   installed. A portable zip's exe should have a ProductVersion equal to the tag. One with no
   version resource installs from launcher 0.12 on but is rolled back by older launchers, so prefer
   upstream's `.msi` when it has one.
3. Add `apps/<id>.toml` with `repo = "YalKouassi/craft-bridges"` and `shared = true`, then run the
   workflow in `compare` mode for that app (it dry-runs).
4. Run it in `publish` mode, and add `{"repo": "YalKouassi/craft-bridges", "app": "<id>"}` to the
   launcher's `index/apps.json`.

App authors who can publish releases themselves should follow
[JOINING.md](JOINING.md) instead.

GitHub disables scheduled workflows in a public repo after 60 days without commits; re-enable
it from the Actions tab if that happens.

## Trust

Installing an app through a bridge means trusting **the bridge's maintainer** as well as the
upstream project: the launcher checks these releases against their own
`SHA256SUMS.txt`, which the bridge writes.

What a bridge does, and doesn't do, to keep that trust small:

- **It never builds anything.** Every package is a file upstream published on its own GitHub
  release, downloaded from `github.com/<upstream>/releases/download/...` only.
- **It verifies before mirroring.** Each download must match the size and SHA-256 digest GitHub
  reports for the upstream asset and, when upstream publishes a checksum file
  (`upstream_sums`), the checksum listed there. Any mismatch aborts the run and nothing is
  published.
- **It never changes a program file.** Packages are renamed. An archive (a portable `.zip` or a
  `.tar.gz`) is **repacked** only when its folder layout would stop the launcher installing it
  (for example, the executable sitting two folders deep). Repacking moves entries between folders
  and recompresses them; the bytes of every file inside are copied unchanged, and nothing is
  dropped (`bridge.py` refuses to repack if a file would be lost). Each release's notes list every
  file, the upstream asset it came from, its SHA-256, and whether it was repacked.
- **Installers stay upstream's.** MSI, DMG, AppImage, deb, rpm and Flatpak files are never
  opened, only renamed.
- **Everything downloaded is treated as untrusted data.** Archives are only listed or copied
  entry by entry (never extracted to disk, never run), with size and entry-count caps, and
  entries with absolute paths, `..`, or links that escape the archive are refused.
- **Upstream's licences travel with the builds.** Every release attaches upstream's `LICENSE*`
  and `NOTICE*` files from the same tag, and the run fails if upstream has no licence file.

To audit a bridge release, compare the hashes in its notes or `SHA256SUMS.txt` with upstream's
release (the "Upstream asset" column names the file).

## When upstream adopts the contract

If an upstream release ever attaches its own valid `craft-app.json` (one whose `repo` is the
upstream repo), the bridge has done its job. `bridge.py` then **publishes nothing**, prints

```text
NOTICE: <upstream> now follows the procedure (...); point the index at https://github.com/<upstream> and retire this bridge.
```

and exits 0. The launcher index should then list the upstream repo instead, and `apps/<id>.toml` can be
removed. (An upstream `craft-app.json` that isn't valid is reported as a
warning, and the bridge keeps mirroring.)

## When upstream changes

- **The repo moves** (transferred or renamed). GitHub keeps redirecting the old name, but
  `bridge.py` stops with `<old> has moved to <new>; check the new owner, then set upstream = ...`.
  It doesn't follow the move on its own, because a new owner is a new party to trust.
- **The assets are renamed.** If no rename rule matches any upstream asset, the run fails and
  lists the unmatched names. If some still match, any unmatched asset that looks like a package
  (`.zip`, `.msi`, `.dmg`, `.AppImage`, `.deb`, `.rpm`, `.flatpak`, `.tar.gz`, ...) is reported as
  a warning, so new builds aren't dropped without anyone noticing.

When a run fails, the **Sync status** issue shows the error.

To check every bridge at once without downloading anything (upstream location, rule coverage of
the latest release, and whether the bridge has it yet):

```sh
GITHUB_TOKEN=$(gh auth token) python -I tools/health.py
```

## `apps/<id>.toml`

```toml
[bridge]
upstream = "opengeos/RustGIS"                          # the project being mirrored
repo = "YalKouassi/craft-bridges"                      # where the releases are published
shared = true                                          # tags <id>-v<version>; see below
upstream_sums = ["SHA256SUMS"]   # upstream checksum files to verify downloads against (optional)
skip = ['\.whl$', '-setup\.exe$']  # regexes (searched) for upstream assets not to mirror
# licenses = ["LICENSE"]         # default "auto": every LICENSE*/COPYING*/NOTICE* at the repo root
# strict = true                  # fail when an upstream asset matches no rule (default: skip it)
# max_asset_mb = 1024            # per-asset download cap
# notes_chars = 4000             # how much of upstream's release notes to quote

[descriptor]          # craft-app.json; schema, repo, upstream and icon are filled in
id = "rustgis"
name = "RustGIS"
tagline = "A fast, free and open-source GIS in pure Rust"
publisher = "Open Geospatial Solutions"
bundle_id = "org.rustgis.RustGIS"
msi_publisher = "Open Geospatial Solutions"   # only when the release ships an .msi
# apple_team = "..."                          # only if you can prove upstream's Developer ID team
website = "https://rustgis.app"
color = "#d36736"
# former_ids / former_names / former_bundles as in the spec

[icon]                # a PNG of at most 512 px a side and 256 KB, saved as <id>.png
url = "https://raw.githubusercontent.com/{upstream}/{tag}/path/icon-256.png"
# or take it from inside a mirrored upstream archive:
# archive = 'RustGIS-{version}-linux-x86_64\.tar\.gz'
# member = 'RustGIS-{version}-linux-x86_64/rustgis\.png'

[[rename]]            # first rule whose regex matches the whole asset name wins
match = 'RustGIS-(?P<version>[0-9][^-]*)-windows-x86_64-portable\.zip'
to = '{id}-{version}-windows-x64-portable.zip'
# repack = "auto"     # auto: only if the launcher couldn't install it; "always"; "never"
# exe = "My App.exe"  # portable zips only: upstream's executable, renamed to <id>.exe when repacked

[[rename]]
match = 'rustgis_(?P<version>[^_]+)_(?P<arch>amd64|arm64)\.deb'
to = '{id}-{version}-linux-{arch}.deb'
map = { arch = { amd64 = "x86_64", arm64 = "aarch64" } }
```

In `to`, `{id}` and `{version}` (the tag without its leading `v`) are always available, along with
every named group of `match`, after `map`. If `match` captures `version` and it differs from the
tag's version, the asset is skipped. `tools/icon.py` (needs Pillow) shrinks an icon that's too
big.

With `shared = true`, upstream's `v1.2.3` is published as `<id>-v1.2.3`, the repo's "latest
release" marker is never moved, and the release is checked as the launcher's `owner/name#<id>`
source (the launcher's spec, section 6).

## `bridge.py`

Python 3.11 or newer, standard library only.

```text
python -I bridge.py [--config bridge.toml] [--out dist] [--dry-run] [--force] [--tag TAG] [--backfill N]
python -I bridge.py --check DIR --tag TAG [--repo OWNER/NAME]
python -I bridge.py --sums DIR
```

- With no flags, it mirrors upstream's latest release (not drafts or prereleases), and exits 0
  without doing anything if this repo already has that release.
- `--dry-run` builds and checks into `--out/<tag>` and publishes nothing.
- `--force` rebuilds and replaces an existing bridge release.
- `--tag` mirrors a specific upstream tag.
- `--backfill N` also mirrors up to N older upstream releases the bridge lacks; only the newest
  is marked as the bridge's latest release.
- `--check` validates a folder as a release of this bridge; with `--repo OWNER/NAME` it validates
  it as a release of any repo and needs no `bridge.toml` (this is how app authors check theirs).
- `--sums DIR` writes `DIR/SHA256SUMS.txt` for every file in the folder.

Exit codes: `0` done or nothing to do, `1` the release couldn't be built or breaks the contract,
`2` a config, argument or network problem. `GITHUB_TOKEN` (or `GH_TOKEN`) is sent to
`api.github.com` only, never to download hosts, and is passed to `gh` for publishing.

Before publishing, `bridge.py` checks the folder with a Python port of the launcher's
`crates/descriptor` rules (the descriptor's fields, the reserved ArtCraft namespace, package
names and platform tokens, version against the tag, `SHA256SUMS.txt` completeness and every
checksum, `msi_publisher` when there's an MSI, and the icon's PNG header and size) plus the
launcher's install rules for portable zips and tarballs. If the two ever disagree, the launcher's
Rust code wins; run `craft-release-check` to be sure. It publishes through `gh release create` as
a draft first, uploads everything, and then makes the release public, so an interrupted run never
leaves a half-uploaded public release.

Tests: `python -I -m unittest discover -s tests`.

## Licence

MIT or Apache-2.0, at your option. This covers this repo's own files only; mirrored apps keep
their upstream licences.
