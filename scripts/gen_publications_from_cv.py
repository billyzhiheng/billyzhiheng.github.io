# -*- coding: utf-8 -*-
"""Extract B.2.x from CV (docx or txt) and write publications.html."""
from __future__ import annotations

import html
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CV_TXT = ROOT / "CV-Zhiheng Zhao .txt"
CV_DOCX = Path(
    os.environ.get(
        "CV_DOCX",
        r"c:\Users\user\OneDrive - The Hong Kong Polytechnic University\Polyu\Dr.Zhao\CV-Zhiheng Zhao .docx",
    )
)
CV_DOCX_FALLBACK = Path(os.environ.get("TEMP", ".")) / "CV-Zhiheng-Zhao.docx"

ENTRY_START = re.compile(r"^\d+\.\s+(?:[A-Za-z]|[\u2018'])")
NUM_ONLY = re.compile(r"^\d+\.$")
ENTRY_INLINE = re.compile(r"^\d+\.\s+")


def clean_cv_text(s: str) -> str:
    s = re.sub(r"===== PAGE \d+ =====", "", s)
    s = re.sub(r"Curriculum Vitae\s*\nIr\. Dr\.[^\n]+\n", "", s)
    s = re.sub(r"Updated on \d+ [A-Za-z]+ \d+\s*\d*", "", s)
    return s


def strip_entry_number(text: str) -> str:
    return ENTRY_INLINE.sub("", text, count=1).strip()


def merge_wrapped_lines(block: str) -> str:
    lines = block.splitlines()
    out: list[str] = []
    buf = ""
    for line in lines:
        line = line.rstrip()
        if not line.strip():
            continue
        if ENTRY_START.match(line) or NUM_ONLY.match(line):
            if buf:
                out.append(buf.strip())
            buf = line
        else:
            buf = (buf + " " + line.strip()) if buf else line
    if buf:
        out.append(buf.strip())
    return "\n".join(out)


def entries_from_numbered_block(block: str) -> list[str]:
    block = clean_cv_text(block)
    merged = merge_wrapped_lines(block)
    items: list[str] = []
    for line in merged.splitlines():
        line = line.strip()
        if not line:
            continue
        if ENTRY_START.match(line) or NUM_ONLY.match(line):
            items.append(strip_entry_number(line))
    return items


def section_between(text: str, start_pat: str, end_pat: str) -> str:
    m = re.search(start_pat, text, re.DOTALL)
    if not m:
        return ""
    start = m.start()
    rest = text[start:]
    m2 = re.search(end_pat, rest[50:], re.DOTALL)
    if not m2:
        return rest
    return rest[: 50 + m2.start()]


def read_docx_paragraphs(docx: Path) -> list[str]:
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(docx) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    paras: list[str] = []
    for p in root.iter(f"{w}p"):
        t = "".join(n.text or "" for n in p.iter(f"{w}t")).strip().replace("\xa0", " ")
        if t:
            paras.append(t)
    return paras


def section_bounds(
    paras: list[str], start_kw: str, end_kw: str, *, min_index: int = 0
) -> tuple[int, int]:
    starts = [i for i, p in enumerate(paras) if start_kw in p and i >= min_index]
    if not starts:
        raise ValueError(f"Section not found: {start_kw!r} (min_index={min_index})")
    start = starts[0]
    ends = [i for i, p in enumerate(paras) if end_kw in p and i > start]
    end = ends[0] if ends else len(paras)
    return start, end


def parse_numbered_section(paras: list[str], start: int, end: int) -> list[str]:
    items: list[str] = []
    buf: str | None = None
    for p in paras[start + 1 : end]:
        if NUM_ONLY.match(p):
            if buf:
                items.append(strip_entry_number(buf))
            buf = p
        elif ENTRY_INLINE.match(p):
            if buf:
                items.append(strip_entry_number(buf))
            buf = p
        else:
            if buf is None:
                continue
            buf = buf + " " + p
    if buf:
        items.append(strip_entry_number(buf))
    return items


def parse_plain_section(paras: list[str], start: int, end: int) -> list[str]:
    items: list[str] = []
    for p in paras[start + 1 : end]:
        if not p.strip():
            continue
        if p.startswith("B.") or p.startswith("C ") or p.startswith("DETAILS"):
            break
        items.append(p.strip())
    return items


def load_sections_from_docx(docx: Path) -> dict[str, list[str]]:
    paras = read_docx_paragraphs(docx)
    b2_min = 0
    for i, p in enumerate(paras):
        if "RESEARCH OUTPUTS" in p:
            b2_min = i
            break
    specs = [
        ("e1", "Refereed journal papers – listed as first or corresponding author", "Refereed journal papers – listed as co-author", "numbered"),
        ("e2", "Refereed journal papers – listed as co-author", "Conference papers", "numbered"),
        ("e3", "Conference papers", "Patents (Invention)", "numbered"),
        ("e4", "Patents (Invention)", "Patents (Utility model)", "plain"),
        ("e5", "Patents (Utility model)", "Software Copyrights", "plain"),
        ("e6", "Software Copyrights", "DETAILS OF TEACHING", "plain"),
    ]
    out: dict[str, list[str]] = {}
    cursor = b2_min
    for key, start_kw, end_kw, kind in specs:
        s, e = section_bounds(paras, start_kw, end_kw, min_index=cursor)
        cursor = e
        if kind == "numbered":
            out[key] = parse_numbered_section(paras, s, e)
        else:
            out[key] = parse_plain_section(paras, s, e)
    return out


