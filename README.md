# Python Ankara Topluluğu Tap (Third-Party Repositories)

## How do I install these formulae?

`brew install python-ankara-toplulugu/tap/<formula>`

Or `brew tap python-ankara-toplulugu/tap` and then `brew install <formula>`.

Or, in a `brew bundle` `Brewfile`:

```ruby
tap "python-ankara-toplulugu/tap"
brew "<formula>"
```

## Automated Formula Updates

This tap uses two complementary workflows to keep formulas up-to-date:

### Scheduled Updates (`update-formulas.yml`)

A "pull" model that periodically checks for new versions.

- **Runs:** Weekly on Mondays at 9:00 UTC, or manually via GitHub Actions
- **How it works:**
  1. Lists all formulas in `Formula/`
  2. Runs `brew livecheck` on each to check PyPI for newer versions
  3. Updates version/sha256 with `brew bump-formula-pr`
  4. Updates Python dependencies with `brew update-python-resources`
  5. Creates a single PR with all updates

### Event-Driven Updates (`update-formula-dispatch.yml`)

A "push" model where package repos notify the tap immediately after publishing.

- **Runs:** When a package repo sends a `repository_dispatch` event
- **How it works:**
  1. Receives payload with `formula` name and optionally `version`
  2. Validates the formula exists
  3. Updates the formula and creates a PR

#### Triggering from Package Repos

Package repos can trigger immediate formula updates after PyPI publish.

<details>
<summary><strong>For Humans</strong></summary>

##### Option A: Let an LLM do it

Copy and paste this prompt into your AI coding assistant:

> Set up automatic Homebrew formula updates for this repository.
> Follow the instructions at: https://github.com/python-ankara-toplulugu/homebrew-tap#triggering-from-package-repos

##### Option B: Manual Setup

1. Create a PAT with `repo` scope and write access to this repo
2. Add it as `HOMEBREW_TAP_TOKEN` secret in the package repo
3. Copy the workflow below to your package repo at `.github/workflows/update-homebrew-formula.yml`

```yaml
# Triggers Homebrew formula update after a release is published
name: Update Homebrew Formula
on:
  # Trigger after release is published
  release:
    types: [published]
  # Or trigger manually
  workflow_dispatch:
jobs:
  update-formula:
    name: Trigger formula update
    runs-on: ubuntu-latest
    # Only run if the release workflow (PyPI publish) succeeded
    # Uncomment if you want to wait for another workflow
    # needs: [publish]
    steps:
      - name: Trigger homebrew-tap update
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.HOMEBREW_TAP_TOKEN }}
          repository: python-ankara-toplulugu/homebrew-tap
          event-type: update-formula
          client-payload: |
            {
              "formula": "${{ github.event.repository.name }}",
              "version": "${{ github.event.release.tag_name }}"
            }
      - name: Summary
        run: |
          echo "Triggered Homebrew formula update for ${{ github.event.repository.name }}"
          echo "Version: ${{ github.event.release.tag_name }}"
          echo ""
          echo "Check the homebrew-tap repo for the PR:"
          echo "https://github.com/python-ankara-toplulugu/homebrew-tap/pulls"
```

</details>

<details>
<summary><strong>For LLM Agents</strong></summary>

**Prerequisites:**

- A GitHub PAT with `repo` scope stored as `HOMEBREW_TAP_TOKEN` in the repository secrets

**Instructions:**

1. Create `.github/workflows/update-homebrew-formula.yml` with this content:

```yaml
name: Update Homebrew Formula
on:
  release:
    types: [published]
  workflow_dispatch:
jobs:
  update-formula:
    name: Trigger formula update
    runs-on: ubuntu-latest
    steps:
      - name: Trigger homebrew-tap update
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.HOMEBREW_TAP_TOKEN }}
          repository: python-ankara-toplulugu/homebrew-tap
          event-type: update-formula
          client-payload: |
            {
              "formula": "${{ github.event.repository.name }}",
              "version": "${{ github.event.release.tag_name }}"
            }
      - name: Summary
        run: |
          echo "Triggered Homebrew formula update for ${{ github.event.repository.name }}"
          echo "Version: ${{ github.event.release.tag_name }}"
          echo ""
          echo "Check the homebrew-tap repo for the PR:"
          echo "https://github.com/python-ankara-toplulugu/homebrew-tap/pulls"
```

2. Verify the file exists and has correct YAML syntax

**Important:**

- `formula` in the payload should match the repository name (e.g., "ossin" for ossin repo)
- `version` is extracted from the release tag (e.g., "v1.0.0" or "1.0.0")
- The workflow triggers on `release: published` events

</details>

### Flow

```
[package repo]                  [homebrew-tap]
     │                               │
     │ Release published             │
     ▼                               │
  repository_dispatch ──────────────►│
  (formula, version)                 ▼
                           update-formula-dispatch.yml
                                     │
                                     ▼
                                Creates PR
```

## Documentation

`brew help`, `man brew` or check [Homebrew's documentation](https://docs.brew.sh).
