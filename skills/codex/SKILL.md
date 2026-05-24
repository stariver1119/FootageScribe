---
name: footage-scribe
description: Use when labeling raw footage, generating timestamped transcripts, preparing video source clips for editing discussion, or creating non-destructive sidecar notes for AI agents. Runs the FootageScribe CLI without renaming or moving original media.
metadata:
  short-description: Label footage into agent-ready transcripts
---

# FootageScribe

Use this skill to prepare raw video clips for editing discussion. The core tool is the shared `footage-scribe` CLI.

## Rules

- Never rename, move, delete, or modify original media unless the user explicitly asks.
- Default output folder: `_footage_scribe/`.
- Default model: local `whisper.cpp` `ggml-small.bin`.
- If the requested model is missing, the CLI downloads it automatically unless `--no-model-download` is used.
- Use `--rules en`, `--rules ko`, or a custom JSON path when the user wants language- or project-specific label behavior.
- Use `--mode visual-only` when the user only wants visual labels.
- Treat transcripts as drafts. Warn when clips are mostly silence or repeated hallucinated text.
- Do not create full edit plans unless the user asks separately.

## Commands

From a source media folder:

```bash
footage-scribe --root . --model small
```

For known Korean footage:

```bash
footage-scribe --root . --model small --language ko
```

With explicit label rules:

```bash
footage-scribe --root . --model small --language en --rules en
footage-scribe --root . --model small --language ko --rules ko
```

If the package is not installed, run from the repository:

```bash
python3 -m footage_scribe.cli --root . --model small
```

Test mode:

```bash
python3 -m footage_scribe.cli --root . --output _footage_scribe_test --limit 3
```

## Outputs

```text
_footage_scribe/
├── manifest.tsv
├── rename_suggestions.tsv
└── scripts/*.txt
```

Report output paths and mention that original files were not changed.
