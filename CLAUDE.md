# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Homebrew Tap** for Python Ankara Topluluğu (Python Ankara Community). It contains Ruby formula files that define how Homebrew installs third-party Python packages not available in the official Homebrew core.

## Common Commands

```bash
# Lint a formula for style and syntax issues
brew audit --strict --online Formula/<formula>.rb

# Test formula syntax only
brew test-bot --only-tap-syntax

# Install a formula locally for testing
brew install --build-from-source Formula/<formula>.rb

# Run formula tests
brew test <formula>

# Get dependency info for a Python package (useful when adding resources)
brew pip-audit <package>

# Uninstall a formula
brew uninstall <formula>
```

## Formula Structure

Formulas are Ruby classes in `Formula/`. For Python packages using virtualenv:

1. **Metadata**: `desc`, `homepage`, `url`, `sha256`, `license`
2. **Dependencies**: Use `depends_on "python@3.x"` for Python version
3. **Resources**: Each Python dependency needs a separate `resource` block with PyPI source URL and sha256
4. **Install**: Use `virtualenv_install_with_resources` for Python packages
5. **Test**: Define a basic smoke test in the `test do` block

## Adding a New Formula

1. Create `Formula/<name>.rb` following the existing pattern
2. Get source tarball URL from PyPI (prefer `.tar.gz` over wheels)
3. Calculate sha256: `curl -L <url> | shasum -a 256`
4. Add resource blocks for all Python dependencies (check `pip show <pkg>` or use `brew pip-audit`)
5. Run `brew audit --strict --online Formula/<name>.rb` to validate

## CI/CD Workflows

- **tests.yml**: Runs `brew test-bot` on push/PR across Ubuntu and macOS (Intel + ARM)
- **publish.yml**: Pulls bottles when PR has `pr-pull` label and pushes to main
- **update-formulas.yml**: Checks PyPI for formula updates weekly, creates PRs for outdated packages
- **update-formula-dispatch.yml**: Receives `repository_dispatch` events from package repos to trigger immediate updates

## Triggering Updates from Package Repos

Package repos can trigger immediate formula updates after PyPI publish using `repository_dispatch`. See `examples/update-homebrew-formula.yml` for a workflow template.

Setup:
1. Create a PAT with `repo` scope and write access to this repo
2. Add it as `HOMEBREW_TAP_TOKEN` secret in the package repo
3. Copy the example workflow to the package repo

## Update Scripts

Scripts in `scripts/` for automated formula updates:

```bash
# Check all formulas for available updates
python scripts/check_updates.py

# Check a specific formula
python scripts/check_updates.py --formula ossin

# Update formulas from a JSON updates file
python scripts/update_formulas.py --updates-file updates.json
```

These scripts query PyPI, compare versions, and can update formula files including all resource blocks (dependencies).
