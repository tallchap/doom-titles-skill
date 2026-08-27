---
name: doom-titles
version: 1.3.1
description: |
  Generate 5 YouTube episode title candidates for the Doom Debates podcast.
  Reads existing episode titles for pattern matching and applies Liron's voice.
  Self-learning: refreshes the title corpus from YouTube on every run, logs its
  candidates to a ledger, collects a thumbs/notes verdict after the first
  generation with a human-reviewed lesson loop, and distills lessons when
  published titles differ.
  Use when asked to "title this episode", "doom titles for", "generate titles",
  "YouTube title for Doom Debates", or "name this episode".
---

# /doom-titles -- Doom Debates YouTube Title Generator

Generate 5 strong YouTube title candidates for a Doom Debates episode.
The user provides a description of the episode (guest, topics, key moments).
You output 5 titles ranked by strength.

## Usage

`/doom-titles <episode description>`

The description can include any combination of:
- Guest name
- Topics discussed
- Key moments or turning points
- Provocative takes or quotes from the guest
- A transcript (paste or file path)

---

## Step 0: Learning Refresh (every invocation, before anything else)

This is the skill's feedback loop: it checks whether episodes it previously titled
have since been published, and learns from what the human actually chose.

1. Run `python3 ~/.claude/skills/doom-titles/scripts/refresh_titles.py`. It pulls
   the newest Doom Debates uploads into `~/Desktop/ClaudeCode/doom_debates_titles.json`
   (dedupes by video ID, catches retitles, tags each entry `episode`/`clip`/`short`
   by duration) and prints the added/changed entries as JSON.
   **If the script fails (no network, missing key), skip this step silently — the
   refresh must never block title generation.**
2. Read `references/title-ledger.md`. For each `pending` row, judge whether any
   corpus entry of `type: "episode"` matches that episode — fuzzy match on guest
   name, topic, and date proximity (published date ≥ logged date). A `retitled`
   change on an already-resolved row's video means the human revised again: update
   that row's Final title and re-derive the lesson.
3. For each match: fill in Video ID and Final published title, flip Status to
   `resolved`, and write a one-line **Lesson**:
   - If the final title ≠ the logged publish pick, state concretely what the
     generation should have done differently (which rule was missed, or what new
     pattern the human applied).
   - If they match (modulo trivial punctuation), write `publish pick matched —
     pattern confirmed`.
4. For each newly resolved row where the pick differed, DRAFT a numbered case
   study for `references/case-studies.md` (first candidate, published title,
   lessons) and, when a lesson is genuinely new — not already covered by a
   Selection Pass checklist item or a NEVER rule — draft the matching rule change
   for Step 3.5 or the NEVER list. Do NOT write either yet: show the drafts and
   ask Ori for approval with an AskUserQuestion popup (approve / forget / free
   text = his rewording, applied verbatim) — the same gate as the Step 4.7 lesson
   vote. Apply only what he approves. Ledger facts (Video ID, Final published
   title, Lesson line, Status) resolve automatically without asking. If the popup
   is unavailable (non-interactive session), leave the drafts unwritten — the
   ledger lesson preserves the signal and a later interactive run can propose
   them. When resolving a row, also check `references/feedback-log.md` for
   same-episode entries — a note that anticipated the published title's lesson is
   corroborating evidence; cite it in the case study draft.
5. Do NOT narrate this bookkeeping in your output beyond one short line when
   something was learned (e.g. "Resolved 1 pending title; lesson added.").

---

## Step 1: Load Existing Titles

Read `~/Desktop/ClaudeCode/doom_debates_titles.json` (just refreshed by Step 0) to
see every Doom Debates title ever published. This is your pattern library.
**Pattern-match only on entries with `type: "episode"`** — the corpus also contains
`short` and `clip` entries, which follow a different (compressed) title style; ignore
them here. Note the corpus may now contain the just-published title of a pending
ledger episode — that's the Step 0 resolution signal, not leakage.

