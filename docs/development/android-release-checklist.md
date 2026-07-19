# Android Release Checklist

Complete this checklist for every official Enkryon Android release. Record
the evidence in the release notes or the phase verification report.

## 1. Release identity and source

- [ ] The release version follows `MAJOR.MINOR.PATCH` format.
- [ ] `main.py`, Android package metadata, changelog, and release notes use
  the same version.
- [ ] The package name is `com.intian.enkryon`.
- [ ] `CHANGELOG.md` has a dated entry for the release.
- [ ] Release-note placeholders have all been replaced.
- [ ] The intended commit is reviewed and the Git working tree is clean.

## 2. Automated quality checks

- [ ] The full test suite passes locally.
- [ ] Python compilation completes without errors.
- [ ] `git diff --check` produces no output.
- [ ] GitHub Actions is green for the release commit.
- [ ] The legacy database fixture upgrades without data loss.

## 3. Reproducible Android build

- [ ] Windows source is synchronized into the WSL build copy.
- [ ] The documented Python, Java, Buildozer, Cython, P4A, SDK, and NDK
  versions are used.
- [ ] `p4a.branch` is `master` and `p4a.commit` is `58d21141`.
- [ ] The secure helper builds the release without exposing passwords.
- [ ] No keystore, password file, database, tests, documentation, cache, or
  repository screenshot is packaged in the APK.

## 4. Artifact and security verification

- [ ] The artifact is named `Enkryon-vX.Y.Z.apk`.
- [ ] `aapt` reports the expected package, version name, version code,
  minimum API, target API, and native architectures.
- [ ] The manifest reports `android:allowBackup="false"`.
- [ ] `apksigner verify --verbose --print-certs` passes.
- [ ] The signer certificate SHA-256 is the permanent Enkryon fingerprint:
  `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D`.
- [ ] `zipalign -c -P 16 -v 4` passes.
- [ ] The `.sha256` file matches the final copied APK.
- [ ] Artifact size and checksum are recorded in the release notes.

## 5. Installation and launch

- [ ] A clean installation succeeds on a supported Android device.
- [ ] The launcher icon is centered, unclipped, and visually correct.
- [ ] The splash screen and first launch complete without a crash.
- [ ] Android reports the intended `versionName` and `versionCode`.

## 6. Official in-place upgrade

- [ ] The previous official APK is signed with the permanent certificate.
- [ ] Representative accounts, categories, income, expenses, centavo values,
  dates, and notes are recorded before upgrading.
- [ ] The new official APK is installed with `adb install -r` without first
  uninstalling or clearing application data.
- [ ] The upgrade succeeds without a signature or downgrade error.
- [ ] Existing record IDs, row counts, relationships, notes, and exact totals
  remain correct after migrations run.
- [ ] `PRAGMA foreign_key_check` reports no violations.
- [ ] Repeating application startup does not repeat completed migrations.
- [ ] Data remains correct after force-stop and relaunch.

## 7. Core workflow smoke test

- [ ] Dashboard balances and income/expense totals are correct.
- [ ] Accounts and categories can be created and edited.
- [ ] Income and expense transactions can be created, edited, filtered, and
  deleted.
- [ ] Centavo values display and total exactly.
- [ ] Empty states, validation messages, and destructive confirmations work.
- [ ] Clearing all data is tested only on disposable test data.

## 8. Approval and publication

- [ ] Backup behavior and recovery limitations are stated accurately.
- [ ] Known issues and upgrade risks are included in the release notes.
- [ ] The APK, checksum, and release notes are copied to the designated
  external release folder.
- [ ] The copied checksum is verified before publication.
- [ ] Final approval is recorded before creating the public release.
