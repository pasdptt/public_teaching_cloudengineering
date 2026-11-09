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

# --- the look: warm paper, a navy night, teal labels, gold on the dark slides -------------
# Matched to the instructor's own executive deck, so the course decks share its mood. Every
# text/background pair below was checked against WCAG AA (4.5:1; most clear 6:1).
PAPER, CARD, LINE = "#f5f3ee", "#fffefb", "#e4e0d6"
HEAD, INK, BODYC, MUTED = "#13213a", "#1b2638", "#3e4a5c", "#5e6878"
TEAL, TEAL_DARK, TEAL_TINT, TEAL_WASH = "#0f7a72", "#0b5f59", "#ddefec", "#e9f3f1"
BLUE, BLUE_TINT = "#234c8e", "#e3ebf7"          # at the terminal
AMBER, AMBER_TINT = "#8a5200", "#fbf1df"        # cost, and quotations
NIGHT = "linear-gradient(135deg, #0e1a2e 0%, #1b2f50 100%)"   # covers and section dividers
NIGHT_TEXT, NIGHT_SUB, NIGHT_FOOT, NIGHT_CARD, GOLD = "#faf8f3", "#c7d1e0", "#a3afc2", "#22365a", "#f2b544"
CODE_BG, CODE_TEXT, CODE_MARK = "#13213a", "#e8ecf2", "#8fd3c8"
SHADOW = "box-shadow:0px 8px 24px rgba(19,33,58,0.06)"

# Two typefaces with fixed jobs: Manrope for every title, Inter for every other word.
# Mono appears only inside code blocks, where alignment needs it.
HEADF = "'Manrope', Arial, sans-serif"
SANS = "'Inter', Arial, sans-serif"
MONO = "'IBM Plex Mono', 'Courier New', monospace"

# One type scale. Every ordinary slide opens with the same header (eyebrow, then title) at the
# same top margin, so stepping through a deck nothing jumps.
DISPLAY, TITLE, BODY, DENSE, LABEL = 80, 60, 36, 28, 24

FACES = {
    "manrope": {"family": "Manrope",
                "href": "https://fonts.googleapis.com/css2?family=Manrope:wght@500..800&display=swap"},
    "inter": {"family": "Inter",
              "href": "https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400..700;1,400..700&display=swap"},
    "ibm-plex-mono": {"family": "IBM Plex Mono",
                      "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&display=swap"},
}

PAD = "padding:128px 128px 160px"   # 1664 × 792 inside; the footer band sits below
NBSP = "\u00a0"


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


def inline(text: str, strong: str = HEAD, code: str = TEAL_DARK, em: str = BODYC) -> str:
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

ICONS = {   # 24-unit line icons, drawn at 28px beside an eyebrow
    "terminal": '<path d="m4 17 6-6-6-6"/><path d="M12 19h8"/>',
    "warning": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3z"/>'
               '<path d="M12 9v4"/><path d="M12 17h.01"/>',
    "speech": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
}


def icon(name: str, color: str, size: int = 28) -> str:
    return (f'<svg aria-label="{name} icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}"><g transform="scale({size / 24:.5f})" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g></svg>')


