#!/usr/bin/env bash
# test-hedit.sh — verify an SVG loads through hedit's real loadSVGText() path
# in headless Chrome, and report object/tag counts, viewBox, and bbox.
#
# Usage:   ./test-hedit.sh [file.svg]   (defaults to strings.svg)
#
# Uses --password-store=basic so Chrome never prompts for the login keyring.
set -euo pipefail

cd "$(dirname "$0")"

SVG="${1:-strings.svg}"
HEDIT="hedit.html"
HARNESS="._test_harness.html"

[ -f "$HEDIT" ] || { echo "error: $HEDIT not found" >&2; exit 1; }
[ -f "$SVG" ]   || { echo "error: SVG '$SVG' not found" >&2; exit 1; }

# Find a Chrome/Chromium binary.
CHROME=""
for c in google-chrome-stable google-chrome chromium chromium-browser; do
  if command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
done
[ -n "$CHROME" ] || { echo "error: no Chrome/Chromium binary found" >&2; exit 1; }

cleanup(){ rm -f "$HARNESS"; }
trap cleanup EXIT

# Build a harness: hedit.html + a separate <script> that inlines the SVG text,
# feeds it to loadSVGText(), and writes the result into <title>.
# A separate script block means a boot-time exception in hedit can't abort the test.
node -e '
  const fs = require("fs");
  const [hedit, svgPath, harness] = process.argv.slice(1);
  let h = fs.readFileSync(hedit, "utf8");
  const svg = fs.readFileSync(svgPath, "utf8");
  const name = svgPath.split("/").pop();
  const inject = `
<script>
window.addEventListener("load", () => {
  let r = "";
  try {
    const txt = ${JSON.stringify(svg)};
    loadSVGText(txt, ${JSON.stringify(name)});
    const n = contentGroup.children.length;
    const tags = {};
    [...contentGroup.querySelectorAll("*")].forEach(e => {
      const t = e.tagName.toLowerCase(); tags[t] = (tags[t] || 0) + 1;
    });
    let bb = null; try { bb = contentGroup.getBBox(); } catch (e) {}
    r = "TEST_OK|top=" + n
      + "|status=" + elStatus.textContent
      + "|vb=" + stage.getAttribute("viewBox")
      + "|tags=" + JSON.stringify(tags)
      + "|bbox=" + (bb ? Math.round(bb.width) + "x" + Math.round(bb.height) : "none");
  } catch (e) { r = "TEST_ERR|" + e.message; }
  document.title = r;
});
<\/script>
`;
  const idx = h.lastIndexOf("</body>");
  h = h.slice(0, idx) + inject + "\n" + h.slice(idx);
  fs.writeFileSync(harness, h);
' "$HEDIT" "$SVG" "$HARNESS"

ABS="$(pwd)/$HARNESS"
RESULT="$(
  "$CHROME" --headless --no-sandbox --disable-gpu --password-store=basic \
    --dump-dom "file://$ABS" 2>/dev/null \
  | grep -o '<title>[^<]*</title>' \
  | sed -E 's#</?title>##g'
)"

echo "SVG:    $SVG"
echo "Result: $RESULT"
echo

case "$RESULT" in
  TEST_OK*) echo "PASS — SVG loaded in hedit."; exit 0 ;;
  TEST_ERR*) echo "FAIL — loadSVGText threw."; exit 1 ;;
  *) echo "FAIL — no result (harness/Chrome did not report)."; exit 1 ;;
esac
