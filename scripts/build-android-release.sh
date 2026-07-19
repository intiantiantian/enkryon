#!/usr/bin/env bash

set -Eeuo pipefail

readonly DEFAULT_KEYSTORE="$HOME/keystores/enkryon-release.jks"
readonly DEFAULT_ALIAS="enkryon"
readonly EXPECTED_CERTIFICATE_SHA256="e3d29b108a694aed7587fd995f00b0226497b566a6533ae847ef2371a012c43d"
readonly RELEASE_NAME="Enkryon"

KEYSTORE_PATH="${P4A_RELEASE_KEYSTORE:-$DEFAULT_KEYSTORE}"
KEY_ALIAS="${P4A_RELEASE_KEYALIAS:-$DEFAULT_ALIAS}"

cleanup() {
    unset KEYSTORE_PASSWORD KEY_ALIAS_PASSWORD
    unset P4A_RELEASE_KEYSTORE P4A_RELEASE_KEYSTORE_PASSWD
    unset P4A_RELEASE_KEYALIAS P4A_RELEASE_KEYALIAS_PASSWD
}
trap cleanup EXIT HUP INT TERM

fail() {
    printf 'Release signing error: %s\n' "$1" >&2
    exit 1
}

[[ "$KEYSTORE_PATH" = /* ]] || fail "the keystore path must be absolute"
[[ -f "$KEYSTORE_PATH" ]] || fail "keystore not found: $KEYSTORE_PATH"
[[ -n "$KEY_ALIAS" ]] || fail "the signing alias is empty"

KEYSTORE_MODE="$(stat -c '%a' "$KEYSTORE_PATH")"
[[ "$KEYSTORE_MODE" =~ ^[0-7]+$ ]] || fail "cannot read keystore permissions"

if (( (8#$KEYSTORE_MODE & 8#077) != 0 )); then
    fail "keystore permissions must deny access to group and others"
fi

# Discard inherited password variables. Passwords must be supplied privately
# for this build and must never be read from a repository file.
unset P4A_RELEASE_KEYSTORE_PASSWD P4A_RELEASE_KEYALIAS_PASSWD

read -r -s -p "Keystore password: " KEYSTORE_PASSWORD
printf '\n'
read -r -s -p "Key alias password: " KEY_ALIAS_PASSWORD
printf '\n'

[[ -n "$KEYSTORE_PASSWORD" ]] || fail "the keystore password is empty"
[[ -n "$KEY_ALIAS_PASSWORD" ]] || fail "the key alias password is empty"

export P4A_RELEASE_KEYSTORE="$KEYSTORE_PATH"
export P4A_RELEASE_KEYSTORE_PASSWD="$KEYSTORE_PASSWORD"
export P4A_RELEASE_KEYALIAS="$KEY_ALIAS"
export P4A_RELEASE_KEYALIAS_PASSWD="$KEY_ALIAS_PASSWORD"

printf 'Building a signed release with alias %s.\n' "$KEY_ALIAS"
buildozer -v android release

APP_VERSION="$(
    sed -n \
        's/^__version__[[:space:]]*=[[:space:]]*"\([^"]*\)"/\1/p' \
        main.py
)"
[[ -n "$APP_VERSION" ]] || fail "cannot read the application version"

BUILT_APK="$(
    find bin -maxdepth 1 -type f -name '*-release*.apk' \
        ! -name "${RELEASE_NAME}-v*.apk" \
        -printf '%T@ %p\n' |
        sort -nr |
        head -n 1 |
        cut -d' ' -f2-
)"
[[ -n "$BUILT_APK" ]] || fail "Buildozer did not produce a release APK"

BUILD_TOOLS_ROOT="$HOME/.buildozer/android/platform/android-sdk/build-tools"
APKSIGNER="$(
    find "$BUILD_TOOLS_ROOT" -type f -name apksigner -print |
        sort -V |
        tail -n 1
)"
ZIPALIGN="$(
    find "$BUILD_TOOLS_ROOT" -type f -name zipalign -print |
        sort -V |
        tail -n 1
)"
[[ -x "$APKSIGNER" ]] || fail "apksigner was not found"
[[ -x "$ZIPALIGN" ]] || fail "zipalign was not found"

SIGNATURE_OUTPUT="$(
    "$APKSIGNER" verify --verbose --print-certs "$BUILT_APK"
)" || fail "APK signature verification failed"
CERTIFICATE_SHA256="$(
    printf '%s\n' "$SIGNATURE_OUTPUT" |
        sed -n 's/^.*certificate SHA-256 digest: //p' |
        head -n 1 |
        tr '[:upper:]' '[:lower:]'
)"
[[ "$CERTIFICATE_SHA256" == "$EXPECTED_CERTIFICATE_SHA256" ]] ||
    fail "APK certificate does not match the permanent Enkryon identity"

"$ZIPALIGN" -c -P 16 -v 4 "$BUILT_APK" >/dev/null ||
    fail "APK alignment verification failed"

RELEASE_APK="bin/${RELEASE_NAME}-v${APP_VERSION}.apk"
RELEASE_CHECKSUM="${RELEASE_APK}.sha256"
cp -- "$BUILT_APK" "$RELEASE_APK"
(
    cd bin
    sha256sum "$(basename "$RELEASE_APK")" > \
        "$(basename "$RELEASE_CHECKSUM")"
)

printf 'Verified release artifact: %s\n' "$RELEASE_APK"
printf 'SHA-256 checksum file: %s\n' "$RELEASE_CHECKSUM"
