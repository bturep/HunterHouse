#!/usr/bin/env bash
# backup_r2.sh — mirror the Hunter House R2 archive bucket to a local disk.
#
# WHY: the master TIFs (preservation copies) live in ONE Cloudflare R2 bucket with
# no object versioning. Nothing else backs them up — the metadata sidecars and the
# catalogue snapshot live in the SAME bucket, so a bucket delete / account loss /
# rclone mishap takes everything at once. On 2026-06-30 an unchecked rclone move
# overwrote three masters in place; they were only recovered because source JPEGs
# happened to survive in a Downloads folder. This script is the off-site second copy
# that should have existed then. See AUDIT-2026-07.md §B1.
#
# This runs on the machine where rclone + the R2 remote are configured (the Mac).
# rclone.conf holds the R2 credentials; this script contains no secrets.
#
# USAGE:
#   ./backup_r2.sh /Volumes/HHF-Backup                    # DRY-RUN — shows what would copy
#   ./backup_r2.sh /Volumes/HHF-Backup --execute          # actually sync
#   ./backup_r2.sh /Volumes/HHF-Backup --execute --check  # sync, then verify checksums
#
# Cadence: monthly, or at any session-end where masters changed. Keep the drive
# OFF-SITE (not in the house) — that single habit takes the archive from one managed
# copy (~NDSA Level 1) to a real second copy in a different place (~Level 2).
#
# Overrides (env): HH_R2_REMOTE (default "hh-r2"), HH_R2_BUCKET (default
# "hunter-house-archive").

set -euo pipefail

REMOTE="${HH_R2_REMOTE:-hh-r2}"
BUCKET="${HH_R2_BUCKET:-hunter-house-archive}"
SRC="$REMOTE:$BUCKET"

DEST="${1:-}"
if [ -z "$DEST" ]; then
  echo "usage: $0 <dest-dir> [--execute] [--check]" >&2
  exit 2
fi
shift || true

EXECUTE=0
CHECK=0
for a in "$@"; do
  case "$a" in
    --execute) EXECUTE=1 ;;
    --check)   CHECK=1 ;;
    *) echo "unknown arg: $a" >&2; exit 2 ;;
  esac
done

command -v rclone >/dev/null 2>&1 || { echo "error: rclone not found on PATH" >&2; exit 1; }
[ -d "$DEST" ] || { echo "error: dest dir does not exist: $DEST" >&2; exit 1; }

MIRROR="$DEST/hh-r2-mirror"
STAMP="$(date +%Y%m%d-%H%M%S)"
# --backup-dir: anything the sync would DELETE or OVERWRITE is moved here instead of
# being destroyed, so the mirror itself can never lose a master to a bad upstream state.
TRASH="$DEST/hh-r2-deleted-$STAMP"

echo "source:      $SRC"
echo "mirror:      $MIRROR"
echo "backup-dir:  $TRASH   (holds anything a sync would delete/overwrite)"
echo

COMMON=( --backup-dir "$TRASH" --transfers 8 --checkers 16 --stats 10s --stats-one-line )

if [ "$EXECUTE" -eq 1 ]; then
  echo ">>> EXECUTE: syncing R2 -> local mirror"
  rclone sync "$SRC" "$MIRROR" "${COMMON[@]}"
  echo
  echo ">>> holdings after sync:"
  rclone size "$MIRROR" | tee "$DEST/hh-r2-size-$STAMP.txt"
else
  echo ">>> DRY-RUN (no changes made). Re-run with --execute to sync."
  rclone sync "$SRC" "$MIRROR" --dry-run "${COMMON[@]}"
fi

if [ "$CHECK" -eq 1 ]; then
  echo
  echo ">>> FIXITY: comparing checksums, R2 vs local mirror (one-way)"
  # Note: files R2 stored via multipart upload may not expose a whole-file MD5;
  # rclone reports those as unchecked rather than failed. A clean run = every
  # master present locally with a matching checksum.
  rclone check "$SRC" "$MIRROR" --checksum --one-way | tee "$DEST/hh-r2-fixity-$STAMP.txt"
fi

echo
echo "done. Store the drive off-site. For NDSA Level 2/3, add a second copy in a"
echo "different location or a second cloud (e.g. Backblaze B2) as a later step."
