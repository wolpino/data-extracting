#!/usr/bin/env python3
"""Generate small Buffy-themed fake chart PDFs under docs/testdata/ (no real PHI)."""

from pathlib import Path

OUT = Path(__file__).resolve().parent

FIXTURES = [
    (
        "buffy-summers-chart.pdf",
        "Sunnydale Clinic — Patient Chart",
        "Buffy",
        "Summers",
        "1981-01-19",
        "January 19, 1981",
        "Fake demo data for GenHealth take-home. Not real PHI.",
    ),
    (
        "willow-rosenberg-chart.pdf",
        "Sunnydale Clinic — Patient Chart",
        "Willow",
        "Rosenberg",
        "1981-05-01",
        "May 1, 1981",
        "Fake demo data for GenHealth take-home. Not real PHI.",
    ),
    (
        "xander-harris-chart.pdf",
        "Sunnydale Clinic — Patient Chart",
        "Alexander",
        "Harris",
        "1981-03-15",
        "March 15, 1981",
        "Goes by Xander. Fake demo data only.",
    ),
    (
        "spike-order-note.pdf",
        "DME Order Note",
        "William",
        "Pratt",
        "1970-06-06",
        "June 6, 1970",
        "Also known as Spike. Fake demo data only.",
    ),
]


def escape_pdf_text(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(path: Path, lines: list[str]) -> None:
    # Minimal one-page PDF — no third-party deps for fixture generation.
    y = 750
    content_ops = ["BT", "/F1 12 Tf", "14 TL"]
    first = True
    for line in lines:
        text = escape_pdf_text(line)
        if first:
            content_ops.append(f"50 {y} Td ({text}) Tj")
            first = False
        else:
            content_ops.append(f"T* ({text}) Tj")
    content_ops.append("ET")
    stream = "\n".join(content_ops).encode("latin-1", errors="replace")

    objects: list[bytes] = []
    objects.append(b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n")
    objects.append(b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n")
    objects.append(
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n"
    )
    objects.append(
        f"4 0 obj<< /Length {len(stream)} >>stream\n".encode()
        + stream
        + b"\nendstream\nendobj\n"
    )
    objects.append(
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
    )

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(out))
        out.extend(obj)
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(
        f"trailer<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n".encode()
    )
    path.write_bytes(out)


def main() -> None:
    for filename, title, first, last, dob_iso, dob_display, notes in FIXTURES:
        lines = [
            title,
            "",
            f"Patient First Name: {first}",
            f"Patient Last Name: {last}",
            f"Date of Birth: {dob_display}",
            f"DOB (ISO): {dob_iso}",
            "",
            notes,
        ]
        path = OUT / filename
        make_pdf(path, lines)
        print(f"wrote {path.name} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
