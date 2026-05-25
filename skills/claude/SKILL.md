---
name: footage-scribe
description: Label raw video footage, generate timestamped transcript txt files, create sidecar notes, and apply explicit source-file renames for video editing discussions with AI agents.
---

# FootageScribe

Use FootageScribe when the user wants to label and transcribe raw video source clips before editing. The normal workflow is to rename source files before importing them into an editor, then use the generated `.txt` scripts for agent discussion.

## Operating Rules

- If the user is preparing fresh source media before editor import, use `--apply-renames`.
- If the user says the media is already linked in an editing project, do not rename unless they explicitly confirm.
- Do not move, delete, or overwrite original media.
- Use the shared CLI: `footage-scribe` or `python3 -m footage_scribe.cli`.
- Default output folder: `_footage_scribe/`.
- Default local transcription model: `whisper.cpp` `ggml-base.bin`.
- If the requested model is missing, the CLI downloads it automatically unless `--no-model-download` is used.
- Output should be plain text and TSV so it can be used by any agent.
- Use `--rules en`, `--rules ko`, or a custom JSON path for language- or project-specific labels.
- Do not generate a complete edit plan unless explicitly requested.
- The shared CLI processes files sequentially by default. Keep that behavior for large jobs.
- Do not start multiple full-folder transcription runs at the same time.
- If you manually parallelize individual clips, sort clips by duration ascending and run at most 2 clips concurrently.
- Only parallelize short clips. Clips around 30 minutes or longer, hour-long clips, and any uncertain/large files must be processed sequentially.

## Typical Command

```bash
python3 -m footage_scribe.cli --root . --apply-renames
```

Known Korean footage:

```bash
python3 -m footage_scribe.cli --root . --language ko --apply-renames
```

Explicit label rules:

```bash
python3 -m footage_scribe.cli --root . --language en --rules en --apply-renames
python3 -m footage_scribe.cli --root . --language ko --rules ko --apply-renames
```

Safe review mode without renaming:

```bash
python3 -m footage_scribe.cli --root .
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

After running, summarize where outputs were written, note low-confidence transcripts, and state whether original media was renamed.
