#!/usr/bin/env python3
"""Convert a week's Marp deck into the files of a claude.ai Slides artifact.

    python3 course/slides/to_artifact.py 09        # one week
    python3 course/slides/to_artifact.py all       # every week with a slides.md

The Markdown in weeks/week-NN/slides.md stays the authority (decision D-65). This script
derives the presentable deck from it, so the two never drift: edit the Markdown, re-run this,
and republish. Output lands in course/slides/artifact/week-NN/project/:

    deck.json            the index: title, slide order, outline sections, typefaces
    slides/<id>.html     one <section> per slide, inline styles only (the Slides format)

Only the Markdown the decks actually use is supported: front matter, `---` slide breaks,
`<!-- _class: ... -->` directives, HTML comments as presenter notes, # and ## headings,
paragraphs, - and 1. lists, tables, fenced code, > quotations, **bold**, *italic*, `code`,
and the block dividers' <span class="min"> / <span class="clock"> timing line. Anything
else stops the script with the slide it is on, rather than being silently dropped.

Standard library only, like the rest of the course tooling.
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "course" / "slides" / "artifact"

# --- the look: minimal, professional, one accent ------------------------------------------
PAPER, WASH, INK = "#f7f8fa", "#eef1f5", "#17212d"
MUTED, FAINT, RULE = "#5c6878", "#7d8898", "#dde2e9"
ACCENT, RUN, COST = "#1f4e8c", "#1d6a52", "#9a4f12"
# the dark bookends: cover and closing slides
NIGHT, NIGHT_TEXT, NIGHT_MUTED, NIGHT_ACCENT = "#17212d", "#f2f4f7", "#b4bfcc", "#9cbbe6"

SANS = "'IBM Plex Sans', Arial, sans-serif"
SERIF = "'IBM Plex Serif', Georgia, serif"
MONO = "'IBM Plex Mono', 'Courier New', monospace"

# one type scale: display · title/statement · body · dense (tables, code) · label
DISPLAY, TITLE, BODY, DENSE, LABEL = 96, 64, 40, 30, 24

FACES = {
    "ibm-plex-sans": {"family": "IBM Plex Sans",
                      "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap"},
    "ibm-plex-serif": {"family": "IBM Plex Serif",
                       "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@400;500&display=swap"},
    "ibm-plex-mono": {"family": "IBM Plex Mono",
                      "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap"},
}

PAD = "padding:128px 160px 160px"   # 1600 × 792 inside; the footer band sits below
NBSP = " "


class DeckError(Exception):
    pass


# --- inline text -------------------------------------------------------------------------

def esc(text: str) -> str:
    """Escape for slide HTML, using numeric entities only."""
    return text.replace("&", "&#38;").replace("<", "&#60;").replace(">", "&#62;")


def typographic(text: str) -> str:
    """Curly quotes and apostrophes for prose (never for code)."""
    text = re.sub(r'"([^"\n]+)"', "“\\1”", text)
    text = re.sub(r"(?<=\w)'(?=\w)", "’", text)          # don't, Iowa's
    text = re.sub(r"(?<=\s)'([^'\n]+)'", "‘\\1’", text)
    text = re.sub(r"(?<=\w)'", "’", text)                # trailing possessive
    return text


def inline(text: str, strong: str = INK, code: str = ACCENT, em: str = MUTED) -> str:
    """**bold**, *italic*, `code` → the format's inline marks. Code keeps straight quotes.

    Code spans are set aside first and put back last, so bold or italic that contains code
    (**`terraform` is gone**) still matches as one run.
    """
    codes: list[str] = []

    def hold(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    held = re.sub(r"`([^`]+)`", hold, text)
    out = esc(typographic(held))
    out = re.sub(r"\*\*(.+?)\*\*", rf'<span style="color:{strong}"><b>\1</b></span>', out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", rf'<span style="color:{em}"><i>\1</i></span>', out)
    return re.sub(r"\x00(\d+)\x00",
                  lambda m: f'<span style="color:{code}">{esc(codes[int(m.group(1))])}</span>', out)


def plain(text: str) -> str:
    """Table cells hold plain text: strip the marks, keep the words."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", text)
    parts = re.split(r"`([^`]*)`", text)
    return "".join(esc(p) if i % 2 else esc(typographic(p)) for i, p in enumerate(parts))


# --- block parsing -----------------------------------------------------------------------

