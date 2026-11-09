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

## Presentable decks on claude.ai

The same fifteen decks are also published as claude.ai **Slides** artifacts: a 1920×1080 canvas
you can present full screen, page through, comment on, and export to PDF or PowerPoint.

The look matches the instructor's executive deck ("Data Value Frontier"), so every deck shares
its mood, and it stays strict so that nothing changes as you step through a deck:

- **Two typefaces with fixed jobs.** Manrope for every title, Inter for every other word; IBM
  Plex Mono appears only inside code blocks.
- **One header.** Every ordinary slide opens with a small uppercase teal eyebrow (the part of
  the session, "For the room", "At the terminal", "Cost") and then its title, at the same top
  margin. Covers and section dividers are the only slides that centre their content.
- **Two title sizes.** 60px on every ordinary slide, questions and statements included; 80px
  on covers and section dividers. A statement written as several `##` lines becomes one heading.
- **Warm paper and a navy night.** Content sits on warm paper (`#f5f3ee`). Covers, closing
  slides and section dividers use a navy gradient with gold eyebrows and a short gold rule, with
  no decorative artwork. Question slides sit on a pale teal wash. Code blocks
  are navy cards, tables have a teal header row, and quotations are pale amber callouts.
- **Colour marks the kind of slide.** Teal for the session part and questions, blue for
  terminal slides, amber for cost. Every text and background pair passes WCAG AA contrast.

| Week | Deck | Slides |
|---|---|---|
| 1 | [What makes a cloud](https://claude.ai/artifact/Bc9LrKS3qQUSmKod4jhWJW) | 40 |
| 2 | [Processes, isolation, containers](https://claude.ai/artifact/Kmfv5f7AJWXtaSmDkSHVQr) | 37 |
| 3 | [State, latency, failure](https://claude.ai/artifact/S6bTkK7r4R1d1gvJoG4MGU) | 36 |
| 4 | [Hierarchy, virtual machines, identity](https://claude.ai/artifact/8T9hqZG8EMCS84ZpdizsH5) | 35 |
| 5 | [Networking and access boundaries](https://claude.ai/artifact/AsdYRw31iwvXMdU3yeaPUd) | 31 |
| 6 | [Storage abstractions](https://claude.ai/artifact/7XQupUBwbESPSXDj2Hug3B) | 34 |
| 7 | [Replication, consistency, choosing](https://claude.ai/artifact/Cb7kBoLPQRimc6FEpCyYHG) | 33 |
| 8 | [Midterm](https://claude.ai/artifact/L4KayoWqrhQsRuyHmUDeq2) | 12 |
| 9 | [Managed containers and serverless](https://claude.ai/artifact/V8rbrxY6wWjzJFq1NUS7Zf) | 36 |
| 10 | [Horizontal scaling and measurement](https://claude.ai/artifact/E1xW4c83h31pjPBYtXUv3m) | 33 |
| 11 | [Queues and event-driven processing](https://claude.ai/artifact/VAGuskEQxSoeHzJzHDiW27) | 35 |
| 12 | [Partial failure, resilience and observability](https://claude.ai/artifact/HwiGyDnvAywGjA9fEwnqKt) | 33 |
| 13 | [Infrastructure as code, environments, pipelines](https://claude.ai/artifact/3pVwsxchnKFpMtJ5KGjubM) | 44 |
| 14 | [Final exam and peer review](https://claude.ai/artifact/ChvS4FJvjkx92WtPkGkzEf) | 11 |
| 15 | [Demonstration and defence](https://claude.ai/artifact/FS6cCeNf7JN8Kj1ZZW6ecU) | 13 |

The links are also kept in [`artifact/decks.json`](artifact/decks.json). **The artifacts are
private** until you share them from each deck's Share menu.

### Where they come from

They are **generated**, not hand-made, so the Markdown stays the one source:

```bash
python3 course/slides/to_artifact.py all     # or one week: 09
```

[`to_artifact.py`](to_artifact.py) reads `weeks/week-NN/slides.md` and writes
`course/slides/artifact/week-NN/project/` — a `deck.json` index (title, slide order, the outline
of session blocks, typefaces) and one `slides/sNN.html` per slide, in the inline-styled format
the Slides artifact reads. Presenter notes come across as each slide's speaker notes. The
generated files **are committed**, so the published decks can always be rebuilt or re-published
from the repository without claude.ai.

The converter supports exactly the Markdown the decks use and stops, naming the slide, on
anything else, rather than dropping it silently. It also warns when a slide's content is likely
taller than the 792px it has; the Slides viewer shrinks an over-full box's text, so a warning
means "look at it", not "it is broken".

### Changing a deck

1. Edit `weeks/week-NN/slides.md`, as before.
2. `python3 course/slides/to_artifact.py NN`
3. Republish the changed files to that week's link (from Claude Code: the Artifact tool with
   `url` = the week's link and `root` = `course/slides/artifact/week-NN`).

**Do not edit a deck in the claude.ai editor and expect the repository to follow.** Those edits
live only in the artifact, and the next regeneration from Markdown will overwrite them. Make the
change in the Markdown.

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

**Keep every code line at 80 characters or fewer.** At the theme's 21px mono, a code block
holds about 81 characters. One longer line and Marp shrinks the **whole block** to fit, so a
single long `gcloud` command makes six lines of commands hard to read from the back of the
room. Break long commands with `\` and a two-space continuation indent.

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
| 9 | Managed containers and serverless | 36 |
| 10 | Horizontal scaling and measurement | 33 |
| 11 | Queues and event-driven processing | 35 |
| 12 | Partial failure, resilience and observability | 33 |
| 13 | Infrastructure as code, environments, pipelines | 43 |
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

Weeks 9–13 (added 2026-11-05) were rendered through `render.sh` to both PDF and HTML, then
to one PNG per slide, and all 180 slides were looked at on contact sheets with the real Plex
faces. The rendered HTML was also measured: no slide's content runs past its frame, and no
table or code block runs past the right edge. The look caught what the measurement could not —
Marp shrinks a code block with an over-long line by a transform, so the font size reads
unchanged — and four such blocks were rewrapped. Week 13 is the longest deck (43 slides)
because it carries what were two weeks; most of its slides are single questions.

**The PDF path works.** It was first exercised on 2026-11-05, on macOS with Google Chrome
installed, rendering weeks 9–13 with `--pdf-notes`. It still needs a browser on the rendering
machine; that requirement is unchanged.

**Not validated:** weeks 2 and 3 render, but they were checked structurally, not looked at
slide by slide.
