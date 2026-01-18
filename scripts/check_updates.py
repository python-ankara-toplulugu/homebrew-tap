#!/usr/bin/env python3
"""Check Homebrew formulas for available updates from PyPI."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

import requests
from packaging.version import Version


class FormulaInfo(NamedTuple):
    """Information extracted from a formula file."""

    name: str
    version: str
    pypi_name: str
    file_path: Path


class UpdateInfo(NamedTuple):
    """Information about an available update."""

    formula: str
    pypi_name: str
    current_version: str
    latest_version: str
    tarball_url: str
    sha256: str


def extract_formula_info(formula_path: Path) -> FormulaInfo | None:
    """Extract package info from a Homebrew formula file."""
    content = formula_path.read_text()

    # Extract class name (formula name)
    class_match = re.search(r"class\s+(\w+)\s+<\s+Formula", content)
    if not class_match:
        return None
    formula_name = class_match.group(1).lower()

    # Extract version from URL
    # Pattern: /packages/.../package-version.tar.gz or /package/version/...
    url_match = re.search(r'url\s+"([^"]+)"', content)
    if not url_match:
        return None
    url = url_match.group(1)

    # Try to extract package name and version from PyPI URL
    # Format: .../packagename-version.tar.gz
    pypi_match = re.search(r"/([a-zA-Z0-9_-]+)-(\d+\.\d+(?:\.\d+)?(?:\.\w+)?)\.tar\.gz$", url)
    if pypi_match:
        pypi_name = pypi_match.group(1).replace("_", "-").lower()
        version = pypi_match.group(2)
    else:
        # Fallback: use formula name
        pypi_name = formula_name
        version_match = re.search(r'version\s+"([^"]+)"', content)
        if version_match:
            version = version_match.group(1)
        else:
            return None

    return FormulaInfo(
        name=formula_name,
        version=version,
        pypi_name=pypi_name,
        file_path=formula_path,
    )


def get_pypi_info(package_name: str) -> dict | None:
    """Fetch package info from PyPI API."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Warning: Failed to fetch PyPI info for {package_name}: {e}", file=sys.stderr)
        return None


def get_tarball_sha256(url: str) -> str | None:
    """Download tarball and calculate SHA256."""
    try:
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        sha256_hash = hashlib.sha256()
        for chunk in response.iter_content(chunk_size=8192):
            sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except requests.RequestException as e:
        print(f"Warning: Failed to download {url}: {e}", file=sys.stderr)
        return None


def check_formula_update(formula_info: FormulaInfo) -> UpdateInfo | None:
    """Check if a formula has an update available."""
    pypi_info = get_pypi_info(formula_info.pypi_name)
    if not pypi_info:
        return None

    latest_version = pypi_info["info"]["version"]

    try:
        current = Version(formula_info.version)
        latest = Version(latest_version)
        if latest <= current:
            return None
    except Exception:
        # If version parsing fails, do string comparison
        if latest_version == formula_info.version:
            return None

    # Find source tarball URL
    tarball_url = None
    for url_info in pypi_info["urls"]:
        if url_info["packagetype"] == "sdist" and url_info["filename"].endswith(".tar.gz"):
            tarball_url = url_info["url"]
            sha256 = url_info["digests"]["sha256"]
            break

    if not tarball_url:
        print(f"Warning: No source tarball found for {formula_info.pypi_name}", file=sys.stderr)
        return None

    return UpdateInfo(
        formula=formula_info.name,
        pypi_name=formula_info.pypi_name,
        current_version=formula_info.version,
        latest_version=latest_version,
        tarball_url=tarball_url,
        sha256=sha256,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check formulas for updates")
    parser.add_argument("--formula", help="Specific formula to check")
    parser.add_argument("--output-json", help="Output results to JSON file")
    parser.add_argument(
        "--formula-dir",
        default="Formula",
        help="Directory containing formula files",
    )
    args = parser.parse_args()

    formula_dir = Path(args.formula_dir)
    if not formula_dir.exists():
        print(f"Error: Formula directory '{formula_dir}' not found", file=sys.stderr)
        return 1

    # Find formula files
    if args.formula:
        formula_files = [formula_dir / f"{args.formula}.rb"]
        if not formula_files[0].exists():
            print(f"Error: Formula '{args.formula}' not found", file=sys.stderr)
            return 1
    else:
        formula_files = list(formula_dir.glob("*.rb"))

    updates: list[dict] = []

    for formula_file in formula_files:
        print(f"Checking {formula_file.stem}...", file=sys.stderr)

        formula_info = extract_formula_info(formula_file)
        if not formula_info:
            print(f"  Warning: Could not parse formula", file=sys.stderr)
            continue

        print(f"  Current: {formula_info.version}", file=sys.stderr)

        update = check_formula_update(formula_info)
        if update:
            print(f"  Update available: {update.latest_version}", file=sys.stderr)
            updates.append({
                "formula": update.formula,
                "pypi_name": update.pypi_name,
                "current_version": update.current_version,
                "latest_version": update.latest_version,
                "tarball_url": update.tarball_url,
                "sha256": update.sha256,
                "file_path": str(formula_file),
            })
        else:
            print(f"  Up to date", file=sys.stderr)

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(updates, indent=2))
        print(f"\nWrote {len(updates)} update(s) to {args.output_json}", file=sys.stderr)

    # Also print to stdout for convenience
    if updates:
        print(json.dumps(updates, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
