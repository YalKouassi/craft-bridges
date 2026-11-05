"""Checks every bridge against its upstream without downloading anything.

    python -I tools/health.py [APPS_DIR]      (default: this repo's apps/)

For each `<id>.toml` in APPS_DIR it:
  - checks the upstream repo hasn't moved or disappeared;
  - plans upstream's latest release with the bridge's rename and skip rules (the same planning
    bridge.py does), so renamed assets show up before the scheduled run fails on them;
  - says whether the bridge already mirrors that release.

Set GITHUB_TOKEN (or GH_TOKEN), e.g. GITHUB_TOKEN=$(gh auth token): a dozen bridges use more
API calls than the unauthenticated limit allows. Exit status: 0 if every bridge is OK or only
behind, 1 otherwise.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bridge as b  # noqa: E402


def check(cfg_path: Path, token: str | None) -> tuple[str, str]:
    """(status, detail): status is OK, BEHIND, WARN or FAIL."""
    try:
        cfg = b.load_config(cfg_path)
        b.check_upstream_home(cfg, token)
        rel = b.fetch_json(f"/repos/{cfg.upstream}/releases/latest", token)
        if rel is None:
            return "OK", "upstream has no published release yet"
        tag = rel["tag_name"]
        d = b.build_descriptor(cfg)
        planned, _, warnings = b.plan_release(cfg, [a["name"] for a in rel.get("assets", [])], d["id"], b.version_of(tag))
        if b.upstream_adopted(cfg, rel, token):
            return "WARN", f"upstream {tag} attaches its own valid craft-app.json; retire this bridge"
        state = b.bridge_release_state(cfg.repo, cfg.bridge_tag(tag), token)
        detail = f"{cfg.upstream} {tag}: {len(planned)} package(s) planned"
        if warnings:
            return "WARN", detail + "; " + "; ".join(warnings)
        if state != "published":
            return "BEHIND", detail + f"; the bridge doesn't have {tag} yet ({state})"
        return "OK", detail
    except (b.ConfigError, b.BridgeError, b.NetError) as e:
        return "FAIL", str(e)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "apps"
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None
    if not token:
        print("note: no GITHUB_TOKEN; the API rate limit may cut this short", file=sys.stderr)
    configs = sorted(root.glob("*.toml"))
    if not configs:
        print(f"no bridge configs in {root}")
        return 1
    bad = 0
    width = max(len(c.stem) for c in configs)
    for c in configs:
        status, detail = check(c, token)
        name = c.stem
        print(f"{status:<6} {name:<{width}}  {detail}", flush=True)
        bad += status in ("WARN", "FAIL")
    print(f"\n{len(configs)} bridge(s), {bad} needing attention")
    return 1 if bad else 0


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