def split_slides(md: str) -> tuple[dict, list[str]]:
    m = re.match(r"---\n(.*?)\n---\n", md, re.S)
    if not m:
        raise DeckError("no front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip("'\"")
    body = md[m.end():]
    return meta, [s for s in re.split(r"\n---\n", body)]


def parse_blocks(chunk: str, where: str):
    """Return (classes, blocks, notes). Blocks are (kind, payload)."""
    classes: list[str] = []
    notes: list[str] = []

    def take_comment(m):
        inner = m.group(1).strip()
        d = re.fullmatch(r"_class:\s*([\w ]+)", inner)
        if d:
            classes.extend(d.group(1).split())
        else:
            notes.append(inner)
        return "\n"

    # protect fenced code before stripping comments
    fences: list[tuple[str, str]] = []

    def take_fence(m):
        fences.append((m.group(1), m.group(2)))
        return f"\n@@FENCE{len(fences) - 1}@@\n"

    chunk = re.sub(r"^```(\w*)\n(.*?)^```\s*$", take_fence, chunk, flags=re.S | re.M)
    chunk = re.sub(r"<!--(.*?)-->", take_comment, chunk, flags=re.S)

    blocks = []
    lines = chunk.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if m := re.fullmatch(r"@@FENCE(\d+)@@", s):
            blocks.append(("code", fences[int(m.group(1))][1].rstrip("\n").split("\n")))
            i += 1
        elif s.startswith("# "):
            blocks.append(("h1", s[2:].strip()))
            i += 1
        elif s.startswith("## "):
            blocks.append(("h2", s[3:].strip()))
            i += 1
        elif s.startswith("<span class=\"min\">"):
            m = re.fullmatch(r'<span class="min">(.*?)</span><span class="clock">(.*?)</span>', s)
            if not m:
                raise DeckError(f"{where}: unreadable timing line: {s}")
            blocks.append(("timing", (m.group(1), m.group(2))))
            i += 1
        elif s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                is_rule = any(cells) and all(re.fullmatch(r":?-+:?", c) for c in cells if c)
                if not is_rule:
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows))
        elif s.startswith("> "):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            paras = [p for p in "\n".join(quote).split("\n\n") if p.strip()]
            blocks.append(("quote", [" ".join(p.split("\n")) for p in paras]))
        elif re.match(r"[-*] ", s):
            items = []
            while i < len(lines) and re.match(r"[-*] ", lines[i].strip()):
                items.append(lines[i].strip()[2:])
                i += 1
            blocks.append(("ul", items))
        elif re.match(r"\d+\. ", s):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            blocks.append(("ol", items))
        elif s.startswith("#") or s.startswith("<"):
            raise DeckError(f"{where}: unsupported markup: {s[:60]}")
        else:
            para = [s]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"(#|\||> |[-*] |\d+\. |@@FENCE|<)", lines[i].strip()):
                para.append(lines[i].strip())
                i += 1
            blocks.append(("p", " ".join(para)))
    return classes, blocks, notes


# --- rendering ---------------------------------------------------------------------------

def code_block(lines: list[str], rule: str) -> str:
    rows = []
    for line in lines:
        text = line.replace("\t", "    ")
        # spaces carry alignment in commands and diagrams; keep every one
        text = esc(text).replace(" ", NBSP) or NBSP
        rows.append(f'<p style="font-family:{MONO};font-size:{DENSE}px;line-height:1.45;white-space:nowrap;color:{INK}">{text}</p>')
    return (f'<div style="align-self:stretch;display:flex;flex-direction:column;background:{WASH};'
            f'border-left:4px solid {rule};padding:28px 36px">' + "".join(rows) + "</div>")


def table_block(rows: list[list[str]]) -> str:
    head, body = rows[0], rows[1:]
    ncols = len(head)
    # share each column by its longest content, floored so short headers are not crushed
    weight = []
    for c in range(ncols):
        longest = max((len(r[c]) if c < len(r) else 0) for r in rows)
        weight.append(min(max(longest, 8), 60))
    total = sum(weight)
    widths = [round(100 * w / total) for w in weight]
    widths[-1] += 100 - sum(widths)
    natural = sum(min(max(len(r[c]) if c < len(r) else 0 for r in rows), 60) for c in range(ncols))
    width = max(900, min(1600, int(natural * DENSE * 0.56) + 60 * ncols))

    th = "".join(
        f'<th style="width:{widths[c]}%;font-family:{MONO};font-size:{LABEL}px;font-weight:500;'
        f'color:{MUTED};text-transform:uppercase;letter-spacing:2px;text-align:left">{plain(head[c])}</th>'
        for c in range(ncols))
    # a blank Markdown header row (| | |) means a table with no header
    trs = [f'<tr style="background:{WASH}">{th}</tr>'] if any(head) else []
    for r in body:
        r = r + [""] * (ncols - len(r))
        trs.append("<tr>" + "".join(f"<td>{plain(r[c])}</td>" for c in range(ncols)) + "</tr>")
    return (f'<table style="width:{width}px;font-family:{SANS};font-size:{DENSE}px;color:{INK};'
            f'font-variant-numeric:tabular-nums">' + "".join(trs) + "</table>")


