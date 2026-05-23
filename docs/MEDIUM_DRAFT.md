# I Built FootageScribe: Raw Footage Labels and Transcripts for AI Editing Agents

Raw footage gets messy fast.

You shoot a few days of material, import everything into Premiere Pro or Resolve, and suddenly your project is full of filenames like `VID_0017.MP4`, `IMG_2968.MOV`, and `GX010143.MP4`.

The obvious solution is to rename the files. The problem is that renaming source files after they are already linked in an editing project can break media references.

So I built **FootageScribe**.

FootageScribe labels raw footage, generates timestamped transcripts, and turns source clips into plain-text notes you can discuss with ChatGPT, Claude, Codex, Cursor, or any local AI agent. Original media stays untouched.

## The Core Idea

FootageScribe does not try to become your editor.

It does not make the final cut. It does not decide the story. It does not rename your media.

It turns raw video files into searchable, agent-ready notes:

```text
_footage_scribe/
├── manifest.tsv
├── rename_suggestions.tsv
└── scripts/
    ├── 001_intro_room_cleanup_decision.txt
    ├── 002_bed_frame_pickup_commentary.txt
    └── 003_late_night_moving_broll.txt
```

Each script is a plain `.txt` file with metadata, a suggested readable name, scene labels, and timestamped transcription.

## Why This Connects to Olwaty

I am also building [Olwaty](https://olwaty.com).

Olwaty is a content binge-watching and rediscovery platform for creators. It helps viewers continue watching a creator's archive instead of dropping off after a single video.

FootageScribe lives at the beginning of the creator-content lifecycle: making raw footage easier to understand before editing.

Olwaty lives later in the lifecycle: making finished content easier for viewers to explore, continue, and binge-watch.

Different parts of the same creator problem:

- creators need to understand their raw footage
- viewers need to understand and continue the finished archive

## Direction

I want tools like this to stay close to the creator's actual workflow. Not a giant dashboard. Not a magic one-click editor. Just useful preprocessing that respects the files you already have and the projects you already started.

That is what FootageScribe is trying to be: a small bridge between raw media chaos and structured creative discussion.

