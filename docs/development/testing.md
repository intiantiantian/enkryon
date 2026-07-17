# Local Development and Testing

This document defines the supported local setup and the checks that must
pass before Enkryon changes are committed.

## Verified Environment

The Phase 3 baseline was verified with:

- Windows 10
- Python 3.13.14
- pytest 9.1.1

Other compatible Python 3.13 versions may work, but Python 3.13.14 is the
verified development version.

## Dependency Files

- `requirements.txt` contains application runtime dependencies.
- `requirements-dev.txt` installs the runtime dependencies and
  development-only testing tools.
- `buildozer.spec` separately defines the dependencies packaged in the
  Android application.

Development tools must not be added to the Android Buildozer requirements.

## Create a Development Environment

From the project root in Windows Command Prompt:

```bat
py -3.13 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

When returning to the project later, activate the existing environment:

```bat
.venv\Scripts\activate
```

## Required Checks

Run the complete automated test suite:

```bat
python -m pytest -q
```

Compile the Python source files to detect syntax problems:

```bat
python -m compileall -q main.py database screens services theme utils widgets tests
```

Check the Git changes for whitespace errors:

```bat
git diff --check
```

Inspect the working tree:

```bat
git status --short
```

## Expected Results

A change is ready for checkpoint review when:

- Every automated test passes.
- The compilation command produces no errors.
- `git diff --check` produces no output.
- `git status --short` shows only the intended files.

The number of tests may increase as the project grows. Success depends on
all collected tests passing, not on preserving a fixed test count.

## Before Committing

1. Review every changed file.
2. Run all required checks.
3. Perform any real-application checks relevant to the change.
4. Commit only after the checkpoint has been reviewed and verified.
