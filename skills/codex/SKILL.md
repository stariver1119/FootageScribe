---
name: footage-scribe
description: Use when labeling raw footage, generating timestamped transcripts, preparing video source clips for editing discussion, creating sidecar notes, or applying explicit source-file renames.
metadata:
  short-description: Label footage into agent-ready transcripts
---

# FootageScribe

Use this skill to prepare raw video clips before they are imported into an editor. The normal workflow is to label and rename source files first, then import the renamed files into Premiere Pro, Resolve, Final Cut Pro, or another NLE. The core tool is the shared `footage-scribe` CLI.

## Rules

- If the user is preparing fresh source media before editor import, use `--apply-renames`.
- If the user says the media is already linked in an editing project, do not rename unless they explicitly confirm.
- Do not move, delete, or overwrite original media.
- Default output folder: `_footage_scribe/`.
- Default model: local `whisper.cpp` `ggml-base.bin`.
- If the requested model is missing, the CLI downloads it automatically unless `--no-model-download` is used.
- Use `--rules en`, `--rules ko`, or a custom JSON path when the user wants language- or project-specific label behavior.
- Use `--mode visual-only` when the user only wants visual labels.
- Treat transcripts as drafts. Warn when clips are mostly silence or repeated hallucinated text.
- Do not create full edit plans unless the user asks separately.
- The shared CLI processes files sequentially by default. Keep that behavior for large jobs.
- Do not start multiple full-folder transcription runs at the same time.
- If you manually parallelize individual clips, sort clips by duration ascending and run at most 2 clips concurrently.
- Only parallelize short clips. Clips around 30 minutes or longer, hour-long clips, and any uncertain/large files must be processed sequentially.

## Commands

From a source media folder:

```bash
footage-scribe --root . --apply-renames
```

For known Korean footage:

```bash
footage-scribe --root . --language ko --apply-renames
```

With explicit label rules:

```bash
footage-scribe --root . --language en --rules en --apply-renames
footage-scribe --root . --language ko --rules ko --apply-renames
```

If the package is not installed, run from the repository:

```bash
python3 -m footage_scribe.cli --root .
```

Safe review mode without renaming:

```bash
footage-scribe --root .
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

Report output paths and whether original files were renamed.
