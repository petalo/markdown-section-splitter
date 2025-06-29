# Scripts Directory

This directory contains utility scripts for project maintenance and distribution.

## Available Scripts

### `upload_commands.sh`
Automated PyPI upload script for publishing the package.

**Usage:**
```bash
./scripts/upload_commands.sh
```

**Features:**
- Checks and installs build tools
- Cleans previous builds
- Builds the package
- Uploads to TestPyPI first (safer)
- Tests installation from TestPyPI
- Uploads to production PyPI
- Tests production installation

**Prerequisites:**
- PyPI and TestPyPI accounts with API tokens
- Configured `~/.pypirc` file (see `.pypirc.example`)

**Safety Features:**
- Interactive prompts before each upload step
- Tests installation before proceeding
- Can be cancelled at any step with Ctrl+C