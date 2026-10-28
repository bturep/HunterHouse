#!/usr/bin/env python3
"""
Check this drive against its fixity manifest (fixity/manifest-latest.sha256).

Re-hashes every file listed and reports anything changed, missing, or new.
Standard library only. Read-only: it never repairs or deletes anything.

Usage:  python3 verify.py
"""

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "fixity", "manifest-latest.sha256")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.isfile(MANIFEST):
        sys.exit("No manifest at fixity/manifest-latest.sha256.")
    expected = {}
    with open(MANIFEST, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line:
                digest, rel = line.split("  ", 1)
                expected[rel] = digest
    print("Checking %d files against %s ..." % (len(expected), os.path.basename(MANIFEST)))
    changed, missing = [], []
    for i, (rel, digest) in enumerate(sorted(expected.items()), 1):
        p = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(p):
            missing.append(rel)
        elif sha256(p) != digest:
            changed.append(rel)
        if i % 250 == 0:
            print("  %d / %d" % (i, len(expected)))
    fx = os.path.join(ROOT, "fixity")
    extra = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if os.path.join(dp, d) != fx]
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), ROOT).replace(os.sep, "/")
            if rel not in expected:
                extra.append(rel)
    print()
    for label, items in (("CHANGED", changed), ("MISSING", missing), ("NOT IN MANIFEST", extra)):
        for rel in items:
            print("  %-16s %s" % (label, rel))
    if changed or missing:
        print("\nFAIL: %d changed, %d missing. Restore from another copy." % (len(changed), len(missing)))
        return 1
    print("OK: all %d files match.%s" % (
        len(expected), " (%d new files not in the manifest)" % len(extra) if extra else ""))
    return 0


if __name__ == "__main__":
    code = main()
    if "--no-pause" not in sys.argv and os.name == "nt":
        input("\nPress Enter to close.")
    sys.exit(code)
