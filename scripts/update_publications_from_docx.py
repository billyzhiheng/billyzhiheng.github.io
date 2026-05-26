# -*- coding: utf-8 -*-
"""Update publications.html list sections from CV docx B.2 RESEARCH OUTPUTS."""
from __future__ import annotations

import html
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "CV-Zhiheng Zhao .docx"
DOCX_ONEDRIVE = Path(
    r"c:\Users\user\OneDrive - The Hong Kong Polytechnic University\Polyu\Dr.Zhao\CV-Zhiheng Zhao .docx"
)
PUB_HTML = ROOT / "publications.html"

ENTRY_NUM = re.compile(r"(?:^|(?<=[\s]))(\d+)\.([A-Za-z\u2018'])")
PATENT_ENTRY = re.compile(
    r"(?=(?:Zhiheng Zhao|Guoquan Huang|Ji Fang, Guoquan|Ming Li, Zhiheng|'\w))"
)
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def read_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    parts: list[str] = []
    for t in root.iter(f"{W_NS}t"):
        if t.text:
            parts.append(t.text)
        if t.tail:
            parts.append(t.tail)
    return "".join(parts)


def clean_cv_text(s: str) -> str:
    s = re.sub(r"Updated on \d+ [A-Za-z]+ \d+\s*\d*", "", s)
    return s


def entries_from_numbered_block(block: str) -> list[str]:
    block = clean_cv_text(block).strip()
    if not block:
        return []
    if ":" in block[:120]:
        block = re.sub(r"^[^:]+:\s*", "", block, count=1)
    parts = re.findall(r"\d{1,2}\.[A-Z].*?(?=\d{1,2}\.[A-Z]|$)", block, re.DOTALL)
    items: list[str] = []
    for part in parts:
        part = part.strip()
        if not part or len(part) < 40:
            continue
        part = re.sub(r"^\d+\.", "", part, count=1).strip()
        if part:
            items.append(part)
    return items


def entries_from_invention_patents(block: str) -> list[str]:
    block = clean_cv_text(block).strip()
    block = re.sub(r"^Patents \([^)]+\)", "", block).strip()
    if not block:
        return []
    parts = re.findall(r"Zhiheng Zhao,.*?(?=Zhiheng Zhao,|$)", block, re.DOTALL)
    return [p.strip() for p in parts if p.strip()]


def entries_from_utility_patents(block: str) -> list[str]:
    block = clean_cv_text(block).strip()
    block = re.sub(r"^Patents \([^)]+\)", "", block).strip()
    if not block:
        return []
    chunks = re.split(r"(?=(?:Ji Fang, Guoquan|Ming Li, Zhiheng))", block)
    return [c.strip() for c in chunks if c.strip() and len(c.strip()) > 15]


def entries_from_software_block(block: str) -> list[str]:
    block = clean_cv_text(block).strip()
    if not block:
        return []
    chunks = re.split(r"(?<=\d)\.(?=[\u2018\u2019'])", block)
    return [c.strip() for c in chunks if c.strip()]


def section_between(text: str, start_pat: str, end_pat: str) -> str:
    m = re.search(start_pat, text, re.DOTALL)
    if not m:
        return ""
    rest = text[m.start() :]
    m2 = re.search(end_pat, rest[30:], re.DOTALL)
    if not m2:
        return rest
    return rest[: 30 + m2.start()]


def to_li(text: str) -> str:
    return "          <li>" + html.escape(text) + "</li>"


def build_lists(full: str) -> dict[str, str]:
    s1 = section_between(
        full,
        r"Refereed journal papers . listed as first or corresponding author:\s*",
        r"Refereed journal papers . listed as co-author:",
    )
    s2 = section_between(
        full,
        r"Refereed journal papers . listed as co-author:\s*",
        r"Conference papers:\s*",
    )
    s3 = section_between(
        full,
        r"Conference papers:\s*",
        r"Patents \(Invention\)",
    )
    s4 = section_between(
        full,
        r"Patents \(Invention\)\s*",
        r"Patents \(Utility model\)",
    )
    s5 = section_between(
        full,
        r"Patents \(Utility model\)\s*",
        r"Software Copyrights",
    )
    m_sw = re.search(
        r"Patents \(Utility model\).*?Software Copyrights[\s\u2018\u2019']*"
        r"([\u2018\u2019'].+?)(?:DETAILS OF TEACHING|\.DETAILS OF TEACHING)",
        full,
        re.DOTALL,
    )
    s6 = m_sw.group(1) if m_sw else ""
    e1 = entries_from_numbered_block(s1)
    e2 = entries_from_numbered_block(s2)
    e3 = entries_from_numbered_block(s3)
    e4 = entries_from_invention_patents(s4)
    e5 = entries_from_utility_patents(s5)
    e6 = entries_from_software_block(s6)
    return {
        "journal_first": "\n".join(to_li(x) for x in e1),
        "journal_co": "\n".join(to_li(x) for x in e2),
        "conf": "\n".join(to_li(x) for x in e3),
        "patent_inv": "\n".join(to_li(x) for x in e4),
        "patent_util": "\n".join(to_li(x) for x in e5),
        "software": "\n".join(to_li(x) for x in e6),
        "counts": (len(e1), len(e2), len(e3), len(e4), len(e5), len(e6)),
    }


