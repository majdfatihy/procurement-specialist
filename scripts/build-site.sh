#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
BROWSER="$(command -v google-chrome || command -v google-chrome-stable || command -v chromium || true)"
if [ -z "$BROWSER" ]; then echo "Chrome/Chromium is required to generate the direct-download CV PDFs" >&2; exit 1; fi
mkdir -p _site/en _site/assets/js
cp index.html cv-ats.html _site/
cp en/index.html _site/en/index.html
cp assets/majd-fatihy-procurement-specialist.jpg _site/assets/
cp assets/js/cv-language.js _site/assets/js/
touch _site/.nojekyll
make_pdf() {
  local html="$1" output="$2"
  "$BROWSER" --headless --no-sandbox --disable-gpu --disable-dev-shm-usage --no-pdf-header-footer --print-to-pdf="$ROOT/_site/$output" "file://$ROOT/$html" >/dev/null 2>&1
  test -s "_site/$output" || { echo "Unable to render PDF: $output" >&2; exit 1; }
}
make_pdf index.html majd-fatihy-cv-ar.pdf
make_pdf cv-ats.html majd-fatihy-cv-ats.pdf
make_pdf en/index.html majd-fatihy-cv-en.pdf
python3 - <<'PY'
from pathlib import Path
import re
expected = {
 "majd-fatihy-cv-ar.pdf": (2, 2),
 "majd-fatihy-cv-ats.pdf": (1, 1),
 "majd-fatihy-cv-en.pdf": (1, 3),
}
for name,(low,high) in expected.items():
    path=Path("_site")/name
    data=path.read_bytes()
    assert data.startswith(b"%PDF-"),f"{name} is not PDF"
    count=len(re.findall(rb"/Type\s*/Page\b",data))
    print(f"{name}: {count} pages; {len(data)} bytes")
    assert low <= count <= high,f"{name} has unexpected {count} pages"
for name in ("index.html","cv-ats.html","en/index.html","assets/majd-fatihy-procurement-specialist.jpg","assets/js/cv-language.js"):
    assert (Path("_site")/name).exists(),name
print("PASS: ready-to-download Arabic, ATS and English CV PDFs + both language pages")
PY
