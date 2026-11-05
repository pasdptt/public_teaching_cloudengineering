#!/usr/bin/env bash
# Render a week's deck to PDF and HTML.
#
#   bash course/slides/render.sh 01        # one week
#   bash course/slides/render.sh all       # every week that has a slides.md
#
# Output goes to course/slides/out/, which is gitignored: the markdown is the authority and
# the rendered files are disposable (decision D-65). Render before the session, present from
# the PDF, and do not commit the output.
#
# Needs npx, which fetches marp-cli on first use. No permanent install.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
out="$here/out"
theme="$here/theme.css"

command -v npx >/dev/null || {
  echo "ERROR: npx not found. Install Node.js, or render elsewhere." >&2
  exit 1
}

mkdir -p "$out"

render_one() {
  local week="$1"
  local src="$repo/weeks/week-$week/slides.md"
  [[ -f "$src" ]] || { echo "  no slides.md for week $week — skipping"; return 0; }
  echo "==> week $week"
  npx --yes @marp-team/marp-cli@latest "$src" \
      --theme-set "$theme" \
      --allow-local-files --no-stdin \
      --pdf --pdf-notes \
      -o "$out/week-$week.pdf"
  npx --yes @marp-team/marp-cli@latest "$src" \
      --theme-set "$theme" \
      --allow-local-files --no-stdin \
      -o "$out/week-$week.html"
  echo "    $out/week-$week.pdf"
  echo "    $out/week-$week.html"
}

if [[ "${1:-all}" == "all" ]]; then
  for d in "$repo"/weeks/week-*/; do
    render_one "$(basename "$d" | sed 's/week-//')"
  done
else
  render_one "$1"
fi

echo
echo "Done. --pdf-notes puts the presenter notes in the PDF, so you can present from it"
echo "without a second screen."
