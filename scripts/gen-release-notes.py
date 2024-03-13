"""
Generates the release notes for the latest release, in Markdown.

1. Extracts the latest release from the CHANGELOG.rst file.
2. Converts it to Markdown using pypandoc.
3. Writes to ``scripts/latest-release-notes.md``, which can be
   used with https://github.com/softprops/action-gh-release.
"""

from pathlib import Path

import pypandoc

this_dir = Path(__file__).parent
rst_text = (this_dir.parent / "CHANGELOG.rst").read_text(encoding="UTF-8")

output_lines = []
capture = False
for line in rst_text.splitlines():
    # Only start capturing after the latest release section.
    if line.startswith("-------"):
        capture = not capture
        if not capture:
            # We only need to capture the latest release, so stop.
            break
        continue

    if capture:
        output_lines.append(line)

# Drop last line, as it contains the previous release section title.
del output_lines[-1]

trimmed_rst = "\n".join(output_lines).strip()
print(">>Trimmed RST follows:")
print(trimmed_rst)
print(">>Trimmed RST ends")

md_text = pypandoc.convert_text(
    trimmed_rst, "md", format="rst", extra_args=["--wrap=preserve"]
)
print(">>Converted Markdown follows:")
print(md_text)
print(">>Converted Markdown ends")

output_fn = this_dir / "latest-release-notes.md"
output_fn.write_text(md_text, encoding="UTF-8")
print(output_fn, "generated.")
