# FootageScribe Generic Agent Instructions

Use these instructions for local coding agents, terminal agents, Cursor, Continue, aider, or any AI assistant that can run shell commands.

## Goal

Label raw video footage, generate timestamped transcript txt files, and apply source-file renames before the files are imported into an editor.

## Safety

- If the user is preparing fresh source media before editor import, use `--apply-renames`.
- If the user says the media is already linked in an editing project, do not rename unless they explicitly confirm.
- Do not move, delete, or overwrite original media.
- Write outputs only under `_footage_scribe/` or a user-provided output folder.
- Use sidecar text/TSV outputs for all labels and suggestions.
- The CLI downloads a missing `whisper.cpp` model automatically unless `--no-model-download` is used.

## Command

```bash
python3 -m footage_scribe.cli --root . --apply-renames
```

For known Korean footage:

```bash
python3 -m footage_scribe.cli --root . --language ko --apply-renames
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
python3 -m footage_scribe.cli --root . --apply-renames
```

## Expected Output

```text
_footage_scribe/
├── manifest.tsv
├── rename_suggestions.tsv
└── scripts/*.txt
```

Use the generated `scripts/*.txt` files for later edit discussion with an AI agent.