def code_block(lines: list[str]) -> str:
    rows = []
    for line in lines:
        text = line.replace("\t", "    ")
        # spaces carry alignment in commands and diagrams; keep every one
        text = esc(text).replace(" ", NBSP) or NBSP
        rows.append(f'<p style="font-family:{MONO};font-size:{DENSE}px;line-height:1.45;white-space:nowrap;'
                    f'color:{CODE_TEXT}">{text}</p>')
    return (f'<div style="align-self:stretch;display:flex;flex-direction:column;background:{CODE_BG};'
            f'border-radius:20px;padding:32px 40px">' + "".join(rows) + "</div>")


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
    width = max(900, min(1664, int(natural * DENSE * 0.56) + 60 * ncols))

    th = "".join(
        f'<th style="width:{widths[c]}%;font-family:{SANS};font-size:{LABEL}px;font-weight:700;'
        f'color:{TEAL_DARK};text-transform:uppercase;letter-spacing:2px;text-align:left">{plain(head[c])}</th>'
        for c in range(ncols))
    # a blank Markdown header row (| | |) means a table with no header
    trs = [f'<tr style="background:{TEAL_TINT}">{th}</tr>'] if any(head) else []
    for r in body:
        r = r + [""] * (ncols - len(r))
        trs.append(f'<tr style="background:{CARD}">' + "".join(f"<td>{plain(r[c])}</td>" for c in range(ncols)) + "</tr>")
    return (f'<table style="width:{width}px;font-family:{SANS};font-size:{DENSE}px;color:{INK};'
            f'font-variant-numeric:tabular-nums">' + "".join(trs) + "</table>")


def eyebrow(text_html: str, color: str, glyph: str = "") -> str:
    """The small uppercase line above every title. A fixed-height row, so titles never move."""
    ic = icon(glyph, color) if glyph else ""
    return (f'<div style="height:32px;display:flex;flex-direction:row;align-items:center;gap:14px">{ic}'
            f'<p style="font-family:{SANS};font-size:{LABEL}px;font-weight:700;letter-spacing:3px;'
            f'text-transform:uppercase;line-height:1.3;white-space:nowrap;color:{color}">{text_html}</p></div>')


def rule_row(color: str) -> str:
    """The eyebrow's slot holding only a short accent rule, for slides with no label."""
    return (f'<div style="height:32px;display:flex;flex-direction:row;align-items:center">'
            f'<div style="width:120px;height:6px;background:{color};border-radius:3px"></div></div>')


def gold_rule() -> str:
    return f'<div style="width:120px;height:6px;background:{GOLD};border-radius:3px"></div>'


def header(top: str, title_html: str) -> str:
    return f'<div style="display:flex;flex-direction:column;gap:16px">{top}{title_html}</div>'


def footer(text: str, number: int, dark: bool) -> str:
    color = NIGHT_FOOT if dark else MUTED
    return (f'<div style="position:absolute;left:128px;bottom:64px;width:1664px;display:flex;'
            f'flex-direction:row;justify-content:space-between">'
            f'<p style="font-family:{SANS};font-size:{LABEL}px;color:{color}">{esc(typographic(text))}</p>'
            f'<p style="font-family:{SANS};font-size:{LABEL}px;color:{color}">{number}</p></div>')


def title_tag(text_html: str, size: int, color: str, tag: str = "h2", width: int = 1600) -> str:
    weight, track = (800, -2) if size >= DISPLAY else (700, -1)
    return (f'<{tag} style="font-family:{HEADF};font-size:{size}px;font-weight:{weight};line-height:1.1;'
            f'letter-spacing:{track}px;color:{color};max-width:{width}px">{text_html}</{tag}>')


def body_blocks(blocks, strong: str) -> list[str]:
    out = []
    for kind, payload in blocks:
        if kind in ("h1", "h2"):
            out.append(title_tag(inline(payload), TITLE, HEAD))
        elif kind == "p":
            out.append(f'<p style="font-family:{SANS};font-size:{BODY}px;line-height:1.45;color:{INK};'
                       f'max-width:1400px">{inline(payload, strong=strong)}</p>')
        elif kind in ("ul", "ol"):
            items = "".join(f"<li>{inline(x, strong=strong)}</li>" for x in payload)
            out.append(f'<{kind} style="font-family:{SANS};font-size:{BODY}px;line-height:1.45;color:{INK};'
                       f'max-width:1400px">{items}</{kind}>')
        elif kind == "code":
            out.append(code_block(payload))
        elif kind == "table":
            out.append(table_block(payload))
        elif kind == "quote":
            paras = "".join(f'<p style="font-family:{SANS};font-size:{BODY}px;line-height:1.45;color:{INK}">'
                            f'{inline(p, code=AMBER)}</p>' for p in payload)
            out.append(f'<div style="display:flex;flex-direction:column;gap:16px;background:{AMBER_TINT};'
                       f'border-radius:20px;padding:28px 40px;max-width:1500px">{paras}</div>')
        else:
            raise DeckError(f"block '{kind}' not expected here")
    return out


