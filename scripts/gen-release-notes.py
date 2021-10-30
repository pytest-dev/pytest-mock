"""
Generates the release notes for the latest release, in Markdown.

Convert CHANGELOG.rst to Markdown, and extracts just the latest release.

Writes to ``scripts/latest-release-notes.md``, which can be
used with https://github.com/softprops/action-gh-release.
"""
from pathlib import Path

import pypandoc

this_dir = Path(__file__).parent
rst_text = (this_dir.parent / "CHANGELOG.rst").read_text(encoding="UTF-8")
md_text = pypandoc.convert_text(
    rst_text, "md", format="rst", extra_args=["--wrap=preserve"]
)

output_lines = []
first_heading_found = False
for line in md_text.splitlines():
    if line.startswith("# "):
        if first_heading_found:
            break
        first_heading_found = True
    else:
        output_lines.append(line)

output_fn = this_dir / "latest-release-notes.md"
output_fn.write_text("\n".join(output_lines), encoding="UTF-8")
print(output_fn, "generated.")
