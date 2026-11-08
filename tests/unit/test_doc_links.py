# SPDX-License-Identifier: Apache-2.0
"""Every relative link in the repository's Markdown resolves to a real file and heading.

M0 acceptance requires README/FAQ links to resolve. This keeps them resolving.
External (http/https/mailto) links are not checked: tests must not use the network.
Git-ignored files (such as the local-only CLAUDE.md) are not scanned, and linking to one
fails, because it won't exist in the public repo or in CI.
"""

import re
import subprocess
from functools import cache
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_DIRS = {".git", ".venv", ".remember", ".mypy_cache", ".pytest_cache", ".ruff_cache"}

# [text](target) where target has no spaces; images included. Code spans are stripped first.
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
CODE_FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.MULTILINE | re.DOTALL)
CODE_SPAN_RE = re.compile(r"`[^`\n]*`")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


@cache
def _is_git_ignored(path: Path) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", str(path)],
        cwd=REPO_ROOT,
        check=False,
    )
    if result.returncode not in (0, 1):  # 0 = ignored, 1 = not ignored, else git failed
        raise RuntimeError(f"git check-ignore failed for {path}")
    return result.returncode == 0


def _markdown_files() -> list[Path]:
    return sorted(
        p
        for p in REPO_ROOT.rglob("*.md")
        if not EXCLUDED_DIRS.intersection(p.relative_to(REPO_ROOT).parts) and not _is_git_ignored(p)
    )


def _strip_code(text: str) -> str:
    return CODE_SPAN_RE.sub("", CODE_FENCE_RE.sub("", text))


def _github_anchor(heading: str) -> str:
    """Approximate GitHub's heading-anchor algorithm."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # links -> their text
    text = text.replace("`", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def _anchors(path: Path) -> set[str]:
    text = CODE_FENCE_RE.sub("", path.read_text(encoding="utf-8"))
    seen: dict[str, int] = {}
    anchors: set[str] = set()
    for heading in HEADING_RE.findall(text):
        slug = _github_anchor(heading)
        count = seen.get(slug, 0)
        anchors.add(slug if count == 0 else f"{slug}-{count}")
        seen[slug] = count + 1
    return anchors


def _relative_links(path: Path) -> list[str]:
    links = LINK_RE.findall(_strip_code(path.read_text(encoding="utf-8")))
    return [t for t in links if not re.match(r"^[a-z][a-z0-9+.-]*:", t, re.IGNORECASE)]


@pytest.mark.parametrize(
    "md_file", _markdown_files(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix()
)
def test_relative_links_resolve(md_file: Path) -> None:
    broken: list[str] = []
    for target in _relative_links(md_file):
        file_part, _, anchor = target.partition("#")
        resolved = (md_file.parent / file_part).resolve() if file_part else md_file
        if not resolved.exists():
            broken.append(f"{target} (missing file)")
        elif resolved.is_relative_to(REPO_ROOT) and _is_git_ignored(resolved):
            broken.append(f"{target} (git-ignored, so absent from the public repo)")
        elif anchor and resolved.suffix == ".md" and anchor not in _anchors(resolved):
            broken.append(f"{target} (missing heading #{anchor})")
    assert not broken, f"Broken links in {md_file.name}: {broken}"


def test_anchor_algorithm_matches_github_examples() -> None:
    assert _github_anchor("3.1 EvidenceRecord") == "31-evidencerecord"
    assert _github_anchor("9. Threat model of the tool itself (summary)") == (
        "9-threat-model-of-the-tool-itself-summary"
    )
    # Existing docs use an em dash (U+2014) in headings; GitHub drops it and keeps both spaces.
    em_dash = chr(0x2014)
    assert _github_anchor(f"M0 {em_dash} Repo hygiene") == "m0--repo-hygiene"
