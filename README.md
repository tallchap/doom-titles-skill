# doom-titles-skill

A Claude Code skill that generates **5 YouTube episode title candidates** for the Doom Debates podcast — pattern-matched against every published episode title and written in Liron Shapira's voice.

Self-learning: it refreshes the title corpus from YouTube on every run, logs its candidates to a ledger, and when the human publishes a different title it resolves the row, writes the lesson, and promotes genuinely new lessons into its own rules.

## What's in this repo

| Path | What it is |
|------|-----------|
| `SKILL.md` | The skill — learning loop, episode-type classification, voice rules, Selection Pass, NEVER list, output format |
| `scripts/refresh_titles.py` | Pulls the newest Doom Debates uploads into the corpus (dedupes by video ID, catches retitles, tags each entry `episode`/`clip`/`short` by duration) |
| `references/title-ledger.md` | One row per episode: what the skill generated vs. what actually got published, plus the lesson |
| `references/case-studies.md` | Annotated misses — the ground truth the Selection Pass rules are built from |
| `doom_debates_titles.json` | Pattern library: 326 published Doom Debates titles (video ID, title, date, type), through 2026-08-26 |

## Install as a Claude Code skill

```bash
git clone https://github.com/tallchap/doom-titles-skill ~/.claude/skills/doom-titles
cp ~/.claude/skills/doom-titles/doom_debates_titles.json ~/Desktop/ClaudeCode/doom_debates_titles.json
```

The corpus path is `~/Desktop/ClaudeCode/doom_debates_titles.json` — adjust in Step 0/Step 1 if you keep it elsewhere. **Keep the path free of spaces**: a bare `@import` in the Claude Code instruction chain parses only up to the first space and fails silently.

Invoke with prompts like *"title this episode"*, *"doom titles for [description]"*, or `/doom-titles <episode description>`.

## How it works

1. **Step 0 — learning refresh.** Refresh the corpus, match any `pending` ledger rows against newly published episodes, fill in the final title, write the lesson, and add a case study when the pick differed. Never blocks generation if the refresh fails.
2. **Step 1 — pattern library.** Load published titles, pattern-matching only on `type: "episode"` (shorts and clips follow a different, compressed style).
3. **Step 1.5 — classify the episode type.** Guest debate, news livestream, special report, contrarian insider, meta/community, street interviews, archival crosspost — each has a distinct published-title shape.
4. **Generate + Selection Pass.** Liron's voice rules: confident, combative, no hashtags/emoji/hedging. Exactly 5 candidates from different angles, each with a 1-line rationale, run through the Selection Pass and NEVER list.
5. **Step 4.5 — log to the ledger** so the next run can learn from what got published.
