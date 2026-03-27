# -*- coding: utf-8 -*-
"""Extract B.2.x from CV-Zhiheng Zhao .txt and write publications.html."""
import html
import re

ENTRY_START = re.compile(r"^\d+\.\s+(?:[A-Za-z]|[\u2018'])")

def clean_cv_text(s: str) -> str:
    s = re.sub(r"===== PAGE \d+ =====", "", s)
    s = re.sub(r"Curriculum Vitae\s*\nIr\. Dr\.[^\n]+\n", "", s)
    s = re.sub(r"Updated on \d+ [A-Za-z]+ \d+\s*\d*", "", s)
    return s

def merge_wrapped_lines(block: str) -> str:
    lines = block.splitlines()
    out = []
    buf = ""
    for line in lines:
        line = line.rstrip()
        if not line.strip():
            continue
        if ENTRY_START.match(line):
            if buf:
                out.append(buf.strip())
            buf = line
        else:
            if buf:
                buf = buf + " " + line.strip()
            else:
                buf = line
    if buf:
        out.append(buf.strip())
    return "\n".join(out)

def entries_from_numbered_block(block: str) -> list[str]:
    block = clean_cv_text(block)
    merged = merge_wrapped_lines(block)
    items = []
    for line in merged.splitlines():
        line = line.strip()
        if not line:
            continue
        if ENTRY_START.match(line):
            items.append(line)
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

def to_li(text: str) -> str:
    return "          <li>" + html.escape(text) + "</li>"

HEADER = r"""<!DOCTYPE html>
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
        <div class="nav-group">
          <div class="nav-group-title">Research</div>
          <ul>
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
        <div class="nav-group">
          <div class="nav-group-title">Experience</div>
          <ul>
            <li><a href="teaching.html">Teaching</a></li>
          </ul>
        </div>
        <div class="nav-group">
          <div class="nav-group-title">Professional Activities</div>
          <ul>
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

FOOTER = r"""        </ul>
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


def main():
    with open("CV-Zhiheng Zhao .txt", encoding="utf-8") as f:
        full = f.read()

    s1 = section_between(
        full,
        r"B\.2\.1\.\s*Refereed journal papers – listed as first or corresponding author:\s*",
        r"B\.2\.2\.\s*Refereed journal papers – listed as co-author:",
    )
    e1 = entries_from_numbered_block(s1)

    s2 = section_between(
        full,
        r"B\.2\.2\.\s*Refereed journal papers – listed as co-author:\s*",
        r"B\.2\.3\.\s*Conference papers:",
    )
    e2 = entries_from_numbered_block(s2)

    s3 = section_between(
        full,
        r"B\.2\.3\.\s*Conference papers:\s*",
        r"B\.2\.4\.\s*Patents \(Invention\)",
    )
    e3 = entries_from_numbered_block(s3)

    s4 = section_between(
        full,
        r"B\.2\.4\.\s*Patents \(Invention\)\s*",
        r"B\.2\.5\.\s*Patents \(Utility model\)",
    )
    e4 = entries_from_numbered_block(s4)

    s5 = section_between(
        full,
        r"B\.2\.5\.\s*Patents \(Utility model\)\s*",
        r"B\.2\.6\.\s*Software Copyrights",
    )
    e5 = entries_from_numbered_block(s5)

    s6 = section_between(
        full,
        r"B\.2\.6\.\s*Software Copyrights\s*",
        r"C DETAILS OF TEACHING",
    )
    e6 = entries_from_numbered_block(s6)

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

    out = "".join(parts)
    with open("publications.html", "w", encoding="utf-8", newline="\n") as f:
        f.write(out)

    print("Wrote publications.html", "counts", len(e1), len(e2), len(e3), len(e4), len(e5), len(e6))


if __name__ == "__main__":
    main()
