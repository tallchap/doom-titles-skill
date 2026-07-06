# doom-titles-skill

A Claude Code skill that generates **5 YouTube episode title candidates** for the Doom Debates podcast — pattern-matched against every published episode title and written in Liron Shapira's voice.

## What's in this repo

| Path | What it is |
|------|-----------|
| `SKILL.md` | The skill — voice rules, 6 title angles, output format |
| `doom_debates_titles.json` | Pattern library: all 145 published Doom Debates episode titles (video ID, title, date) |

## Install as a Claude Code skill

```bash
mkdir -p ~/.claude/skills/doom-titles
cp SKILL.md ~/.claude/skills/doom-titles/SKILL.md
cp doom_debates_titles.json ~/Desktop/"Claude Code"/doom_debates_titles.json
```

`SKILL.md` reads the titles JSON from `~/Desktop/Claude Code/doom_debates_titles.json` — adjust that path in Step 1 if you keep it elsewhere.

Invoke with prompts like *"title this episode"*, *"doom titles for [description]"*, or `/doom-titles <episode description>`.

## How it works

1. Loads all published titles and silently analyzes patterns (one-word CAPS emphasis, the binary `Will AI [doom] or [utopia]?` fork, returning-guest hooks)
2. Applies Liron's voice rules: confident, combative, no hashtags/emoji/hedging, 40–80 chars
3. Outputs exactly 5 candidates, each from a different angle (provocative question, flat declaration, quote pull, contrast/reframe, binary stakes, stakes framer), each with a 1-line rationale