def is_break(blocks) -> bool:
    return next((p for k, p in blocks if k == "h1"), "").strip().lower() == "break"


def section(sid: str, bg: str, fg: str, children: str, transition: bool = False,
            centre: bool = False) -> str:
    """Every ordinary slide shares this frame: same padding, same top-anchored column, same gap.
    Only the dark bookends and dividers centre their content, as a deliberate change of pace."""
    tr = ' data-transition="fade"' if transition else ""
    just = "center" if centre else "start"
    return (f'<section id="{sid}"{tr} style="background:{bg};color:{fg};font-family:{SANS};{PAD};'
            f'display:flex;flex-direction:column;justify-content:{just};gap:48px">' + children + "</section>")


def render_slide(sid: str, classes: list[str], blocks, notes: list[str], foot: str, n: int,
                 where: str, part: str = "", part_no: int = 0) -> str:
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

    if "lead" in kinds:   # cover and closing: the navy night, gold accents, no footer
        eyebrow_text = [p for k, p in blocks if k == "h2"]
        title = [p for k, p in blocks if k == "h1"]
        paras = [p for k, p in blocks if k == "p"]
        dark = dict(strong=NIGHT_TEXT, code=CODE_MARK, em=NIGHT_SUB)
        parts = []
        if eyebrow_text:
            parts.append(eyebrow(esc(eyebrow_text[0]), GOLD))
        parts += [title_tag(inline(t, **dark), DISPLAY, NIGHT_TEXT, tag="h1", width=1120) for t in title]
        parts.append(gold_rule())
        if paras:
            parts.append(f'<p style="font-family:{SANS};font-size:{BODY}px;line-height:1.4;color:{NIGHT_SUB};'
                         f'max-width:1120px">{inline(paras[0], **dark)}</p>')
        if paras[1:]:
            lines = "".join(f'<p style="font-family:{SANS};font-size:{DENSE + 4}px;line-height:1.4;'
                            f'color:{NIGHT_TEXT}">{inline(p, strong=GOLD, code=CODE_MARK, em=NIGHT_SUB)}</p>'
                            for p in paras[1:])
            parts.append(f'<div style="width:1240px;display:flex;flex-direction:column;gap:14px;'
                         f'background:{NIGHT_CARD};border-radius:24px;padding:36px 48px">{lines}</div>')
        return section(sid, NIGHT, NIGHT_TEXT, "".join(parts) + aside, transition=True, centre=True)

    if "block" in kinds:  # section divider: the night again, numbered
        timing = [p for k, p in blocks if k == "timing"]
        title = [p for k, p in blocks if k == "h1"]
        paras = [p for k, p in blocks if k == "p"]
        sep = f"{NBSP}{NBSP}·{NBSP}{NBSP}"
        bits = [] if is_break(blocks) else [f"Part {part_no:02d}"]   # a break is not a part
        if timing:
            bits += [esc(timing[0][0]), esc(timing[0][1])]
        label_html = sep.join(bits)
        dark = dict(strong=NIGHT_TEXT, code=CODE_MARK, em=NIGHT_SUB)
        parts = [eyebrow(label_html, GOLD)]
        parts += [title_tag(inline(t, **dark), DISPLAY, NIGHT_TEXT, tag="h1", width=1400) for t in title]
        parts.append(gold_rule())
        parts += [f'<p style="font-family:{SANS};font-size:{BODY}px;line-height:1.4;color:{NIGHT_SUB};'
                  f'max-width:1300px">{inline(p, **dark)}</p>' for p in paras]
        return section(sid, NIGHT, NIGHT_TEXT, "".join(parts) + footer(foot, n, dark=True) + aside,
                       transition=True, centre=True)

    if "ask" in kinds or "punch" in kinds:  # a question or a statement: same header, same place
        heads = [p for k, p in blocks if k == "h2"]
        paras = [p for k, p in blocks if k == "p"]
        if "ask" in kinds:
            top, bg, tone = eyebrow("For the room", TEAL_DARK, "speech"), TEAL_WASH, TEAL_DARK
        elif "cost" in kinds:
            top, bg, tone = eyebrow("Cost", AMBER, "warning"), PAPER, AMBER
        else:
            top, bg, tone = rule_row(TEAL), PAPER, TEAL_DARK
        # several ## lines are one statement: one heading, line breaks between them
        title = title_tag("<br>".join(inline(h, strong=tone, em=tone) for h in heads), TITLE, HEAD) if heads else ""
        parts = [header(top, title)]
        parts += [f'<p style="font-family:{SANS};font-size:{BODY}px;line-height:1.45;color:{BODYC};'
                  f'max-width:1400px">{inline(p)}</p>' for p in paras]
        return section(sid, bg, INK, "".join(parts) + footer(foot, n, dark=False) + aside)

    # content slides: plain, terminal (demo) or cost
    if "demo" in kinds:
        top, strong = eyebrow("At the terminal", BLUE, "terminal"), BLUE
    elif "cost" in kinds:
        top, strong = eyebrow("Cost", AMBER, "warning"), AMBER
    else:
        top, strong = eyebrow(esc(typographic(part)), TEAL_DARK), HEAD
    if any(k == "timing" for k, _ in blocks):
        raise DeckError(f"{where}: a timing line outside a block divider")
    inner = body_blocks(blocks, strong)
    if inner and inner[0].startswith("<h2"):
        title, rest = inner[0], inner[1:]
    else:
        title, rest = "", inner
    content = (f'<div style="display:flex;flex-direction:column;align-items:start;gap:32px;flex:1">'
               + "".join(rest) + "</div>")
    return section(sid, PAPER, INK, header(top, title) + content + footer(foot, n, dark=False) + aside)