def label(text: str, color: str, dot: bool = False) -> str:
    left = 160
    parts = []
    if dot:
        parts.append(f'<x-shape kind="ellipse" style="position:absolute;left:{left}px;top:76px;'
                     f'width:16px;height:16px;background:{color}"></x-shape>')
        left += 32
    parts.append(f'<p style="position:absolute;left:{left}px;top:64px;width:900px;font-family:{MONO};'
                 f'font-size:{LABEL}px;font-weight:500;letter-spacing:3px;text-transform:uppercase;'
                 f'color:{color}">{esc(text)}</p>')
    return "".join(parts)


def footer(text: str, number: int, dark: bool) -> str:
    color = NIGHT_MUTED if dark else FAINT
    return (f'<p style="position:absolute;left:160px;bottom:64px;width:1300px;font-family:{MONO};'
            f'font-size:{LABEL}px;color:{color}">{esc(typographic(text))}</p>'
            f'<p style="position:absolute;right:160px;bottom:64px;width:120px;text-align:right;'
            f'font-family:{MONO};font-size:{LABEL}px;color:{color}">{number}</p>')


def body_blocks(blocks, strong: str, rule: str) -> list[str]:
    out = []
    for kind, payload in blocks:
        if kind == "h2":
            out.append(f'<h2 style="font-family:{SANS};font-size:{TITLE}px;font-weight:600;line-height:1.12;'
                       f'letter-spacing:-1px;color:{INK}">{inline(payload, strong=INK)}</h2>')
        elif kind == "h1":
            out.append(f'<h2 style="font-family:{SANS};font-size:{TITLE}px;font-weight:600;line-height:1.12;'
                       f'color:{INK}">{inline(payload, strong=INK)}</h2>')
        elif kind == "p":
            out.append(f'<p style="font-size:{BODY}px;line-height:1.4;color:{INK};max-width:1380px">'
                       f'{inline(payload, strong=strong)}</p>')
        elif kind in ("ul", "ol"):
            items = "".join(f"<li>{inline(x, strong=strong)}</li>" for x in payload)
            out.append(f'<{kind} style="font-size:{BODY}px;line-height:1.4;color:{INK};max-width:1380px">'
                       f'{items}</{kind}>')
        elif kind == "code":
            out.append(code_block(payload, rule))
        elif kind == "table":
            out.append(table_block(payload))
        elif kind == "quote":
            paras = "".join(f'<p style="font-family:{SERIF};font-size:{BODY + 4}px;line-height:1.4;color:{INK}">'
                            f'{inline(p, strong=INK)}</p>' for p in payload)
            out.append(f'<div style="display:flex;flex-direction:column;gap:16px;border-left:4px solid {rule};'
                       f'padding:8px 0 8px 36px;max-width:1380px">{paras}</div>')
        else:
            raise DeckError(f"block '{kind}' not expected here")
    return out


