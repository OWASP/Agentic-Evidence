# SPDX-License-Identifier: Apache-2.0
"""Every relative link in the repository's Markdown resolves to a real file and heading.

M0 acceptance requires README/FAQ links to resolve. This keeps them resolving.
External (http/https/mailto) links are not checked: tests must not use the network.
Git-ignored files (such as the local-only CLAUDE.md) are not scanned, and linking to one
fails, because it won't exist in the public repo or in CI.

Checked: inline links and images (with or without a title, bare or <angle> destinations),
and reference definitions ([label]: target), which covers full, collapsed and shortcut
references. Link syntax this module can't parse fails the test instead of being skipped,
as does a full or collapsed reference whose label has no definition.
Not checked: links in raw HTML (<a href>, <img src>), and shortcut references ([label]) with
no definition, which can't be told apart from ordinary bracketed text.
"""

import re
import subprocess
from functools import cache
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_DIRS = {".git", ".venv", ".remember", ".mypy_cache", ".pytest_cache", ".ruff_cache"}

# Link syntax is matched after code spans and fences are stripped. Link text excludes
# brackets so that nested links (a badge image inside a link) match innermost first.
_TITLE = r"""(?:\s+(?:"[^"]*"|'[^']*'|\([^()]*\)))?"""
# [text](target), [text](target "title"), [text](<target with spaces>); images included.
INLINE_LINK_RE = re.compile(
    r"!?\[[^\[\]]*\]\(\s*(?:<(?P<angle>[^<>\n]*)>|(?P<bare>[^\s()<>]+))" + _TITLE + r"\s*\)"
)
# [text][label] and the collapsed form [label][]; images included.
REFERENCE_LINK_RE = re.compile(r"!?\[(?P<text>[^\[\]]*)\]\[(?P<label>[^\[\]]*)\]")
# [label]: target, optionally on the next line. Labels starting with ^ are GFM footnotes.
REFERENCE_DEF_RE = re.compile(
    r"^[ \t>]*\[(?P<label>[^\]\^\n][^\]\n]*)\]:[ \t]*(?:\n[ \t>]*)?"
    r"(?:<(?P<angle>[^<>\n]*)>|(?P<bare>[^<\s]\S*))",
    re.MULTILINE,
)
URI_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
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


def _normalize_label(label: str) -> str:
    """Reference labels match case-insensitively with internal whitespace collapsed."""
    return " ".join(label.split()).casefold()


def _destination(match: re.Match[str]) -> str:
    angle = match.group("angle")
    return angle if angle is not None else match.group("bare")


def _parse_links(text: str) -> tuple[list[str], list[str]]:
    """Return (link targets, syntax problems) for Markdown text with code already stripped."""
    targets: list[str] = []
    definitions: set[str] = set()
    used_labels: list[str] = []

    def take_definition(match: re.Match[str]) -> str:
        definitions.add(_normalize_label(match.group("label")))
        targets.append(_destination(match))
        return ""

    def take_inline(match: re.Match[str]) -> str:
        targets.append(_destination(match))
        return "link"

    def take_reference(match: re.Match[str]) -> str:
        used_labels.append(match.group("label") or match.group("text"))
        return "link"

    text = REFERENCE_DEF_RE.sub(take_definition, text)
    # Replace links with plain text until none remain, so an outer link around an image
    # becomes matchable once the image is gone. Each pass removes at least one "](" or "][".
    while True:
        text, inline_count = INLINE_LINK_RE.subn(take_inline, text)
        text, reference_count = REFERENCE_LINK_RE.subn(take_reference, text)
        if inline_count == reference_count == 0:
            break

    problems = [
        f"[{label}] (undefined reference label)"
        for label in used_labels
        if _normalize_label(label) not in definitions
    ]
    problems += [
        f"{line.strip()} (unparsed inline link)" for line in text.splitlines() if "](" in line
    ]
    return targets, problems


def _read_without_code(path: Path) -> str:
    return _strip_code(path.read_text(encoding="utf-8"))


def _relative_links(path: Path) -> list[str]:
    targets, _ = _parse_links(_read_without_code(path))
    return [t for t in targets if not URI_SCHEME_RE.match(t)]


def _link_syntax_problems(path: Path) -> list[str]:
    _, problems = _parse_links(_read_without_code(path))
    return problems


