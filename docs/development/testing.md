# Local Development and Testing

This document defines the supported local setup and the checks that must
pass before Enkryon changes are committed.

## Verified Environment

The Phase 3 baseline was verified with:

- Windows 10
- Python 3.13.14
- pytest 9.1.1
- pytest-cov 7.1.0

Other compatible Python 3.13 versions may work, but Python 3.13.14 is the
verified development and continuous-integration version.

## Dependency Files

- `requirements.txt` contains application runtime dependencies.
- `requirements-dev.txt` installs runtime dependencies and pinned
  development-only testing tools.
- `buildozer.spec` separately defines dependencies packaged in the Android
  application.

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

## Required Local Checks

Run the complete test suite with branch coverage:

```bat
python -m pytest -q --cov --cov-report=term-missing
```

Compile the Python source files to detect syntax problems:

```bat
python -m compileall -q main.py database screens services theme utils widgets tests
```

Check Git changes for whitespace errors:

```bat
git diff --check
```

Inspect the working tree:

```bat
git status --short
```

## Coverage Baseline

The initial Phase 3 application-wide baseline is `51%` branch coverage.

The strongest coverage is concentrated in the highest-risk core areas:

- Database migrations
- Transaction repositories and totals
- Exact money conversion and formatting
- Transaction validation and payload creation
- Transaction services

Screen and interactive-widget coverage remains lower because importing a
Kivy interface is not the same as exercising its behavior. The current
headless smoke test verifies that the application entry point and all six
screen modules can import successfully.

The baseline is informational. Phase 3 does not impose an arbitrary
percentage gate; new tests should target meaningful financial, migration,
service, and failure behavior.

## Phase 6 Interface Regression

Phase 6 began with `252` tests. Its implementation regression contained
`391` passing tests, and the documentation closeout adds four tests for a
final total of `395` passing tests.

Automated coverage now includes source-level responsive-layout contracts,
transaction-form preservation, actionable empty states, shared overlay
behavior, option selection, floating-label boundaries, Dashboard amount
capacity, and overlay-first Back handling Back handling.

Real rendering still requires application checks. Relevant Phase 6
checkpoints used these conditions:

- Small `S / 90%` profile.
- One medium or desktop profile.
- Default and enlarged system font.
- Empty, populated, validation-error, destructive, and long-content states.
- Android checks for keyboard, safe-area, and Back behavior.
- Desktop Escape behavior for active overlays.

The two final regression corrections received focused automated and
real-application checks. The complete all-profile manual checklist was not
repeated afterward; that explicit evidence limit is recorded in
`docs/audits/phase-6-verification.md`.

Future interface changes must run their focused tests, the complete suite,
and the device or desktop checks relevant to the changed behavior.

## GitHub Actions

`.github/workflows/quality.yml` runs on pushes, pull requests, and manual
workflow requests.

The workflow:

1. Uses a Windows runner.
2. Installs Python 3.13.14.
3. Installs `requirements-dev.txt`.
4. Compiles the Python source.
5. Runs the complete test suite with coverage.

The hosted Windows runner exposes only OpenGL 1.1, while Kivy requires
OpenGL 2.0 for real rendering. The workflow therefore uses Kivy's mock
graphics backend for headless tests. This setting exists only inside the
workflow and does not change desktop or Android rendering.

## Expected Results

A change is ready for checkpoint review when:

- Every collected test passes.
- Coverage collection finishes successfully.
- Compilation produces no errors.
- `git diff --check` produces no output.
- `git status --short` shows only intended files.
- Any relevant desktop or Android behavior check passes.
- GitHub Actions becomes green after the change is pushed.

The number of tests will increase as the project grows. Success depends on
all collected tests passing, not on preserving a fixed count.

## Before Committing

1. Review the intended changed files.
2. Run the required local checks.
3. Perform any real-application check relevant to the change.
4. Commit the verified checkpoint.
5. Push the branch and confirm that GitHub Actions passes.
