# Phase 4 Verification

## Result

Passed on July 19, 2026.

Phase 4 established a repeatable Android release process and produced a
permanently signed `v0.4.8` APK that safely upgraded official `v0.4.0` on a
physical Android device without losing the controlled financial dataset.

## Automated Checks

- `125` tests passed with coverage reporting.
- Python source compilation completed without errors.
- Git whitespace validation completed without errors.
- GitHub Actions passed after each stable checkpoint.
- Tests protect Android compatibility settings, backup policy, toolchain
  pins, package exclusions, adaptive assets, signing configuration,
  certificate parsing, release naming, checksums, and version extraction.

## Reproducible Build Configuration

- Host workflow: Windows 10 canonical source with an Ubuntu 24.04.4 WSL2
  build copy.
- Buildozer: `1.6.0`
- Cython: `0.29.37`
- Python-for-Android: commit `58d21141`
- Android target API: 36
- Android minimum API: 24
- Android NDK: 28
- Android NDK API: 24
- Native architectures: `arm64-v8a`, `armeabi-v7a`
- Android automatic backup: disabled

The build, signing, asset, release, and synchronization procedures are
documented under `docs/development/`. Signing passwords and private keys
remain outside the repository.

## Verified Release Candidate

- Artifact: `Enkryon-v0.4.8.apk`
- Package: `com.intian.enkryon`
- Version name: `0.4.8`
- Version code: `1024408`
- Size: 45,767,240 bytes
- SHA-256:
  `de79af685d4d1972c8e0cbadb5396f643c4b0083e7ef7235e48945120d16113e`
- Signers: one
- Signature scheme: APK Signature Scheme v2
- ZIP alignment: passed
- Packaged adaptive icon and splash resources: present
- Repository screenshots and duplicated source assets: absent
- Development and sensitive files: absent

The release certificate SHA-256 digest is:

```text
e3d29b108a694aed7587fd995f00b0226497b566a6533ae847ef2371a012c43d
```

## Android Upgrade Evidence

The official `v0.4.0` baseline was verified with the same permanent
certificate, clean-installed, and populated through the application. The
app was closed and relaunched to establish baseline persistence.

`v0.4.8` was then installed with `adb install -r`, without uninstalling or
clearing the package. Accounts, category groups, categories, transactions,
notes, exact totals, and account balances survived. A PHP 0.02 expense was
created after the upgrade and remained present after another relaunch.

The full controlled dataset and artifact evidence are recorded in
`docs/audits/phase-4-upgrade-verification.md`.

## Known Limits Carried Forward

- Android automatic backup remains disabled until Phase 7 implements an
  explicit, validated backup and restore flow.
- Both supported ABIs remain in one APK. Further size work must not weaken
  supported-device compatibility.
- Broader device, accessibility, font-size, and responsive-layout testing
  remains assigned to Phase 6.
- Phase 5 will reduce screen-level workflow and business logic while
  preserving the behavior verified here.

## Completion Gate

Passed. The build is documented and reproducible, the APK excludes
development-only content, the permanent signature and alignment pass, and
`v0.4.8` installs over official `v0.4.0` without losing user data.
