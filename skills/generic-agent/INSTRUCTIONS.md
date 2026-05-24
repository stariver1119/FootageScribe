# FootageScribe Generic Agent Instructions

Use these instructions for local coding agents, terminal agents, Cursor, Continue, aider, or any AI assistant that can run shell commands.

## Goal

Label raw video footage, generate timestamped transcript txt files, and create rename suggestions without changing original media files.

## Safety

- Do not rename, move, delete, or overwrite original video files.
- Write outputs only under `_footage_scribe/` or a user-provided output folder.
- Use sidecar text/TSV outputs for all labels and suggestions.
- The CLI downloads a missing `whisper.cpp` model automatically unless `--no-model-download` is used.

## Command

```bash
python3 -m footage_scribe.cli --root . --model small
```

For known Korean footage:

```bash
python3 -m footage_scribe.cli --root . --model small --language ko
```

For language- or project-specific labels:

```bash
python3 -m footage_scribe.cli --root . --language en --rules en
python3 -m footage_scribe.cli --root . --language ko --rules ko
python3 -m footage_scribe.cli --root . --rules ./my-label-rules.json
```

Options:

```bash
python3 -m footage_scribe.cli --root . --limit 3
python3 -m footage_scribe.cli --root . --include 'intro|commentary'
python3 -m footage_scribe.cli --root . --mode visual-only
```

## Expected Output

```text
_footage_scribe/
├── manifest.tsv
├── rename_suggestions.tsv
└── scripts/*.txt
```

Use the generated `scripts/*.txt` files for later edit discussion with an AI agent.
