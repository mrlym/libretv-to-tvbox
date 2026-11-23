#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_SOURCE_URL = "https://gist.githubusercontent.com/yifanwang-yet/dbb7af044d90b5f51c1f32d0e0a200f6/raw/libretv-sources.json"


def fetch_json(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": "libretv-to-tvbox-sync/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def make_site_key(url: str, used_keys: set) -> str:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    host = re.sub(r"^(www|api|cj|caiji|zy)\.", "", host)
    parts = host.split(".")
    base = parts[0] if len(parts) >= 2 else host
    base = re.sub(r"[^a-z0-9_]+", "_", base).strip("_")
    if not base:
        base = "site_" + hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    key, suffix = base, 2
    while key in used_keys:
        key = f"{base}_{suffix}"
        suffix += 1
    used_keys.add(key)
    return key


def convert_sources(data: dict, include_adult: bool = False):
    name = str(data.get("name") or "LibreTV 订阅源").strip()
    used_keys = set()
    desktop_sites, standard_sites = [], []

    for item in data.get("sources") or []:
        if not isinstance(item, dict):
            continue
        if not include_adult and bool(item.get("isAdult")):
            continue
        site_name = str(item.get("name") or "").strip()
        api_url = str(item.get("url") or "").strip()
        if not site_name or not api_url:
            continue
        key = make_site_key(api_url, used_keys)
        desktop_sites.append({
            "key": key,
            "name": site_name,
            "type": "cms",
            "api": api_url,
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1,
        })
        standard_sites.append({
            "key": key,
            "name": site_name,
            "type": 3,
            "api": api_url,
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1,
        })

    lives = []
    for item in data.get("liveSources") or []:
        if not isinstance(item, dict):
            continue
        live_name = str(item.get("name") or "").strip()
        live_url = str(item.get("url") or "").strip()
        if live_name and live_url:
            lives.append({"name": live_name, "url": live_url})

    desktop_cfg = {
        "format": "tvbox-desktop/1",
        "name": name,
        "sites": desktop_sites,
        "lives": lives,
    }
    standard_cfg = {
        "sites": standard_sites,
        "lives": lives,
    }
    return desktop_cfg, standard_cfg


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-url", default=os.environ.get("SOURCE_URL", DEFAULT_SOURCE_URL))
    parser.add_argument("--desktop-out", type=Path, default=Path("tvbox-desktop.json"))
    parser.add_argument("--standard-out", type=Path, default=Path("tvbox.json"))
    parser.add_argument(
        "--include-adult",
        action="store_true",
        default=os.environ.get("INCLUDE_ADULT", "").lower() in ("1", "true", "yes"),
    )
    args = parser.parse_args()

    raw_data = fetch_json(args.source_url)
    desktop_cfg, standard_cfg = convert_sources(raw_data, include_adult=args.include_adult)
    if not desktop_cfg["sites"] and not desktop_cfg["lives"]:
        print("Error: converted config is empty.", file=sys.stderr)
        return 1

    args.desktop_out.write_text(json.dumps(desktop_cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.standard_out.write_text(json.dumps(standard_cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Converted {len(desktop_cfg['sites'])} sites and {len(desktop_cfg['lives'])} live sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