def load_sections_from_txt() -> dict[str, list[str]]:
    full = CV_TXT.read_text(encoding="utf-8")
    blocks = [
        ("e1", r"B\.2\.1\.\s*Refereed journal papers – listed as first or corresponding author:\s*", r"B\.2\.2\.\s*Refereed journal papers – listed as co-author:"),
        ("e2", r"B\.2\.2\.\s*Refereed journal papers – listed as co-author:\s*", r"B\.2\.3\.\s*Conference papers:"),
        ("e3", r"B\.2\.3\.\s*Conference papers:\s*", r"B\.2\.4\.\s*Patents \(Invention\)"),
        ("e4", r"B\.2\.4\.\s*Patents \(Invention\)\s*", r"B\.2\.5\.\s*Patents \(Utility model\)"),
        ("e5", r"B\.2\.5\.\s*Patents \(Utility model\)\s*", r"B\.2\.6\.\s*Software Copyrights"),
        ("e6", r"B\.2\.6\.\s*Software Copyrights\s*", r"C DETAILS OF TEACHING"),
    ]
    out: dict[str, list[str]] = {}
    for key, start_pat, end_pat in blocks:
        block = section_between(full, start_pat, end_pat)
        out[key] = entries_from_numbered_block(block) if key != "e6" else entries_from_numbered_block(block)
    # Patents in txt may lack numbers; fall back to line-based if empty
    for key in ("e4", "e5", "e6"):
        if not out[key]:
            block = section_between(full, blocks[["e1", "e2", "e3", "e4", "e5", "e6"].index(key)][1], blocks[["e1", "e2", "e3", "e4", "e5", "e6"].index(key)][2])
            lines = [ln.strip() for ln in clean_cv_text(block).splitlines() if ln.strip() and not ln.startswith("B.2")]
            out[key] = lines
    return out


def resolve_docx() -> Path | None:
    for path in (CV_DOCX, CV_DOCX_FALLBACK):
        if path.is_file():
            try:
                read_docx_paragraphs(path)
                return path
            except (OSError, zipfile.BadZipFile, KeyError):
                continue
    return None


def to_li(text: str) -> str:
    return "          <li>" + html.escape(text) + "</li>"


HEADER = """<!DOCTYPE html>
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

FOOTER = """        </ul>
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


def build_html(sections: dict[str, list[str]]) -> str:
    e1, e2, e3, e4, e5, e6 = (sections[k] for k in ("e1", "e2", "e3", "e4", "e5", "e6"))
    parts = [HEADER]
    parts.append("\n".join(to_li(x) for x in e1) + "\n")
    parts.append(
        """        </ul>
        <h3><span class="mw-headline">Refereed journal papers &mdash; listed as co-author</span></h3>
        <ul class="entry-list">
"""
    )
    parts.append("\n".join(to_li(x) for x in e2) + "\n")
    parts.append(
        """        </ul>
      </section>

      <section id="conf">
        <h2><span class="mw-headline">Conference papers</span></h2>
        <ul class="entry-list">
"""
    )
    parts.append("\n".join(to_li(x) for x in e3) + "\n")
    parts.append(
        """        </ul>
      </section>

      <section id="patents">
        <h2><span class="mw-headline">Patents &amp; software</span></h2>
        <h3><span class="mw-headline">Patents (Invention)</span></h3>
        <ul class="entry-list">
"""
    )
    parts.append("\n".join(to_li(x) for x in e4) + "\n")
    parts.append(
        """        </ul>
        <h3><span class="mw-headline">Patents (Utility model)</span></h3>
        <ul class="entry-list">
"""
    )
    parts.append("\n".join(to_li(x) for x in e5) + "\n")
    parts.append(
        """        </ul>
        <h3><span class="mw-headline">Software Copyrights</span></h3>
        <ul class="entry-list">
"""
    )
    parts.append("\n".join(to_li(x) for x in e6) + "\n")
    parts.append(FOOTER)
    return "".join(parts)


def main() -> None:
    docx = resolve_docx()
    if docx:
        sections = load_sections_from_docx(docx)
        source = f"docx:{docx}"
    else:
        sections = load_sections_from_txt()
        source = f"txt:{CV_TXT}"

    out_path = ROOT / "publications.html"
    out_path.write_text(build_html(sections), encoding="utf-8", newline="\n")
    counts = tuple(len(sections[k]) for k in ("e1", "e2", "e3", "e4", "e5", "e6"))
    print(f"Wrote {out_path} from {source}")
    print("counts (first, co, conf, inv, util, soft):", counts)


if __name__ == "__main__":
    main()
