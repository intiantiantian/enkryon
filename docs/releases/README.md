# Android Release Records

This directory defines the public records prepared for every Enkryon
Android release. APK binaries and checksum files remain outside Git because
they are generated artifacts.

## Standard Names

For version `X.Y.Z`, use exactly:

```text
Enkryon-vX.Y.Z.apk
Enkryon-vX.Y.Z.apk.sha256
Enkryon-vX.Y.Z-release-notes.md
```

Before version 1.0, Enkryon versions used `major.phase.subphase` as the
roadmap reference. Phase 8 prepared `v0.8.0` from `v0.7.0`; Phase 5 was an
internal architecture checkpoint and did not require a public `v0.5.x`
APK. Phase 9 prepares the first stable release, `v1.0.0`, from official
`v0.8.0`. Update 1 prepares `v1.1.0` from official `v1.0.0` and adds the
first database migration and backup-format expansion after the stable release.
Update 2 prepares `v1.2.0` from official `v1.1.0`, adds Pending Transactions,
migration 6, and backup format 3. Update 3 releases `v1.3.0` from official
`v1.2.0`, adds Pass-through Transfers, migrations 7 through 9, and backup
format 4. Update 4 releases `v1.4.0` from official `v1.3.0`, adds Daily Bank
Interest, migration 10, and backup format 5.

`main.py` is the version source. The secure release helper reads that value,
verifies the permanent Enkryon certificate and APK alignment, then creates
the standardized APK and checksum in `bin/`.

## Prepare a Release

1. Choose the version and update `main.py`.
2. Move completed entries from `CHANGELOG.md` under the new version and
   release date.
3. Copy `RELEASE_NOTES_TEMPLATE.md` to
   `Enkryon-vX.Y.Z-release-notes.md` in the external release folder.
4. Replace every placeholder and describe upgrade or migration effects.
5. Run the complete local checks and require a green GitHub Actions run.
6. Synchronize the canonical Windows source into WSL.
7. Run `bash scripts/build-android-release.sh` in WSL.
8. Complete `docs/development/android-release-checklist.md`.
9. Copy only the verified APK, checksum, and completed release notes to the
   external release folder.
10. Verify the copied checksum from that folder:

```bash
sha256sum -c Enkryon-vX.Y.Z.apk.sha256
```

Do not publish a release whose checklist contains an unchecked required
item. Never store a keystore, signing password, or private-key export with
the release notes.

## Release Notes Policy

Release notes must state:

- what users will notice;
- the supported Android range;
- whether an in-place upgrade was tested and from which official version;
- whether stored data or schema migrations are affected;
- known limitations or risks;
- the artifact size and SHA-256 checksum;
- the permanent certificate fingerprint used for signing.

Internal commands, passwords, private paths, and unverified claims do not
belong in public release notes.
