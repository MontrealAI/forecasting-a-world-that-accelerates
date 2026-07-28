#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
make release-bundle VERSION="$(cat VERSION)"
printf 'Release artifacts created in dist/.\n'