PAGE_SHELL_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Publications -PolyU Matrix</title>
  <link rel="stylesheet" href="css/wiki-team.css" />
</head>
<body>
  <div class="layout-wrap">
    <aside class="sidebar" aria-label="Site navigation">
      <div class="brand">Zhiheng Zhao</div>
      <nav>
        <div class="nav-group">
          <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="members.html">Members</a></li>
          </ul>
        </div>
        <div class="nav-group"><ul>
            <li><a href="project.html">Projects</a></li>
            <li>
              <details class="sidebar-details" open>
                <summary class="sidebar-details__summary"><a href="publications.html" aria-current="page">Publications</a></summary>
                <ul class="sidebar-subnav">
                  <li><a href="publications.html#journal">Journal papers</a></li>
                  <li><a href="publications.html#conf">Conference papers</a></li>
                  <li><a href="publications.html#patents">Patents &amp; software</a></li>
                </ul>
              </details>
            </li>
          </ul>
        </div>
        <div class="nav-group"><ul>
            <li><a href="teaching.html">Teaching</a></li>
          </ul>
        </div>
        <div class="nav-group"><ul>
            <li><a href="services.html">Services &amp; Awards</a></li>
          </ul>
        </div>
      </nav>
    </aside>
    <main class="main mw-body mw-body--publications">
      <h1 class="page-title">Publications</h1>

      <section id="journal">
        <h2><span class="mw-headline">Journal papers</span></h2>
        <h3><span class="mw-headline">Refereed journal papers &mdash; listed as first or corresponding author</span></h3>
        <ul class="entry-list">
"""

PAGE_SHELL_TAIL = """        </ul>
      </section>

      <p class="lead">For the complete list and citation metrics, visit <a href="https://scholar.google.com/citations?hl=zh-CN&amp;user=AwDLDGkAAAAJ" rel="noopener noreferrer" target="_blank">Google Scholar</a>.</p>
      <p><a href="index.html">← Home</a></p>
    </main>
    <aside class="right-rail" aria-label="Appearance">
      <div class="right-rail-header">Appearance</div>
      <div class="right-rail-title">Languages</div>
      <div class="right-rail-section">
        <label class="right-rail-option right-rail-option--current">
          <input type="radio" name="lang" checked disabled>
          <span>English</span>
        </label>
        <label class="right-rail-option">
          <input type="radio" name="lang" disabled>
          <a href="index.zh.html" lang="zh">中文</a>
        </label>
      </div>
      <div class="right-rail-title">Color</div>
      <div class="right-rail-section">
        <label class="right-rail-option">
          <input type="radio" name="color" value="light">
          <span>Light</span>
        </label>
        <label class="right-rail-option">
          <input type="radio" name="color" value="dark">
          <span>Dark</span>
        </label>
      </div>
    </aside>
  </div>
  <script src="js/theme.js"></script>
</body>
</html>
"""


def render_publications_page(lists: dict[str, str]) -> str:
    return (
        PAGE_SHELL_HEAD
        + lists["journal_first"]
        + "\n        </ul>\n        <h3><span class=\"mw-headline\">Refereed journal papers &mdash; listed as co-author</span></h3>\n        <ul class=\"entry-list\">\n"
        + lists["journal_co"]
        + "\n        </ul>\n      </section>\n\n      <section id=\"conf\">\n        <h2><span class=\"mw-headline\">Conference papers</span></h2>\n        <ul class=\"entry-list\">\n"
        + lists["conf"]
        + "\n        </ul>\n      </section>\n\n      <section id=\"patents\">\n        <h2><span class=\"mw-headline\">Patents &amp; software</span></h2>\n        <h3><span class=\"mw-headline\">Patents (Invention)</span></h3>\n        <ul class=\"entry-list\">\n"
        + lists["patent_inv"]
        + "\n        </ul>\n        <h3><span class=\"mw-headline\">Patents (Utility model)</span></h3>\n        <ul class=\"entry-list\">\n"
        + lists["patent_util"]
        + "\n        </ul>\n        <h3><span class=\"mw-headline\">Software Copyrights</span></h3>\n        <ul class=\"entry-list\">\n"
        + lists["software"]
        + "\n"
        + PAGE_SHELL_TAIL
    )


def resolve_docx() -> Path:
    if DOCX.is_file():
        return DOCX
    if DOCX_ONEDRIVE.is_file():
        return DOCX_ONEDRIVE
    raise SystemExit(f"CV docx not found: {DOCX} or {DOCX_ONEDRIVE}")


def main() -> None:
    docx_path = resolve_docx()
    full = read_docx_text(docx_path)
    lists = build_lists(full)
    c1, c2, c3, c4, c5, c6 = lists["counts"]
    print("Counts:", c1, c2, c3, c4, c5, c6)

    page = render_publications_page(lists)
    PUB_HTML.write_text(page, encoding="utf-8", newline="\n")
    print("Updated", PUB_HTML, "journal", c1 + c2, "conf", c3)


if __name__ == "__main__":
    main()
