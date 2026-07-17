# Phase 2 Verification Report

Date: 2026-07-17  
Branch: `phase-2-financial-correctness`  
Base tag: `phase-1-complete`  
Application version: `0.4.0`

## Objective

Make Enkryon's financial storage exact, safely upgrade existing databases,
enforce core data rules, and unify application version metadata.

## Result

Phase 2 desktop, database, legacy-upgrade, and Android release
verification passed.

Transaction amounts are now stored and calculated as integer centavos.
Existing data upgraded through three transactional migrations without
changing row counts, totals, foreign-key relationships, or transaction IDs.

The v0.4.0 APK was signed with the permanent Enkryon release certificate,
verified with `apksigner` and `zipalign`, clean-installed on Android, and
passed the centavo transaction smoke test.

Earlier debug-signed installations require a clean reinstall because
v0.4.0 establishes Enkryon's permanent release-signing identity.

## Implementation commits

| Commit | Change |
|---|---|
| `6046bf0` | Centralize database schema initialization |
| `a4889dc` | Add transactional database migration framework |
| `ca92ae0` | Store transaction amounts as integer centavos |
| `010be21` | Enforce database validation constraints |
| `52b13a4` | Unify application version metadata |
| `acc4472` | Fix centavo transaction payload integration |
| `d129d94` | Document Phase 2 database verification |
| `4f1254b` | Prepare v0.4.0 Android release |

## Automated verification

Final result:

```text
88 passed
```

## Android release verification

- Package: `com.intian.enkryon`
- Version name: `0.4.0`
- Version code: `1024400`
- Minimum SDK: 24
- Target SDK: 33
- Architectures: ARM64 and ARMv7
- Artifact: `Enkryon-v0.4.0.apk`
- Artifact size: 51,378,096 bytes
- APK SHA-256: `b663852dfb4220553e43ad010b45effc68854e05ed3009c7adf71322a4b0d532`
- Signing scheme: APK Signature Scheme v2
- Certificate SHA-256: `e3d29b108a694aed7587fd995f00b0226497b566a6533ae847ef2371a012c43d`
- `apksigner` verification: passed
- `zipalign` verification: passed
- Clean-install smoke test: passed
