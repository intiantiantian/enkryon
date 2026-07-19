# Android Release Signing

This guide defines how Enkryon release APKs are signed without storing a
private key or password in the repository.

## Permanent Signing Identity

The verified Enkryon signing identity is:

| Property | Verified value |
|---|---|
| Package | `com.intian.enkryon` |
| Key alias | `enkryon` |
| Keystore format | JKS |
| Certificate SHA-256 | `E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D` |

Every Enkryon upgrade must use this identity. An APK signed with a debug
key or a different release key cannot upgrade an existing Enkryon
installation.

The JKS format warning printed by `keytool` is informational. Do not
convert the permanent keystore during a release. A format conversion
mutates a critical release asset and requires a separately verified backup
and recovery procedure.

## Keystore Storage

The canonical private copy is outside the repository:

```text
A:\Portfolio\Projects\Enkryon\Private\signing\enkryon-release.jks
```

The WSL build copy is also outside the repository:

```text
~/keystores/enkryon-release.jks
```

The WSL directory must use mode `700`, and the keystore must deny access
to group and other users. The verified file mode is `600`.

Never put a keystore, signing password, signing environment file, or
private-key export inside the Enkryon repository. Never paste a password
into documentation, Git history, an issue, a pull request, or a CI log.

## Confirm the Public Identity

Before signing a release, inspect the public certificate information:

```bash
keytool -list -v \
    -keystore "$HOME/keystores/enkryon-release.jks"
```

Enter the password only at the private terminal prompt. Confirm the alias
and SHA-256 fingerprint against the permanent identity above.

## Build Without Persisting Passwords

Synchronize the verified Windows source into WSL and activate the Android
build environment as described in `docs/development/android-build.md`.
Then run:

```bash
bash scripts/build-android-release.sh
```

The helper uses the verified default keystore path and alias, prompts for
both passwords without echoing them, exports the four variables required
by Python-for-Android only for the Buildozer process, and clears them when
the script exits:

- `P4A_RELEASE_KEYSTORE`
- `P4A_RELEASE_KEYSTORE_PASSWD`
- `P4A_RELEASE_KEYALIAS`
- `P4A_RELEASE_KEYALIAS_PASSWD`

After Buildozer succeeds, the helper verifies the permanent certificate,
checks APK alignment, and creates these standardized files in `bin/`:

```text
Enkryon-v<version>.apk
Enkryon-v<version>.apk.sha256
```

The version is read from `main.py`. The checksum file records only the
standard artifact filename so it can be checked from any release folder.

Do not run the helper with shell tracing such as `bash -x`, because tracing
can expose sensitive values.

An alternate external keystore path or public alias may be supplied for a
controlled recovery exercise:

```bash
P4A_RELEASE_KEYSTORE=/absolute/external/path/enkryon-release.jks \
P4A_RELEASE_KEYALIAS=enkryon \
bash scripts/build-android-release.sh
```

Passwords are still entered through the private prompts.

## Independently Verify the Resulting Signature

The helper performs these checks automatically. Use the commands below to
confirm a prepared artifact independently or during release review.

Locate the Android SDK signing tool and the newest release APK:

```bash
APKSIGNER="$(find "$HOME/.buildozer/android/platform/android-sdk/build-tools" \
    -type f -name apksigner -print | sort -V | tail -n 1)"
APK="$(find bin -maxdepth 1 -type f -name '*-release*.apk' \
    -printf '%T@ %p\n' | sort -nr | head -n 1 | cut -d' ' -f2-)"

test -x "$APKSIGNER"
test -n "$APK"
printf 'APK: %s\n' "$APK"
```

Verify the APK and display only public certificate information:

```bash
"$APKSIGNER" verify --verbose --print-certs "$APK" |
    grep -E 'Verified using|Signer #1 certificate SHA-256 digest'
```

The certificate digest must equal this value without separators:

```text
e3d29b108a694aed7587fd995f00b0226497b566a6533ae847ef2371a012c43d
```

Generate and record the artifact checksum only after signature
verification succeeds:

```bash
sha256sum "$APK"
```

A successful Buildozer command alone does not prove that the APK used the
permanent certificate. Signature verification is a required release
checkpoint.

## References

- [Android: Prepare your app for release](https://developer.android.com/studio/publish/preparing)
- [Kivy: Creating a release APK](https://github.com/kivy/kivy/wiki/creating-a-release-apk)
