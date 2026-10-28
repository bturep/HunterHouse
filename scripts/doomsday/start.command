#!/bin/sh
# Hunter House archive -- start the offline copy (Mac: double-click; Linux: sh start.command).
cd "$(dirname "$0")" && exec python3 serve.py "$@"