def render_slide(sid: str, classes: list[str], blocks, notes: list[str], foot: str, n: int,
                 where: str) -> str:
    kinds = set(classes)
    unknown = kinds - {"lead", "block", "ask", "punch", "demo", "cost"}
    if unknown:
        raise DeckError(f"{where}: unknown class {sorted(unknown)}")

    aside = ""
    if notes:
        text = "\n\n".join(notes).strip()
        if len(text) > 4000:
            raise DeckError(f"{where}: notes over 4000 characters")
        aside = f"<aside>{esc(text)}</aside>"

    if "lead" in kinds:
        eyebrow = [p for k, p in blocks if k == "h2"]
        title = [p for k, p in blocks if k == "h1"]
        paras = [p for k, p in blocks if k == "p"]
        parts = []
        if eyebrow:
            parts.append(f'<p style="font-family:{MONO};font-size:{LABEL + 6}px;font-weight:500;letter-spacing:4px;'
                         f'text-transform:uppercase;color:{NIGHT_ACCENT}">{esc(eyebrow[0])}</p>')
        parts.append(f'<div style="width:240px;height:6px;background:{NIGHT_ACCENT}"></div>')
        for t in title:
            parts.append(f'<h1 style="font-family:{SANS};font-size:{DISPLAY}px;font-weight:600;line-height:1.06;'
                         f'letter-spacing:-2px;color:{NIGHT_TEXT};max-width:1500px">{inline(t, strong=NIGHT_TEXT, code=NIGHT_ACCENT)}</h1>')
        for p in paras:
            parts.append(f'<p style="font-size:{BODY}px;line-height:1.4;color:{NIGHT_MUTED};max-width:1400px">'
                         f'{inline(p, strong=NIGHT_TEXT, code=NIGHT_ACCENT, em=NIGHT_MUTED)}</p>')
        return (f'<section id="{sid}" data-transition="fade" style="background:{NIGHT};color:{NIGHT_TEXT};'
                f'font-family:{SANS};{PAD};display:flex;flex-direction:column;justify-content:end;gap:32px">'
                + "".join(parts) + aside + "</section>")   # bookends carry no footer

    if "block" in kinds:
        timing = [p for k, p in blocks if k == "timing"]
        title = [p for k, p in blocks if k == "h1"]
        paras = [p for k, p in blocks if k == "p"]
        parts = []
        if timing:
            mins, clock = timing[0]
            parts.append(f'<p style="font-family:{MONO};font-size:{LABEL}px;font-weight:500;letter-spacing:3px;'
                         f'text-transform:uppercase;color:{ACCENT}">{esc(mins)}'
                         f'<span style="color:{FAINT}">{NBSP}{NBSP}·{NBSP}{NBSP}{esc(clock)}</span></p>')
        for t in title:
            parts.append(f'<h1 style="font-family:{SANS};font-size:{DISPLAY}px;font-weight:600;line-height:1.06;'
                         f'letter-spacing:-2px;color:{INK};max-width:1500px">{inline(t, strong=INK)}</h1>')
        for p in paras:
            parts.append(f'<p style="font-size:{BODY}px;line-height:1.4;color:{MUTED};max-width:1400px">'
                         f'{inline(p, strong=INK)}</p>')
        return (f'<section id="{sid}" data-transition="fade" style="background:{WASH};color:{INK};'
                f'font-family:{SANS};{PAD};display:flex;flex-direction:column;justify-content:center;gap:28px">'
                + "".join(parts) + footer(foot, n, dark=False) + aside + "</section>")

    if "ask" in kinds or "punch" in kinds:
        tone = COST if "cost" in kinds else ACCENT
        heads = [p for k, p in blocks if k == "h2"]
        paras = [p for k, p in blocks if k == "p"]
        parts = []
        if "punch" in kinds:
            parts.append(f'<div style="width:240px;height:6px;background:{tone}"></div>')
        for h in heads:
            parts.append(f'<h2 style="font-family:{SERIF};font-size:{TITLE + 8}px;font-weight:400;line-height:1.22;'
                         f'color:{INK};max-width:1500px">{inline(h, strong=tone, em=tone)}</h2>')
        for p in paras:
            parts.append(f'<p style="font-size:{BODY}px;line-height:1.4;color:{MUTED};max-width:1400px">'
                         f'{inline(p, strong=INK)}</p>')
        lab = label("For the room", ACCENT) if "ask" in kinds else (label("Cost", COST) if "cost" in kinds else "")
        return (f'<section id="{sid}" style="background:{PAPER};color:{INK};font-family:{SANS};{PAD};'
                f'display:flex;flex-direction:column;justify-content:center;gap:28px">'
                + lab + "".join(parts) + footer(foot, n, dark=False) + aside + "</section>")

    # content slides: plain, terminal (demo) or cost
    if "demo" in kinds:
        lab, strong, rule = label("At the terminal", RUN, dot=True), RUN, RUN
    elif "cost" in kinds:
        lab, strong, rule = label("Cost", COST), COST, COST
    else:
        lab, strong, rule = "", INK, RULE
    if any(k in ("timing",) for k, _ in blocks):
        raise DeckError(f"{where}: a timing line outside a block divider")
    inner = body_blocks(blocks, strong, rule if rule != RULE else ACCENT)
    if inner and inner[0].startswith("<h2"):
        title, rest = inner[0], inner[1:]
    else:
        title, rest = "", inner
    content = (f'<div style="display:flex;flex-direction:column;align-items:start;gap:30px;flex:1">'
               + "".join(rest) + "</div>")
    return (f'<section id="{sid}" style="background:{PAPER};color:{INK};font-family:{SANS};{PAD};'
            f'display:flex;flex-direction:column;justify-content:start;gap:44px">'
            + lab + title + content + footer(foot, n, dark=False) + aside + "</section>")


