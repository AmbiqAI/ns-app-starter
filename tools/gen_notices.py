#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026, Ambiq
"""Generate THIRD-PARTY-NOTICES.md from the submodules' license files.

Walks the submodule trees listed in SUBMODULES (relative to the repository
root) and collects every file that looks like a license, notice, or EULA,
recursing into vendored `extern`/`third_party` payloads (e.g. the AmbiqSuite
SDK release trees, CMSIS, and TensorFlow Lite Micro's third_party/ deps).

A file matches if its name (case-insensitive) starts with "license",
"copying", or "notice", contains "eula" (this also catches AmbiqSuite's
AM-BSD-EULA.txt, which does not follow the LICENSE/COPYING/NOTICE stem), or
if it lives directly under a directory named "licenses" (this catches
modules/ns-cmsis-nn/LICENSES/*.txt).

This script does not judge or rewrite license text -- it only concatenates
whatever it finds, verbatim, under a heading for its repository-relative
path. It never modifies files inside the submodules.

Provenance: `.gitmodules` records a submodule's URL and path but not the
license text itself, and this repository's pinned commits for
modules/ns-cmsis-dsp and modules/ns-cmsis-nn are not always reachable on
their remotes (see the "Provenance" section this script writes into the
output). So every generated file stamps, per submodule, the exact commit
and ref actually read (`git -C <submodule> rev-parse HEAD` /
`--abbrev-ref HEAD`), and notes whether that commit matches the pin
recorded in this repository's index or is a substitute (typically the
`main` branch tip) read because the pin was unreachable. Regenerate this
file whenever a submodule pin changes or once a dangling pin is fixed --
`--check` compares against the committed file and reports the provenance
recorded in each so drift is attributable to a specific submodule commit.

Usage:
    python3 tools/gen_notices.py            # (re)write THIRD-PARTY-NOTICES.md
    python3 tools/gen_notices.py --check    # verify the file is up to date;
                                             # exits 1 and prints the stamped
                                             # provenance (both what was just
                                             # read and what is committed) if
                                             # not.

Output is deterministic: submodule order is fixed, files within a submodule
are sorted by relative path, and all paths are repository-relative with
forward slashes (no absolute paths), so the generated file is reproducible
across machines and operating systems given the same submodule commits.

Fails closed: if a submodule directory is missing or not checked out
(`git submodule update --init` not run), this script errors out naming the
missing submodule instead of silently generating a partial file.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "THIRD-PARTY-NOTICES.md"

# Submodule paths to walk, relative to REPO_ROOT. Kept explicit (rather than
# parsed from .gitmodules) so the set of trees this script touches is
# obvious on review. Update this list if a submodule is added or removed.
SUBMODULES = [
    "neuralspot",
    "modules/ns-cmsis-dsp",
    "modules/ns-cmsis-nn",
]

_NAME_PREFIXES = ("license", "copying", "notice")
# Restrict to plain-text-ish extensions so config/workflow files that merely
# start with "license" (e.g. .github/workflows/license-headers.yml) are not
# mistaken for license text.
_ALLOWED_SUFFIXES = ("", ".txt", ".md")

_PROVENANCE_LINE_RE = re.compile(
    r"^- `(?P<submodule>[^`]+)` @ `(?P<sha>[0-9a-fA-F]{7,40})` \((?P<ref>[^)]*)\)"
)


class SubmoduleMissingError(RuntimeError):
    """Raised when a submodule directory is missing/not checked out."""


def _is_license_file(path: Path) -> bool:
    if path.suffix.lower() not in _ALLOWED_SUFFIXES:
        return False
    name_lower = path.name.lower()
    if any(name_lower.startswith(prefix) for prefix in _NAME_PREFIXES):
        return True
    if "eula" in name_lower:
        return True
    if path.parent.name.lower() in ("license", "licenses"):
        return True
    return False


def _find_license_files(submodule_root: Path) -> list[Path]:
    import os

    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(submodule_root):
        # Never descend into a submodule's own .git directory.
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for filename in filenames:
            candidate = Path(dirpath) / filename
            if _is_license_file(candidate):
                found.append(candidate)
    found.sort(key=lambda p: p.relative_to(REPO_ROOT).as_posix())
    return found


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _relposix(path: Path) -> str:
    return PurePosixPath(path.relative_to(REPO_ROOT).as_posix()).as_posix()


def _run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _pinned_sha(submodule: str) -> str | None:
    """Return the gitlink commit recorded in this repo's index for `submodule`.

    This is what `.gitmodules` + the parent tree pin the submodule to. Returns
    None if the path has no gitlink entry (should not happen for an entry in
    SUBMODULES, but handled defensively).
    """
    result = subprocess.run(
        ["git", "ls-tree", "HEAD", "--", submodule],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    line = result.stdout.strip()
    if not line:
        return None
    # Format: "<mode> commit <sha>\t<path>"
    fields = line.split()
    if len(fields) >= 3 and fields[1] == "commit":
        return fields[2]
    return None


def _submodule_provenance(submodule: str) -> tuple[str, str]:
    """Return (sha, ref) actually checked out for `submodule`.

    Fails closed (raises SubmoduleMissingError naming the submodule) if it
    is not checked out, rather than silently generating a partial file.
    """
    root = REPO_ROOT / submodule
    if not root.is_dir() or not (root / ".git").exists():
        raise SubmoduleMissingError(
            f"submodule '{submodule}' is not checked out at {root}. "
            "Run `git submodule update --init` (or the equivalent manual "
            "clone/checkout for pins that are unreachable on the remote) "
            "before generating THIRD-PARTY-NOTICES.md."
        )
    sha = _run_git(root, "rev-parse", "HEAD")
    ref = _run_git(root, "rev-parse", "--abbrev-ref", "HEAD")
    return sha, ref


def _provenance_note(submodule: str, sha: str, pinned: str | None) -> str:
    if pinned is None:
        return "no pinned commit found in this repository's index."
    if sha == pinned:
        return "matches the commit pinned in this repository's index."
    return (
        f"the pinned commit (`{pinned}`) was unreachable on the submodule's "
        "remote at generation time; the tip shown here was read instead."
    )


def generate() -> tuple[str, dict[str, tuple[str, str]]]:
    """Return (file content, {submodule: (sha, ref)}).

    Raises SubmoduleMissingError (fail closed) if any submodule in
    SUBMODULES is not checked out.
    """
    provenance: dict[str, tuple[str, str]] = {}
    for submodule in SUBMODULES:
        provenance[submodule] = _submodule_provenance(submodule)

    lines: list[str] = []
    lines.append("# Third-Party Notices")
    lines.append("")
    lines.append(
        "Generated by `tools/gen_notices.py`. Do not hand-edit; regenerate "
        "with `python3 tools/gen_notices.py`, and verify with "
        "`python3 tools/gen_notices.py --check`."
    )
    lines.append("")
    lines.append(
        "This file concatenates, verbatim, every LICENSE, COPYING, NOTICE, "
        "and EULA file found while walking the vendored submodule trees "
        "(`neuralspot`, `modules/ns-cmsis-dsp`, `modules/ns-cmsis-nn`), "
        "including their nested `extern`/`third_party` payloads (AmbiqSuite "
        "SDK releases, CMSIS, TensorFlow Lite Micro and its dependencies, "
        "and similar vendored trees). See `NOTICE` for a short, hand-written "
        "summary naming each submodule and its primary license."
    )
    lines.append("")

    lines.append("## Provenance")
    lines.append("")
    lines.append(
        "Every submodule commit actually read to produce this file, so "
        "drift is attributable. See the script docstring for why a "
        "submodule's tip can differ from its `.gitmodules` pin."
    )
    lines.append("")
    for submodule in SUBMODULES:
        sha, ref = provenance[submodule]
        pinned = _pinned_sha(submodule)
        note = _provenance_note(submodule, sha, pinned)
        lines.append(f"- `{submodule}` @ `{sha}` ({ref}) -- {note}")
    lines.append("")

    for submodule in SUBMODULES:
        submodule_root = REPO_ROOT / submodule
        sha, ref = provenance[submodule]
        lines.append(f"## {submodule}")
        lines.append("")
        lines.append(f"Generated from: {submodule} @ {sha} ({ref})")
        lines.append("")

        license_files = _find_license_files(submodule_root)
        if not license_files:
            lines.append("_No LICENSE/COPYING/NOTICE/EULA files found._")
            lines.append("")
            continue

        for path in license_files:
            rel = _relposix(path)
            lines.append(f"### {rel}")
            lines.append("")
            lines.append("```")
            lines.append(_read_text(path).rstrip("\n"))
            lines.append("```")
            lines.append("")

    content = "\n".join(lines).rstrip("\n") + "\n"
    return content, provenance


def _extract_provenance(text: str) -> dict[str, tuple[str, str]]:
    found: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        match = _PROVENANCE_LINE_RE.match(line)
        if match:
            found[match.group("submodule")] = (match.group("sha"), match.group("ref"))
    return found


def _print_provenance(label: str, provenance: dict[str, tuple[str, str]]) -> None:
    print(f"{label}:", file=sys.stderr)
    for submodule in SUBMODULES:
        sha, ref = provenance.get(submodule, ("(none)", "(none)"))
        print(f"  - {submodule} @ {sha} ({ref})", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify THIRD-PARTY-NOTICES.md is up to date without writing it",
    )
    args = parser.parse_args(argv)

    try:
        content, provenance = generate()
    except SubmoduleMissingError as exc:
        print(f"gen_notices.py: {exc}", file=sys.stderr)
        return 1

    if args.check:
        existing = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        _print_provenance("Provenance read this run", provenance)
        if existing == content:
            print(f"{OUTPUT_PATH.relative_to(REPO_ROOT)} is up to date.")
            return 0
        _print_provenance("Provenance in committed file", _extract_provenance(existing))
        print(
            f"{OUTPUT_PATH.relative_to(REPO_ROOT)} is out of date. "
            "Run `python3 tools/gen_notices.py` to regenerate.",
            file=sys.stderr,
        )
        return 1

    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
