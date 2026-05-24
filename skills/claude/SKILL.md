---
name: footage-scribe
description: Label raw video footage, generate timestamped transcript txt files, create sidecar notes, and apply explicit source-file renames for video editing discussions with AI agents.
---

# FootageScribe

Use FootageScribe when the user wants to understand, label, transcribe, discuss, or explicitly rename raw video source clips.

## Operating Rules

- Original media must remain untouched unless the user explicitly asks for renaming.
- If the user wants original files renamed, use `--apply-renames`.
- Use the shared CLI: `footage-scribe` or `python3 -m footage_scribe.cli`.
- Default output folder: `_footage_scribe/`.
- Default local transcription model: `whisper.cpp` `ggml-base.bin`.
- If the requested model is missing, the CLI downloads it automatically unless `--no-model-download` is used.
- Output should be plain text and TSV so it can be used by any agent.
- Use `--rules en`, `--rules ko`, or a custom JSON path for language- or project-specific labels.
- Do not generate a complete edit plan unless explicitly requested.

## Typical Command

```bash
python3 -m footage_scribe.cli --root .
```

Known Korean footage:

```bash
python3 -m footage_scribe.cli --root . --language ko
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

Apply source-file renames when explicitly requested:

```bash
python3 -m footage_scribe.cli --root . --apply-renames
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

After running, summarize where outputs were written, note low-confidence transcripts, and state whether original media was renamed.
