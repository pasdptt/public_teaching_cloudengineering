# Slide decks

One `slides.md` per week, in `weeks/week-NN/`, rendered with
[Marp](https://marp.app/). Markdown stays the authority (decision D-65, which narrows D-09);
the rendered PDFs and HTML are disposable and gitignored.

## Render

```bash
bash course/slides/render.sh 01      # one week
bash course/slides/render.sh all     # every week that has a slides.md
```

Output lands in `course/slides/out/`. `--pdf-notes` puts the presenter notes into the PDF, so
you can present from the PDF alone without a second screen.

Needs `npx`, which fetches `marp-cli` on first use. Nothing is installed permanently.

**PDF export needs a browser** (Chrome, Edge or Firefox) on the rendering machine. HTML export
does not. If PDF fails with "No suitable browser found", render HTML and print from that.

## The convention

Decks are derived from `weeks/week-NN/teaching-guide.md`, which stays authoritative for the
teaching. The deck is **what goes on the wall**; the guide is what you teach from. When they
disagree, the guide is right and the deck is stale.

Each deck covers the whole three-hour session — concepts, discussion and practical — because
the practical block's commands and checkpoints get projected too.

### Slide classes

Set per slide with `<!-- _class: name -->`.

| Class | Looks like | Use for |
|---|---|---|
| `lead` | centred, rule under the title | the title slide and the closing "next week" slide |
| `block` | solid blue, centred, carries a timing marker | section dividers — one per block of the session plan |
| `ask` | cream, orange rule, centred, large | a question put to the room, with nothing else on the slide |
| `demo` | pale green, green rule | **you are about to type.** Live demos and practical commands |
| `cost` | orange headings | money, traps, and things that bite |
| `punch` | centred, large, nothing else | one sentence that should land |

The green `demo` class earns its keep: at a glance you can tell whether the next slide is
something you say or something you run.

### Timing markers

Every `block` divider carries its minutes from the guide's session plan:

```markdown
<!-- _class: block -->

<span class="min">15 minutes</span>

# Metering, properly
```

The sum across a deck is 180 minutes. If you re-cut a deck, re-check the sum — `audit.py`
verifies it.

### Presenter notes

HTML comments become presenter notes. They carry **only** what you need while standing up:
the commands to type, a timing or sequencing reminder, and which guide section to glance at.

They deliberately do **not** duplicate the teaching guide. Two copies of the same prose
diverge, and the guide is the one that stays right.

```markdown
<!--
Take a show of hands FIRST. The split is the teaching moment and it disappears the instant
the output is on screen.
Guide: "Frame containers as an answer, not a technology"
-->
```

A comment that Marp parses as a directive (`<!-- _class: lead -->`) is consumed as a
directive and does not become a note.

## Status

| Week | Deck | Slides |
|---|---|---|
| 1 | What makes a cloud | 41 |
| 2 | Processes, isolation, containers | 38 |
| 3 | State, latency, failure | 36 |
| 4–15 | not yet authored | — |

**Validated:** all three render to HTML, the presenter notes survive into the output, and
week 1 was rendered to 40 PNGs and inspected slide by slide — no slide overflows.

**Not validated:** the vertical centring of the `lead` and `block` slides. The first render
showed those sitting in the top third, because the `header:` directive injects a `<header>`
element that becomes a flex item. The theme now takes it out of the flow, and all three decks
still render — but the corrected centring has **not been seen**. No browser was available to
re-shoot the images.

> **Check this on your first render** and say if it is wrong: the title slide and the blue
> dividers should be vertically centred, not sitting high.
