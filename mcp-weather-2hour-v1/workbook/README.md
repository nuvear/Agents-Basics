# Student workbook

Author: **Rajkumar Rajagobalan**. Draft v1.0, 10 September 2026.

- [Markdown workbook](MCP_Colab_Student_Workbook.md)
- [PDF workbook](../../output/pdf/MCP_Colab_Student_Workbook.pdf)

Use alongside the published Colab notebook. The workbook includes preparation, 38 numbered steps, expected outputs, evidence tables, reflection space, failure diagnosis and an exit ticket. It retains the 120-minute class schedule and identifies live integration checks that remain pending.

## Rebuild the PDF

The Markdown file is the content source. The PDF builder uses explicit page breaks from the Markdown and retains clickable links. Install ReportLab in a separate document-building environment and make DejaVu Sans, DejaVu Sans Bold and DejaVu Sans Mono available.

From the repository root:

```bash
python -m pip install reportlab
WORKBOOK_FONT_DIR=/path/to/dejavu/fonts python scripts/build_workbook_pdf.py
```

On Linux, the builder defaults to `/usr/share/fonts/truetype/dejavu`. On other platforms, set `WORKBOOK_FONT_DIR` to the directory containing those font files. The generated PDF is written to `output/pdf/MCP_Colab_Student_Workbook.pdf`. Re-render and visually inspect the PDF after content or layout edits.
