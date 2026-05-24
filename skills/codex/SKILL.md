---
name: footage-scribe
description: Use when labeling raw footage, generating timestamped transcripts, preparing video source clips for editing discussion, creating sidecar notes, or applying explicit source-file renames.
metadata:
  short-description: Label footage into agent-ready transcripts
---

# FootageScribe

Use this skill to prepare raw video clips for editing discussion. The core tool is the shared `footage-scribe` CLI.

## Rules

- Do not rename, move, delete, or modify original media unless the user explicitly asks.
- If the user wants original files renamed, use `--apply-renames`.
- Default output folder: `_footage_scribe/`.
- Default model: local `whisper.cpp` `ggml-base.bin`.
- If the requested model is missing, the CLI downloads it automatically unless `--no-model-download` is used.
- Use `--rules en`, `--rules ko`, or a custom JSON path when the user wants language- or project-specific label behavior.
- Use `--mode visual-only` when the user only wants visual labels.
- Treat transcripts as drafts. Warn when clips are mostly silence or repeated hallucinated text.
- Do not create full edit plans unless the user asks separately.

## Commands

From a source media folder:

```bash
footage-scribe --root .
```

For known Korean footage:

```bash
footage-scribe --root . --language ko
```

With explicit label rules:

```bash
footage-scribe --root . --language en --rules en
footage-scribe --root . --language ko --rules ko
```

If the package is not installed, run from the repository:

```bash
python3 -m footage_scribe.cli --root .
```

Test mode:

```bash
python3 -m footage_scribe.cli --root . --output _footage_scribe_test --limit 3
```

Apply source-file renames when explicitly requested:

```bash
footage-scribe --root . --apply-renames
```

## Outputs

```text
_footage_scribe/
├── manifest.tsv
├── rename_suggestions.tsv
└── scripts/*.txt
```

Report output paths and whether original files were renamed.
