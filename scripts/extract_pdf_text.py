from pathlib import Path
import sys

import pdfplumber


def main() -> None:
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    target.parent.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(source) as pdf:
        pages = []
        for number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
            pages.append(f"\n===== PAGE {number} =====\n{text}")
    target.write_text("\n".join(pages), encoding="utf-8")


if __name__ == "__main__":
    main()
