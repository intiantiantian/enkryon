#!/usr/bin/env bash

set -Eeuo pipefail

readonly DEFAULT_KEYSTORE="$HOME/keystores/enkryon-release.jks"
readonly DEFAULT_ALIAS="enkryon"

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