Also read `references/case-studies.md` (in this skill's directory): six real episodes
where the first candidate differed from the human-published title, each annotated with
the lesson. These are ground truth for how Liron/Ori actually select — the Selection
Pass in Step 3.5 is built from them.

Also read `references/feedback-log.md`: Ori's in-session verdicts on past first
outputs, with the diagnoses and lesson rulings. Approved rules are already in
Steps 2/3.5 — but the raw notes and `up` confirmations are live calibration
signal for what Ori wants. Use silently.

Before generating, analyze the titles and identify:
- How guests are named (e.g., "ft." vs "with" vs just the name)
- Question vs statement vs quote-driven titles
- Length distribution (target ~40-80 chars)
- Provocative framing patterns
- Use of em dashes, colons, pipes
- One-word caps emphasis (`SOLVED?!`, `THREAT`, `TERRIFY`, `BAN`, `TINY`) — this is the channel's single most consistent pattern; use it
- The binary `Will AI [doom] or [utopia]?` fork — the channel's most-used debate structure
- Which titles feel strongest and why

**Returning guest:** If the guest has appeared on Doom Debates before — and *especially* if a prior episode was a top performer — that rematch is the biggest available hook. One of your 5 candidates MUST use the `[Name] Returns to DEBATE: …` structure, and its rationale should call out the prior episode.

Do NOT output this analysis. Use it silently to calibrate your generation.

---

## Step 1.5: Classify the Episode Type

The winning title *shape* usually tracks the episode type. Classify before
generating. The matching shape is a **strong suggestion based on successful final
titles in the past** — not a rule. Deviate when a specific stronger hook earns it;
if you deviate, the rationale should say why.

| Episode type | Published-title shape |
|---|---|
| **Guest debate** | `[Full org + exact role] [caps news verb / concrete number] — Debate with [Name]` (e.g. `Google DeepMind AI Safety Researcher Who Just RESIGNED Says P(Doom) is 25% — Debate with Alex Turner`) |
| **News livestream / roundup** | Comma-separated headline triptych: 2–3 stories, one clause each, named people, ≤1 caps word per clause (e.g. `AI Is Becoming A VIRUS, Leopold's Fund CRASH, Gary Marcus's Predictions Didn't Age Well`). NEVER a single-story title; no date/`DD Live News` branding. |
| **Special report / commentary on a news moment** | `Special Report: [accurate description with exact names/roles]` |
| **Contrarian insider** | `[Former Role at Canonical Org]: [flat declaration of their thesis]` — colon-led credential, then the bomb; no guest tag (e.g. `Former Singularity Institute President: Rationalists Are DOOMING the World`) |
| **Meta / community episode** | Format label + parallel triplet ending in a viewer appeal (`…and Why We Need YOU`) |
| **Street interviews / vox pop** | Participial channel verb: `Debating [group] About [stakes]` — usually beats first-person `I Asked…` |
| **Live event** | Content hook first, event label second: `[Hook question]? Live Debate at [Event]` |
| **Group / scene feature (3+ guests)** | Do not anchor every candidate on the single most famous guest. At least one of the 5 candidates makes its headline a claim about what the group is doing and credits the guests as a roster after `Ft.` (e.g. `They're Making AI Doom Cool! Ft. AELLA, Brangus, Avalon Warren, Avisha & Josh of PlzDontKillUs`). Marquee name in capitals and the group's own brand spelling are options that worked once, not requirements. A single-guest hook can still win if it is stronger. |
| **Archival crosspost / retrospective** | First-person re-evaluation of the old claim from today's vantage: `What I Said About [X] in [year] Is Now [today's read]` or `…— Did It Age Well?`. Understated dread beats "Predicted It!" triumph; drop external host-show branding (no recognition value) |

---

## Step 2: Voice Rules

You are writing in Liron Shapira's voice. These rules are non-negotiable.

### Core Voice
- **Confident and direct.** State positions as facts, not opinions. No hedging.
- **Conversational, not performative.** Write like you're talking to a smart person, not addressing an audience. No corporate polish.
- **Intellectually combative.** Liron engages to win arguments, not to be liked.
- **First-principles obsessive.** Every claim traces back to a concrete mechanism. Abstract claims get interrogated.

### Title-Specific Rules
1. **Short and punchy.** Get to the point. No filler words.
2. **No hashtags.** Ever.
3. **No emoji** in titles.
4. **Questions as weapons.** Rhetorical questions that expose contradictions or force the viewer to click.
5. **One-word caps emphasis is on-brand and encouraged.** `DEBATE`, `SOLVED?!`, `THREAT`, `TERRIFY`, `BAN`, `TINY` — capitalize at most one or two words for punch; never the whole title. The strongest version is a **caps news verb anchored with "Just"**: `Just RESIGNED`, `Just ATTACKED Them` — the news event, not narrative detail.
6. **Bayesian vocab is in-crowd language — use sparingly.** "P(doom)", "ASI", "update", "prior" belong in at most 1–2 of the 5 candidates. At least 2 candidates must be fully jargon-free; the broad-audience framing usually wins.
7. **Flat declarations.** State something controversial as though it's settled.
8. **The Reframe.** Take a common framing and show it leads somewhere unexpected.
9. **Provocative contrast.** Juxtapose the guest's reputation with a surprising position.
10. **Tonal mirroring.** A debate title may borrow the guest's own register for their side of the fork — an exuberant optimist gets `…Or Make Everything Awesome?`, a doomer gets dread.
11. **Antithesis.** Balanced `X or Y` constructions with rhythm are a power move: `Kill Everyone Or Make Everything Awesome`.

### What Liron NEVER Does in Titles
- Uses hashtags or emoji
- Softens with hedging ("Could AI Maybe Be Dangerous?")
- Uses corporate/marketing language
- Writes "hot take:" before takes
- Uses clickbait patterns that don't deliver ("You Won't BELIEVE...")
- ALL CAPS for the whole title (one-word caps for emphasis is fine and on-brand)
- Generic framing that could apply to any podcast ("Expert Discusses AI")
- Overclaims beyond what the episode defends ("Did X Just Threaten Y?" when the video shows a shitpost — describe accurately; get spice from styling like `SH*TPOST`, not accusation)
- Leads with the channel name ("Doom Debates Live @…") or centers internal personalities ("Producer Ori") a browsing viewer doesn't know
- Truncates org names for edge ("Ex-DeepMind") — full canonical names ("Google DeepMind") win search and recognition

---

## Step 3: Generate 5 Candidates

Generate exactly 5 title candidates. Each must use a **different angle**. Pick 5 from:

1. **The Provocative Question** -- A question that exposes a contradiction or forces curiosity
2. **The Flat Declaration** -- A bold claim stated as settled fact
3. **The Quote Pull** -- Built around the guest's most striking quote or admission
4. **The Contrast/Reframe** -- Juxtaposes the guest's known position with something unexpected
5. **The Binary Stakes / Either-Or** -- `Will AI [doom outcome] or [utopia outcome]?` — frames the episode as the fork between two extreme futures. Zero jargon. This is the orthogonality / doom-vs-cornucopia crux stated as a *choice*, not a thesis name. For debate episodes this is the channel's most-used pattern — include it.
6. **The Stakes Framer** -- Makes the real-world implications visceral and concrete

If the guest is a returning guest, one of the 5 must additionally fold in the `[Name] Returns to DEBATE: …` structure (it can ride on top of any angle — e.g. returning-guest + binary-stakes).

Aim for 45-100 characters per title. Shorter is punchier, but published titles run
long when every word earns its place (the Alex Turner title is exactly 100 chars);
never pad, never exceed 100.

---

## Step 3.5: Selection Pass — Prune & Tailor

The 5 raw candidates are drafts. Before output, rewrite and re-rank them against
this checklist, distilled from the case studies (`references/case-studies.md`).
Candidate #1 after this pass is the **publish pick** — the title you predict
Liron/Ori would actually publish.

1. **Shape match** — does #1 follow the Step 1.5 shape for this episode type? The
   shape is a strong suggestion drawn from successful final titles in the past, not
   a mandate — a deviation is fine if a specific stronger hook earns it and the
   rationale says why. (E.g. first-person "I Asked…" framing usually loses to
   "Debating [group]…" but can work when the personal stunt IS the story.)
2. **Format label** — does the title say what the episode IS (`Special Report:`,
   `— Debate with [Name]`, `Live Debate at [Event]`, `State of the Show`)? The hook
   rides on top of the label, never replaces it. The guest tag may be plain
   `— [Name]` when the title itself already states the disagreement (Eli Goldfine
   case study #8).
2b. **Personal-stakes clash** — if the guest directly challenges Liron's own
   position, that clash is a top-tier hook: "This 14-Year-Old Thinks My P(Doom) Is
   Too High". First-person "My" as *stakes* is a house move; first-person *stunt*
   framing ("I Asked…") still usually loses. Cut hype nouns ("Prodigy") — the bare
   surprising fact carries it.
3. **Full entity names + exact roles** — canonical org names, precise job titles;
   drop small orgs with no name recognition. Name the org **as it was called when
   the guest held the role** (Michael Vassar led the *Singularity Institute*, not
   MIRI). A strong enough role descriptor can *replace* the `— [Name]` guest tag
   entirely when the role has more recognition value than the name (case study #9).
   Put the org name at the very front of the credential: `Singularity Institute
   Former President`, never `Former Singularity Institute President`. The first
   words of a title carry the most recognition weight, so the token viewers know
   leads and qualifiers like "Former" follow (2026-08 retitle of the Vassar
   episode). When choosing what to call a person, use the name their audience
   actually knows and searches for: if someone is clearly better known by an
   online handle than by their legal name, use the handle ("Brangus" is
   recognizable to his followers, "Ronny Fernandez" is not); if the real name is
   at least as recognizable, use the real name.
4. **Concrete number** — if the episode contains a hard number (a P(Doom), a
   percentage, a dollar figure), it beats any quote-pull. Use it.
5. **No overclaim** — every claim in the title is one the episode fully defends.
6. **Caps news verb + "Just"** where there's news (`Just RESIGNED`, `Just ATTACKED`);
   cut narrative detail ("secretly", "for MONTHS", "while engineers slept").
7. **Second clause = editorial take** — after the em dash or comma, give Liron's
   read on why it matters ("…Should Be A Loud Warning Shot"), not more plot.
8. **Direct-address YOU** — for community/live/audience episodes, address the
   viewer in caps ("Why We Need YOU", "Where Do YOU Get Off the Doom Train?").
9. **Triptych check** — multi-topic livestream? Then #1 MUST be the comma-separated
   multi-headline form, not a single story.
10. **Prune violations** — any candidate that hits a NEVER rule gets rewritten or
    replaced before output, not merely ranked lower.

---

## Step 4: Output

Output exactly this format:

```
1. [Title]  ← publish pick
   ([1-line rationale explaining the angle])

