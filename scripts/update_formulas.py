#!/usr/bin/env python3
"""Update Homebrew formula files with new versions from PyPI."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests


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


def get_tarball_info(package_name: str, version: str | None = None) -> tuple[str, str] | None:
    """Get tarball URL and SHA256 for a package from PyPI."""
    if version:
        url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    else:
        url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Warning: Failed to fetch PyPI info for {package_name}: {e}", file=sys.stderr)
        return None

    for url_info in data["urls"]:
        if url_info["packagetype"] == "sdist" and url_info["filename"].endswith(".tar.gz"):
            return url_info["url"], url_info["digests"]["sha256"]

    return None


def get_package_dependencies(package_name: str, version: str) -> list[str]:
    """Get package dependencies by installing in a temp venv and checking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        venv_path = Path(tmpdir) / "venv"

        # Create venv
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Warning: Failed to create venv: {result.stderr}", file=sys.stderr)
            return []

        pip_path = venv_path / "bin" / "pip"

        # Install the package
        result = subprocess.run(
            [str(pip_path), "install", f"{package_name}=={version}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Warning: Failed to install {package_name}: {result.stderr}", file=sys.stderr)
            return []

        # Get list of installed packages (excluding the main package and pip/setuptools)
        result = subprocess.run(
            [str(pip_path), "freeze"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []

        deps = []
        skip_packages = {"pip", "setuptools", "wheel", package_name.lower().replace("-", "_")}

        for line in result.stdout.strip().split("\n"):
            if "==" in line:
                dep_name, dep_version = line.split("==")
                dep_name_normalized = dep_name.lower().replace("-", "_")
                if dep_name_normalized not in skip_packages:
                    deps.append((dep_name, dep_version))

        return deps


def generate_resource_block(package_name: str, version: str) -> str | None:
    """Generate a Homebrew resource block for a package."""
    tarball_info = get_tarball_info(package_name, version)
    if not tarball_info:
        return None

    url, sha256 = tarball_info

    # Normalize name for resource block (use hyphen style)
    resource_name = package_name.lower().replace("_", "-")

    return f'''  resource "{resource_name}" do
    url "{url}"
    sha256 "{sha256}"
  end'''


def update_formula(
    formula_path: Path,
    new_version: str,
    tarball_url: str,
    sha256: str,
    update_resources: bool = True,
) -> bool:
    """Update a formula file with new version and optionally update resources."""
    content = formula_path.read_text()

    # Extract package name from URL for dependency resolution
    pypi_match = re.search(r"/([a-zA-Z0-9_-]+)-[\d.]+\.tar\.gz$", tarball_url)
    if not pypi_match:
        print(f"Warning: Could not extract package name from URL", file=sys.stderr)
        return False
    package_name = pypi_match.group(1)

    # Update main URL
    content = re.sub(
        r'(url\s+"https://files\.pythonhosted\.org/packages/)[^"]+(")',
        rf'\g<1>{tarball_url.split("packages/")[1]}\2',
        content,
    )

    # If URL format is different, try a more general approach
    if tarball_url not in content:
        content = re.sub(
            r'(url\s+")[^"]+(\.tar\.gz")',
            rf'\g<1>{tarball_url}\2',
            content,
        )

    # Update sha256
    # Find the sha256 that comes right after the main url (not in resource blocks)
    lines = content.split("\n")
    new_lines = []
    in_main_section = True
    url_found = False

    for i, line in enumerate(lines):
        if "url " in line and "resource" not in lines[max(0, i - 1) : i]:
            url_found = True
            new_lines.append(f'  url "{tarball_url}"')
            continue

        if url_found and "sha256" in line and in_main_section:
            new_lines.append(f'  sha256 "{sha256}"')
            url_found = False
            in_main_section = False
            continue

        if "resource " in line:
            in_main_section = False

        new_lines.append(line)

    content = "\n".join(new_lines)

    # Update resources if requested
    if update_resources:
        print(f"  Fetching dependencies for {package_name}=={new_version}...", file=sys.stderr)
        deps = get_package_dependencies(package_name, new_version)

        if deps:
            # Remove old resource blocks
            content = re.sub(
                r'\n  resource "[^"]+" do\n    url "[^"]+"\n    sha256 "[^"]+"\n  end',
                "",
                content,
            )

            # Generate new resource blocks
            resource_blocks = []
            for dep_name, dep_version in sorted(deps, key=lambda x: x[0].lower()):
                print(f"    Adding resource: {dep_name}=={dep_version}", file=sys.stderr)
                block = generate_resource_block(dep_name, dep_version)
                if block:
                    resource_blocks.append(block)

            # Insert resources before "def install"
            resources_text = "\n\n".join(resource_blocks)
            content = re.sub(
                r"(\n  def install)",
                f"\n\n{resources_text}\n\\1",
                content,
            )

    formula_path.write_text(content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Update formula files")
    parser.add_argument("--updates-file", required=True, help="JSON file with updates")
    parser.add_argument(
        "--no-resources",
        action="store_true",
        help="Don't update resource blocks",
    )
    args = parser.parse_args()

    updates_path = Path(args.updates_file)
    if not updates_path.exists():
        print(f"Error: Updates file '{updates_path}' not found", file=sys.stderr)
        return 1

    updates = json.loads(updates_path.read_text())

    if not updates:
        print("No updates to process", file=sys.stderr)
        return 0

    for update in updates:
        formula_path = Path(update["file_path"])
        print(f"\nUpdating {update['formula']}...", file=sys.stderr)
        print(f"  {update['current_version']} -> {update['latest_version']}", file=sys.stderr)

        success = update_formula(
            formula_path=formula_path,
            new_version=update["latest_version"],
            tarball_url=update["tarball_url"],
            sha256=update["sha256"],
            update_resources=not args.no_resources,
        )

        if success:
            print(f"  Updated successfully", file=sys.stderr)
        else:
            print(f"  Failed to update", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
