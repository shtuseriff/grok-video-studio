#!/usr/bin/env python3
"""Inspect all session folders, verify local video files, download missing ones."""

import json
import sys
import urllib.request
from pathlib import Path

SESSIONS_DIR = Path(__file__).parent / "sessions"


def verify_session(session_dir: Path) -> dict:
    """Check a single session for missing local video files."""
    json_path = list(session_dir.glob("*_session.json"))
    if not json_path:
        return {"session_id": session_dir.name, "error": "No session JSON found"}

    with open(json_path[0]) as f:
        data = json.load(f)

    session_id = data.get("session_id", session_dir.name)
    outputs = data.get("outputs", [])
    results = {
        "session_id": session_id,
        "total_outputs": len(outputs),
        "missing": [],
        "duplicate_paths": [],
        "downloaded": [],
        "errors": [],
    }

    # Detect duplicate local paths (parallel gen bug)
    seen_paths = {}
    for i, out in enumerate(outputs):
        p = out.get("path", "")
        if p in seen_paths:
            results["duplicate_paths"].append(
                f"outputs[{seen_paths[p]}] and outputs[{i}] both use '{p}'"
            )
        seen_paths[p] = i

    for i, out in enumerate(outputs):
        local_path = session_dir / out.get("path", "")
        remote_url = out.get("url", "")
        out_type = out.get("type", "unknown")
        status = out.get("status", "ok")

        if not local_path.name:
            continue

        if local_path.exists() and local_path.stat().st_size > 0:
            continue

        # File is missing or empty
        results["missing"].append({
            "index": i,
            "path": str(local_path.name),
            "type": out_type,
            "status": status,
            "url": remote_url,
        })

    return results


def download_missing(session_dir: Path, missing_list: list, dry_run: bool = False) -> list:
    """Download missing files from their remote URLs."""
    downloaded = []
    for item in missing_list:
        url = item["url"]
        local_path = session_dir / item["path"]

        if not url:
            print(f"  ⚠ No remote URL for {item['path']} — cannot recover")
            continue

        if dry_run:
            print(f"  [DRY RUN] Would download {item['path']} from {url[:80]}...")
            downloaded.append(item["path"])
            continue

        print(f"  ⬇ Downloading {item['path']}...")
        try:
            urllib.request.urlretrieve(url, local_path)
            size = local_path.stat().st_size
            print(f"    ✓ Saved ({size:,} bytes)")
            downloaded.append(item["path"])
        except Exception as exc:
            print(f"    ✗ Failed: {exc}")

    return downloaded


def main():
    dry_run = "--dry-run" in sys.argv
    fix = "--fix" in sys.argv or not dry_run

    if not SESSIONS_DIR.exists():
        print(f"Sessions directory not found: {SESSIONS_DIR}")
        sys.exit(1)

    session_dirs = sorted(
        [d for d in SESSIONS_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    )

    print(f"Scanning {len(session_dirs)} sessions in {SESSIONS_DIR}\n")

    total_missing = 0
    total_duplicates = 0
    total_downloaded = 0

    for session_dir in session_dirs:
        result = verify_session(session_dir)

        if result.get("error"):
            print(f"[{result['session_id']}] ERROR: {result['error']}")
            continue

        missing = result["missing"]
        dupes = result["duplicate_paths"]
        n_outputs = result["total_outputs"]

        if not missing and not dupes:
            continue

        print(f"[{result['session_id']}] {n_outputs} outputs")

        if dupes:
            total_duplicates += len(dupes)
            for d in dupes:
                print(f"  ⚠ DUPLICATE PATH: {d}")

        if missing:
            total_missing += len(missing)
            for m in missing:
                status_tag = f" ({m['status']})" if m["status"] != "ok" else ""
                print(f"  ✗ MISSING: {m['path']} [{m['type']}{status_tag}]")

            if fix:
                downloaded = download_missing(session_dir, missing, dry_run=dry_run)
                total_downloaded += len(downloaded)

    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Sessions scanned:  {len(session_dirs)}")
    print(f"  Duplicate paths:   {total_duplicates}")
    print(f"  Missing files:     {total_missing}")
    print(f"  Downloaded:        {total_downloaded}")

    if total_missing > 0 and dry_run:
        print(f"\nRun without --dry-run to download missing files.")


if __name__ == "__main__":
    main()