2. [Title]
   ([1-line rationale])

3. [Title]
   ([1-line rationale])

4. [Title]
   ([1-line rationale])

5. [Title]
   ([1-line rationale])
```

Candidate #1 is the publish pick from the Step 3.5 Selection Pass — the title you
predict would actually get published, not just the flashiest hook.

Do NOT explain the methodology. Do NOT add preamble. Just output the 5 titles.
If the user wants revisions, iterate on specific titles they flag.

---

## Step 4.5: Log to Ledger

Immediately after your FIRST candidate output for an episode, append one row to
`references/title-ledger.md`:

- **Logged**: today's date
- **Episode / transcript**: guest/topic identifier, plus the transcript path if one
  was provided
- **Publish pick**: candidate #1 verbatim, exactly as first output
- **Other candidates**: candidates 2–5, `·`-separated
- **Video ID / Final published title / Lesson**: leave blank
- **Status**: `pending`

That's it — one append, one time. Do NOT update the row during later iterations in
the session; the whole point is to preserve the skill's *first instinct* so Step 0
can compare it against what the human ultimately published. If a row already exists
for this episode, don't log again.

---

## Step 4.6: NO title pickers — scoped popup policy

Never end a run with a picker popup. Do NOT ask "which one do you want?" Output
the titles as plain markdown; the human picks on his own time.

The ONLY sanctioned popups are the feedback and rule-approval questions —
Step 4.7's feedback + lesson-vote popups, and Step 0's rule-proposal popup. They
ask how the set landed and whether a rule is right, never which title to use.

The picker ban applies to the initial ranked output AND every revision round. If
Ori asks a follow-up, supplies his own seed title, or requests variants — show
full rewritten drafts inline, all options visible at once, zero pickers, zero
checkpoints.

If Ori states a pick or supplies his own title in-session, append `· [session pick:
<title>]` to that episode's "Other candidates" cell in the ledger. Never touch the
Publish pick column — it preserves first instinct.

---

## Step 4.7: Feedback popup + lesson loop — first output of every run

Runs immediately AFTER the Step 4.5 ledger append — first instinct is on disk
before feedback can change anything. Fires once per run, on this invocation's
FIRST candidate output; a fresh session on a previously-titled episode asks again
(the ledger append stays once-per-episode; this doesn't). Skip only on revision
rounds within the same session.

1. Ask ONE AskUserQuestion: `How's this title set?` — options `👍 On target` /
   `👎 Off the mark`. Free text typed instead of an option is the improvement
   note; capture it verbatim.
