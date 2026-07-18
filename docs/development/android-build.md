# Reproducible Android Builds

This guide defines the verified host environment and repeatable commands
used to build Enkryon for Android.

Release signing is documented separately. Do not place a keystore, alias,
password, or signing environment file in the repository.

## Verified Build Environment

The Phase 4 baseline was verified with:

| Component | Verified value |
|---|---|
| Host | Windows 10 with WSL2 |
| Linux distribution | Ubuntu 24.04.4 LTS, `x86_64` |
| Host Python | Python 3.12.3 |
| Java runtime and compiler | OpenJDK 17.0.19 |
| Buildozer | 1.6.0 |
| Cython | 0.29.37 |
| Python-for-Android | `v2026.05.09` (`58d21141`) |
| Android target API | 36 |
| Android minimum API | 24 |
| Android NDK | 28 |
| Android NDK API | 24 |

`requirements-android.txt` pins the host-side Python build tools.
`buildozer.spec` pins the Python-for-Android release and Android
compatibility settings.

These host tools are separate from `requirements.txt`, which contains the
libraries packaged inside Enkryon, and `requirements-dev.txt`, which
contains Windows development and testing tools.

## Keep the Build on the Linux Filesystem

The Windows repository is the canonical working copy:

```text
A:\Portfolio\Projects\Enkryon\Programming
```

The Android build copy is stored inside the WSL filesystem:

```text
~/Projects/enkryon
```

Do not run Buildozer directly inside `/mnt/a`. Linux builds on a mounted
Windows filesystem are slower and can make build dependencies behave as
though they are running on Windows.

The WSL copy is for Android builds only. Make source changes and Git
commits in the canonical Windows repository.

## First-Time Ubuntu Setup

Install the system packages required by the Buildozer and
Python-for-Android toolchains:

```bash
sudo apt update
sudo apt install -y \
    git zip unzip openjdk-17-jdk python3-pip \
    python3-virtualenv autoconf automake autopoint gettext \
    libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo6 cmake libffi-dev libssl-dev
```

If several Java versions are installed, select OpenJDK 17:

```bash
sudo update-alternatives --config java
sudo update-alternatives --config javac
```

Install Rust through the official Rust installer if it is not already
available, then follow its instruction to load Cargo from the shell.

## Create the Android Build Environment

From the WSL build copy:

```bash
cd ~/Projects/enkryon
python3 -m virtualenv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-android.txt
```

For later sessions:

```bash
cd ~/Projects/enkryon
source .venv/bin/activate
```

Verify the important tools before building:

```bash
python --version
buildozer --version
java -version
javac -version
```

## Synchronize the Current Source

Before synchronization, run the required tests and confirm that the
canonical Windows working tree contains only the intended state.

From WSL, synchronize the Windows repository into the Linux build copy:

```bash
rsync -a --delete \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='.buildozer/' \
    --exclude='__pycache__/' \
    --exclude='.pytest_cache/' \
    --exclude='.coverage' \
    /mnt/a/Portfolio/Projects/Enkryon/Programming/ \
    "$HOME/Projects/enkryon/"
```

The trailing slash on both directory paths is intentional. The exclusions
preserve the Linux virtual environment, Buildozer cache, and Git metadata.
`--delete` removes obsolete source files from the build copy so deleted
Python or asset files cannot remain in a later APK.

Do not reverse the source and destination paths. That would overwrite the
canonical Windows project with the build copy.

After synchronization, reactivate the Linux environment and confirm the
pinned tools remain installed:

```bash
cd ~/Projects/enkryon
source .venv/bin/activate
python -m pip install -r requirements-android.txt
```

## Build Modes

Create a verbose debug APK for development checks:

```bash
buildozer -v android debug
```

A debug APK uses the Android debug signing identity. It must not be treated
as an official Enkryon release and cannot upgrade an installation signed
with Enkryon's permanent certificate.

Create a release APK after the secure signing environment has been loaded:

```bash
buildozer -v android release
```

Artifacts are written to `bin/`. Release artifacts must still pass the
documented alignment, signature, checksum, install, and upgrade checks.

## Cleaning and Rebuilding

Clean the current Android target when application or build settings require
a fresh target build:

```bash
buildozer android clean
```

Use a full distribution clean only when the cached SDK, NDK, or
Python-for-Android state is corrupt or when the pinned toolchain changes:

```bash
buildozer distclean
```

`distclean` removes downloaded and compiled build state, so the next build
will take substantially longer. Do not use it as a routine build step.

## Normal Build Sequence

1. Make and verify changes in the Windows repository.
2. Confirm the Windows Git working tree is in the intended state.
3. Synchronize Windows source into the WSL build copy.
4. Activate the WSL `.venv`.
5. Install the pinned Android requirements.
6. Run the appropriate debug or release Buildozer command.
7. Inspect the generated artifact instead of assuming a successful command
   produced the expected package.
8. Copy only the verified artifact and its recorded checksum to the release
   location.

Never edit release source only inside the WSL build copy, because the next
synchronization intentionally replaces it with the canonical Windows
source.
