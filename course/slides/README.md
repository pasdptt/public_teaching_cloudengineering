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

### Look

A cool, near-white page with one deep-blue accent. Set in IBM Plex: **Sans** for content,
**Serif** only for the sentences meant to land (questions to the room, one-line statements,
quotations), and **Mono** for commands, labels, the footer and the session clock.

Everything is left-aligned. Every content title sits on the same line, so a deck reads as one
system. Colour carries meaning, not decoration: green appears only on terminal slides, amber
only on cost slides, and both only as a small label and a rule.

The fonts load from Google Fonts, with system fallbacks. On an offline machine the HTML falls
back to Segoe UI or Helvetica, Georgia, and Menlo or Consolas. It still reads correctly; it is
just less refined. Render the PDF on a machine with a connection, and the fonts are embedded.

### Slide classes

Set per slide with `<!-- _class: name -->`.

| Class | Looks like | Use for |
|---|---|---|
| `lead` | anchored low, accent rule above the title, mono eyebrow | the title slide and the closing "next week" slide |
| `block` | paper ground, large title, **session clock** | section dividers, one per block of the session plan |
| `ask` | serif question, "For the room" label | a question put to the room, with nothing else on the slide |
| `demo` | "● At the terminal" label, green rule on code | **you are about to type**: live demos and practical commands |
| `cost` | "Cost" label, amber emphasis | money, traps, and things that bite |
| `punch` | serif statement under an accent rule | one sentence that should land |

The `demo` label earns its keep. At a glance you can tell whether the next slide is something
you say or something you run.

### Timing markers and the session clock

Every `block` divider carries its length from the guide's session plan, and the clock time at
which the block starts and ends:

```markdown
<!-- _class: block -->

<span class="min">15 minutes</span><span class="clock">0:40 – 0:55</span>

# Metering, properly
```

The clock is time since the session started, so a glance at a divider tells you whether you
are on schedule. The minutes across a deck sum to 180, and `audit.py` verifies it. If you
re-cut a deck, re-derive the clock times as well; they are cumulative, so one changed block
shifts every later one.

### Writing slide text

Marp turns every newline inside a paragraph into a hard line break on the slide. So keep each
paragraph, list item and quotation on **one source line**, however long. Wrapping prose at 95
columns, as the rest of the repository does, produces sentences broken mid-phrase on the
wall. Separate lines that should be separate with a blank line.

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
| 1 | What makes a cloud | 40 |
| 2 | Processes, isolation, containers | 37 |
| 3 | State, latency, failure | 36 |
| 4 | Hierarchy, virtual machines, identity | 35 |
| 5 | Networking and access boundaries | 31 |
| 6 | Storage abstractions | 34 |
| 7 | Replication, consistency, choosing | 33 |
| 8 | Midterm — logistics only | 12 |
| 9–13 | not yet authored | — |
| 14 | Final exam and peer review — logistics only | 11 |
| 15 | Demonstration and defence — logistics only | 13 |

Weeks 8, 14 and 15 teach nothing new (D-66), so their decks are short: the session timeline,
the exam rules to leave on the wall, the trial-check prompt, the peer-review questions, and the
week 15 running order. The running order is a blank table on purpose — student names never go
in this repository.

**Validated:** all three decks render. Week 1 was rendered with the real Plex faces and all
40 slides were inspected: no overflow, the title and divider slides sit where they should, and
no prose breaks mid-sentence. Slide counts and timings were checked unchanged across the
redesign, and no hard line breaks remain outside code blocks.

Weeks 4–8, 14 and 15 (added 2026-11-05) were rendered to HTML and every slide was looked at
on a contact sheet with the real Plex faces: no overflow after fixes (the week 15 running order
was split into two columns to fit ten slots; three titles were shortened to one line).

**Not validated:** the PDF path in `render.sh`. It needs a browser on the rendering machine,
and neither machine used here had one available to Marp. Weeks 2 and 3 render, but they were
checked structurally, not looked at slide by slide.