# --- a rough height check, so an over-full slide is named rather than silently shrunk -----

def estimate_height(blocks) -> int:
    chars_per_line = lambda size, width=1400: max(1, int(width / (size * 0.52)))
    h = 48   # the eyebrow row and its gap
    for kind, payload in blocks:
        if kind in ("h1", "h2"):
            h += 60 * 1.1 * (1 + len(payload) // chars_per_line(60, 1600)) + 48
        elif kind == "p":
            h += 36 * 1.45 * (1 + len(payload) // chars_per_line(36)) + 32
        elif kind in ("ul", "ol"):
            h += sum(36 * 1.45 * (1 + len(x) // chars_per_line(36, 1340)) for x in payload) + 32
        elif kind == "code":
            h += 28 * 1.45 * len(payload) + 64 + 32
        elif kind == "table":
            for r in payload:
                lines = max(1 + len(c) // 36 for c in r) if r else 1
                h += 28 * 2.1 * lines
            h += 32
        elif kind == "quote":
            h += sum(36 * 1.45 * (1 + len(p) // chars_per_line(36, 1420)) for p in payload) + 56 + 32
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
    part, part_no = foot.split(" · ")[0], 0   # the eyebrow before the first divider: "Week 1"
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
        if "block" in classes and not is_break(blocks):
            part_no += 1
            part = f"{part_no:02d}{NBSP}·{NBSP}" + next((p for k, p in blocks if k == "h1"), "Section")
        (slides_dir / f"{sid}.html").write_text(
            render_slide(sid, classes, blocks, notes, foot, n, where, part, part_no) + "\n", encoding="utf-8")
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