# --- a rough height check, so an over-full slide is named rather than silently shrunk -----

def estimate_height(blocks) -> int:
    chars_per_line = lambda size, width=1380: max(1, int(width / (size * 0.52)))
    h = 0
    for kind, payload in blocks:
        if kind in ("h1", "h2"):
            h += 64 * 1.15 * (1 + len(payload) // chars_per_line(64, 1600)) + 44
        elif kind == "p":
            h += 40 * 1.4 * (1 + len(payload) // chars_per_line(40)) + 30
        elif kind in ("ul", "ol"):
            h += sum(40 * 1.4 * (1 + len(x) // chars_per_line(40, 1300)) for x in payload) + 30
        elif kind == "code":
            h += 30 * 1.45 * len(payload) + 56 + 30
        elif kind == "table":
            for r in payload:
                lines = max(1 + len(c) // 34 for c in r) if r else 1
                h += 30 * 2.0 * lines
            h += 30
        elif kind == "quote":
            h += sum(44 * 1.4 * (1 + len(p) // chars_per_line(44)) for p in payload) + 46
    return int(h)


# --- one deck ----------------------------------------------------------------------------

def convert(week: str) -> tuple[Path, int, list[str]]:
    src = ROOT / "weeks" / f"week-{week}" / "slides.md"
    meta, chunks = split_slides(src.read_text(encoding="utf-8"))
    foot = meta.get("footer", f"Week {int(week)}")
    out = OUT / f"week-{week}" / "project"
    slides_dir = out / "slides"
    if slides_dir.exists():
        for old in slides_dir.glob("*.html"):
            old.unlink()
    slides_dir.mkdir(parents=True, exist_ok=True)

    order, sections, warnings = [], {}, []
    n = 0
    for chunk in chunks:
        n_candidate = n + 1
        where = f"week {week}, slide {n_candidate}"
        classes, blocks, notes = parse_blocks(chunk, where)
        if not blocks:
            if notes and not order:
                continue          # the deck-level comment above the cover
            raise DeckError(f"{where}: empty slide")
        n = n_candidate
        if n == 1:
            notes = [x for x in notes if not x.startswith("Deck for week")]
        sid = f"s{n:02d}"
        (slides_dir / f"{sid}.html").write_text(
            render_slide(sid, classes, blocks, notes, foot, n, where) + "\n", encoding="utf-8")
        order.append(sid)

        if n == 1:
            sections["opening"] = {"description": "Title, timing and where the course is", "start": sid}
        elif "block" in classes:
            title = next((p for k, p in blocks if k == "h1"), "Section")
            mins = next((p[0] for k, p in blocks if k == "timing"), "")
            sections[f"part{len(sections)}"] = {
                "description": typographic(f"{title} — {mins}".strip(" —")),
                "start": sid}

        if not ({"block", "lead", "ask", "punch"} & set(classes)):
            est = estimate_height(blocks) + (60 if {"demo", "cost"} & set(classes) else 0)
            if est > 792:
                warnings.append(f"{sid}: about {est}px of content for 792px — check it")

    deck = {
        "v": 4,
        "createdOnFiles": {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "lists": "css",
        "title": typographic(foot),
        "cover": order[0],
        "order": order,
        "sections": sections,
        "faces": FACES,
        "designSystems": [],
    }
    existing = out / "deck.json"
    if existing.exists():
        # keep the creation stamp stable across regenerations
        try:
            deck["createdOnFiles"] = json.loads(existing.read_text())["createdOnFiles"]
        except (KeyError, ValueError):
            pass
    existing.write_text(json.dumps(deck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out, len(order), warnings


def main(argv: list[str]) -> int:
    arg = argv[1] if len(argv) > 1 else "all"
    weeks = ([p.parent.name[5:] for p in sorted((ROOT / "weeks").glob("week-*/slides.md"))]
             if arg == "all" else [arg.zfill(2)])
    failed = False
    for w in weeks:
        try:
            out, count, warnings = convert(w)
        except DeckError as exc:
            print(f"ERROR week {w}: {exc}", file=sys.stderr)
            failed = True
            continue
        print(f"week {w}: {count} slides -> {out.relative_to(ROOT)}")
        for warn in warnings:
            print(f"    {warn}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
