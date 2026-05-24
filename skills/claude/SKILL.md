---
name: footage-scribe
description: Label raw video footage, generate timestamped transcript txt files, and create non-destructive sidecar notes for video editing discussions with AI agents.
---

# FootageScribe

Use FootageScribe when the user wants to understand, label, transcribe, or discuss raw video source clips without renaming original media.

## Operating Rules

- Original media must remain untouched by default.
- Use the shared CLI: `footage-scribe` or `python3 -m footage_scribe.cli`.
- Default output folder: `_footage_scribe/`.
- Default local transcription model: `whisper.cpp` `ggml-small.bin`.
- Output should be plain text and TSV so it can be used by any agent.
- Use `--rules en`, `--rules ko`, or a custom JSON path for language- or project-specific labels.
- Do not generate a complete edit plan unless explicitly requested.

## Typical Command

```bash
python3 -m footage_scribe.cli --root . --model small
```

Known Korean footage:

```bash
python3 -m footage_scribe.cli --root . --model small --language ko
```

Explicit label rules:

```bash
python3 -m footage_scribe.cli --root . --language en --rules en
python3 -m footage_scribe.cli --root . --language ko --rules ko
```

Test mode:

```bash
python3 -m footage_scribe.cli --root . --output _footage_scribe_test --limit 3
```

Visual-only:

```bash
python3 -m footage_scribe.cli --root . --mode visual-only
```

## Expected Output

```text
_footage_scribe/
├── manifest.tsv
├── rename_suggestions.tsv
├── frames/
├── audio/
└── scripts/
```

After running, summarize where outputs were written, note low-confidence transcripts, and remind the user that original media was not renamed.
