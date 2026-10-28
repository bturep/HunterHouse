#!/bin/sh
# Hunter House archive -- check every file against the fixity manifest.
cd "$(dirname "$0")" && exec python3 verify.py --no-pause "$@"