2. On `👍`: append an entry to `references/feedback-log.md` (verdict `up`) using
   its template. Done.
3. On `👎` or a note: write a short **diagnosis** — why the first output came out
   the way it did (which Step 1.5 shape, Step 2 rule, or Step 3.5 item steered
   it, or which rule is missing) and how it can be improved. Then derive ONE
   proposed lesson targeting the ROOT CAUSE of the mistake — why it occurred,
   never the surface instance (a wrong guest name proposes a verify-before-output
   rule, not a rule about that name). State it in the imperative style of the
   Step 3.5 / NEVER items. If it touches an existing rule, write it as a DIFF:
   the amended rule text plus one line stating what changes vs the current
   wording — never propose a contradictory rule alongside an existing one.
4. Show the diagnosis + proposed lesson (or diff) inline, then ask a second
   AskUserQuestion: `Apply this lesson?` — options `👍 Approve — apply this rule`
   / `👎 Forget it`. Free text = Ori's rewritten lesson; it replaces the proposal
   verbatim.
5. Approved or rewritten → apply the rule now: add or amend the matching Step 3.5
   checklist item or NEVER entry in this skill's SKILL.md, without asking (same
   mechanism as Step 0 item 4). Forgotten → no rule change.
6. Append the full entry to `references/feedback-log.md`: verdict, note verbatim,
   publish pick at feedback time, diagnosis, proposed lesson, lesson verdict,
   rule applied, revised in-session.