@pytest.mark.parametrize(
    "md_file", _markdown_files(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix()
)
def test_relative_links_resolve(md_file: Path) -> None:
    broken = _link_syntax_problems(md_file)
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


def _write_markdown(tmp_path: Path, text: str) -> Path:
    md_file = tmp_path / "doc.md"
    md_file.write_text(text, encoding="utf-8")
    return md_file


# Regression tests for issue #12: these link forms used to be skipped, so a broken target
# in any of them passed the repository-wide link check.
@pytest.mark.parametrize(
    ("markdown", "expected_target"),
    [
        ("[a](plain.md)", "plain.md"),
        ('[a](double-title.md "Title")', "double-title.md"),
        ("[a](single-title.md 'Title')", "single-title.md"),
        ("[a](paren-title.md (Title))", "paren-title.md"),
        ("[a](<angle target.md>)", "angle target.md"),
        ('[a](<angle-titled.md> "Title")', "angle-titled.md"),
        ("[a][ref]\n\n[ref]: full-reference.md", "full-reference.md"),
        ("[ref][]\n\n[ref]: collapsed-reference.md", "collapsed-reference.md"),
        ("[ref]\n\n[ref]: shortcut-reference.md", "shortcut-reference.md"),
        ('[a][ref]\n\n[ref]: <angle reference.md> "Title"', "angle reference.md"),
        ("[a][ref]\n\n[ref]:\n  next-line-reference.md", "next-line-reference.md"),
        ("[a][ref]\n\n   [ref]: indented-reference.md", "indented-reference.md"),
        ("![img][logo]\n\n[logo]: image-reference.png", "image-reference.png"),
        ("[![badge](badge.svg)](outer.md)", "badge.svg"),
        ("[![badge](badge.svg)](outer.md)", "outer.md"),
    ],
    ids=[
        "inline",
        "double-quoted-title",
        "single-quoted-title",
        "parenthesized-title",
        "angle-destination",
        "angle-destination-with-title",
        "full-reference",
        "collapsed-reference",
        "shortcut-reference",
        "reference-angle-with-title",
        "reference-destination-on-next-line",
        "indented-reference-definition",
        "image-reference",
        "nested-image-inner",
        "nested-image-outer",
    ],
)
def test_relative_links_extracts_every_link_form(
    tmp_path: Path, markdown: str, expected_target: str
) -> None:
    assert expected_target in _relative_links(_write_markdown(tmp_path, markdown))


@pytest.mark.parametrize(
    "markdown",
    [
        "[a](https://example.com/page)",
        "[a][ref]\n\n[ref]: https://example.com/page",
        "[^1]: Footnote text, not a link target.",
        "`[a](in-code-span.md)`",
        "```\n[a](in-fence.md)\n[ref]: in-fence.md\n```",
    ],
    ids=["external-inline", "external-reference", "footnote", "code-span", "code-fence"],
)
def test_relative_links_ignores_non_relative_targets(tmp_path: Path, markdown: str) -> None:
    assert _relative_links(_write_markdown(tmp_path, markdown)) == []


def test_reference_labels_match_case_and_whitespace_insensitively(tmp_path: Path) -> None:
    md_file = _write_markdown(tmp_path, "[a][My  Ref]\n\n[my ref]: target.md")
    assert _relative_links(md_file) == ["target.md"]
    assert _link_syntax_problems(md_file) == []


@pytest.mark.parametrize(
    ("markdown", "expected_problem"),
    [
        ("[a][missing]", "undefined reference label"),
        ("[missing][]", "undefined reference label"),
        ("[a](target with spaces.md)", "unparsed inline link"),
        ("[a]()", "unparsed inline link"),
    ],
    ids=["full-undefined", "collapsed-undefined", "unbracketed-space", "empty-destination"],
)
def test_link_syntax_problems_are_reported(
    tmp_path: Path, markdown: str, expected_problem: str
) -> None:
    problems = _link_syntax_problems(_write_markdown(tmp_path, markdown))
    assert len(problems) == 1
    assert expected_problem in problems[0]


def test_link_syntax_problems_ignores_plain_brackets(tmp_path: Path) -> None:
    text = "- [ ] task\n- [x] done\n\nSee [1] and [ADR-0003].\n\n[ref]: used-nowhere.md\n"
    assert _link_syntax_problems(_write_markdown(tmp_path, text)) == []
