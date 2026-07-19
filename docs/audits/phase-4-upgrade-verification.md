# Phase 4 Android Upgrade Verification

## Result

Passed on July 19, 2026.

The permanently signed Enkryon `v0.4.8` APK installed over the official
permanently signed `v0.4.0` APK without uninstalling the application or
losing its local records. The upgraded database also accepted and retained
a new transaction after the application was closed and relaunched.

## Scope

This verification covered:

- Authenticity and alignment of both Android release artifacts.
- Clean installation of the official `v0.4.0` baseline.
- Creation and persistence of a controlled baseline dataset.
- In-place installation of `v0.4.8` with `adb install -r`.
- Preservation of accounts, category data, transactions, notes, and totals.
- A new database write after the upgrade and persistence after relaunch.

## Verified Artifacts

### Official baseline

- Artifact: `Enkryon-v0.4.0.apk`
- Package: `com.intian.enkryon`
- Version name: `0.4.0`
- Version code: `1024400`
- Minimum Android API: 24
- Target Android API: 33
- Native architectures: `arm64-v8a`, `armeabi-v7a`
- SHA-256:
  `b663852dfb4220553e43ad010b45effc68854e05ed3009c7adf71322a4b0d532`
- ZIP alignment: passed

### Upgrade candidate

- Artifact: `Enkryon-v0.4.8.apk`
- Package: `com.intian.enkryon`
- Version name: `0.4.8`
- Version code: `1024408`
- Minimum Android API: 24
- Target Android API: 36
- Native architectures: `arm64-v8a`, `armeabi-v7a`
- Size: 45,767,240 bytes
- SHA-256:
  `de79af685d4d1972c8e0cbadb5396f643c4b0083e7ef7235e48945120d16113e`
- ZIP alignment: passed
- Excluded source assets: absent

Both artifacts contain one signer and use the permanent Enkryon release
certificate with this SHA-256 digest:

```text
e3d29b108a694aed7587fd995f00b0226497b566a6533ae847ef2371a012c43d
```

## Baseline Dataset

The following records were created through the `v0.4.0` user interface:

- Accounts: `Phase4 Cash`, `Phase4 Bank`
- Income group: `Phase4 Income`
- Expense group: `Phase4 Expense`
- Income category: `Upgrade Salary`
- Expense category: `Upgrade Food`
- Income: PHP 1,234.56 in `Phase4 Cash`, note
  `Official v0.4.0 baseline`
- Expense: PHP 10.20 in `Phase4 Cash`, note `Upgrade expense`
- Expense: PHP 0.01 in `Phase4 Bank`, note `Centavo boundary`

The baseline values were:

- Income: PHP 1,234.56
- Expenses: PHP 10.21
- Overall balance: PHP 1,224.35
- `Phase4 Cash`: PHP 1,224.36
- `Phase4 Bank`: -PHP 0.01

The app was closed and relaunched before the upgrade. The dataset persisted.

## Upgrade Procedure and Evidence

1. The existing debug installation was removed because its certificate was
   not the permanent release identity.
2. The official `v0.4.0` release APK was clean-installed and launched.
3. The controlled baseline dataset was created and verified after relaunch.
4. `Enkryon-v0.4.8.apk` was installed using `adb install -r`, without
   uninstalling or clearing `com.intian.enkryon`.
5. Android reported version code `1024408`, version name `0.4.8`, minimum
   API 24, and target API 36.
6. The upgraded application launched with the baseline dataset preserved.
7. A PHP 0.02 expense was added to `Phase4 Bank` under `Upgrade Food` with
   the note `v0.4.8 post-upgrade`.
8. The application was closed and relaunched. The new transaction persisted.

The final values after the post-upgrade write were:

- Income: PHP 1,234.56
- Expenses: PHP 10.23
- Overall balance: PHP 1,224.33
- `Phase4 Bank`: -PHP 0.03

## Automated and Packaging Evidence

- The most recent local regression run passed all 122 tests.
- Python source compilation completed without errors.
- Git whitespace validation produced no errors.
- The `v0.4.8` checksum sidecar validated successfully.
- APK signature, permanent certificate, ZIP alignment, API levels, native
