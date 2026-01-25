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

# Uninstall a formula
brew uninstall <formula>

# Check for available updates (requires livecheck block in formula)
brew livecheck <formula>

# Update a formula to a new version
brew bump-formula-pr --version=<version> <formula>

# Update Python resource blocks automatically
brew update-python-resources <formula>
```

## Formula Structure

Formulas are Ruby classes in `Formula/`. For Python packages using virtualenv:

1. **Metadata**: `desc`, `homepage`, `url`, `sha256`, `license`
2. **Livecheck**: Add a `livecheck do` block with `strategy :pypi` for automatic version checking
3. **Dependencies**: Use `depends_on "python@3.x"` for Python version
4. **Resources**: Each Python dependency needs a separate `resource` block with PyPI source URL and sha256
5. **Install**: Use `virtualenv_install_with_resources` for Python packages
6. **Test**: Define a basic smoke test in the `test do` block

## Adding a New Formula

1. Create `Formula/<name>.rb` following the existing pattern
2. Get source tarball URL from PyPI (prefer `.tar.gz` over wheels)
3. Calculate sha256: `curl -L <url> | shasum -a 256`
4. Add a `livecheck do` block with `strategy :pypi` for automatic update detection
5. Add resource blocks for all Python dependencies using `brew update-python-resources`
6. Run `brew audit --strict --online Formula/<name>.rb` to validate

## CI/CD Workflows

- **tests.yml**: Runs `brew test-bot` on push/PR across Ubuntu and macOS (Intel + ARM)
- **publish.yml**: Pulls bottles when PR has `pr-pull` label and pushes to main
- **update-formulas.yml**: Uses `brew livecheck` to check for updates weekly, creates PRs using `brew bump-formula-pr` and `brew update-python-resources`
- **update-formula-dispatch.yml**: Receives `repository_dispatch` events from package repos to trigger immediate updates

## Triggering Updates from Package Repos

Package repos can trigger immediate formula updates after PyPI publish using `repository_dispatch`. See the "Triggering from Package Repos" section in README.md for the workflow template and setup instructions.