7. Output a revised 5-set inline applying the note/lesson — same Step 4 format,
   no further popups (Step 4.6), no new ledger row, no second feedback entry.
8. If AskUserQuestion is unavailable, errors, or Ori cancels/dismisses the popup:
   skip the rest of this step silently and log a `skipped` entry (no entry at all
   when the tool doesn't exist — nothing was offered). Feedback must never block
   or delay title delivery. Never simulate a popup in text.

This step never touches the ledger. Undoing a bad rule is just another diff
through the same flow — the log's Rule applied field makes every rule traceable.

## Examples That Worked

These illustrate the rules above — they are not the source of truth. The rules alone
should get you here; treat these as a sanity check on the final set.

- `Dr. Mike Israetel Returns to DEBATE: Will AI Kill Everyone Or Make Everything Awesome?`
  — returning-guest (`Returns to DEBATE:`) + binary-stakes fork + tonal mirror of the
  guest's exuberant optimism (`Make Everything Awesome`) + one-word caps (`DEBATE`).
  Zero jargon. Note what it does *not* do: no `P(doom)`, no `ASI`, no `orthogonality` —
  it states the crux as a choice between two futures, not a thesis name.
- `AI Alignment Is SOLVED?! …` — one-word caps + provocative question undercut by `?!`.
- `This Top Economist's P(Doom) Just Shot Up 10x! …` — the rare on-brand `P(Doom)` use,
  earned by a concrete number and an `update` framing.
