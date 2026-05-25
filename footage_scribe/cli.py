#!/usr/bin/env python3
"""FootageScribe CLI.

Label raw footage, generate timestamped transcripts, and keep original media
untouched. The CLI intentionally writes plain txt/tsv outputs so any local AI
agent can inspect them.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import unicodedata
import urllib.request
from importlib.resources import files
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv"}
DEFAULT_FFMPEG = "/opt/homebrew/bin/ffmpeg"
DEFAULT_FFPROBE = "/opt/homebrew/bin/ffprobe"
DEFAULT_WHISPER_CLI = "/opt/homebrew/bin/whisper-cli"
DEFAULT_MODEL_DIR = Path.home() / ".local/share/whisper.cpp/models"
DEFAULT_RULES = "default"
WHISPER_CPP_MODEL_BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def duration_seconds(path: Path, ffprobe: str) -> float:
    data = subprocess.check_output(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    return float(json.loads(data)["format"]["duration"])


def fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def fmt_ts(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds - (m * 60)
    return f"{m:02d}:{s:06.3f}"


def clean_name(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[^\w.-]+", "_", text, flags=re.UNICODE)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "clip"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    for idx in range(2, 1000):
        candidate = path.with_name(f"{path.stem}_{idx}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not find an available filename for: {path}")


def model_path(model: str, model_dir: Path) -> Path:
    if model.endswith(".bin") or "/" in model:
        return Path(model).expanduser()
    return model_dir / f"ggml-{model}.bin"


def model_download_url(model: str) -> str | None:
    if model.endswith(".bin") or "/" in model:
        return None
    return f"{WHISPER_CPP_MODEL_BASE_URL}/ggml-{model}.bin"


def ensure_model(model: str, model_dir: Path, allow_download: bool) -> Path:
    path = model_path(model, model_dir)
    if path.exists():
        return path

    url = model_download_url(model)
    if not allow_download or not url:
        raise FileNotFoundError(f"Whisper model not found: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    print(f"Downloading Whisper model '{model}' to {path}", file=sys.stderr)
    try:
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    return path


def list_videos(root: Path, include: str | None, limit: int | None) -> list[Path]:
    pattern = re.compile(include) if include else None
    videos = sorted(
        [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS],
        key=lambda p: str(p.relative_to(root)).lower(),
    )
    if pattern:
        videos = [
            p
            for p in videos
            if pattern.search(unicodedata.normalize("NFC", str(p.relative_to(root))))
        ]
    if limit:
        videos = videos[:limit]
    return videos


def sample_times(duration: float) -> list[tuple[str, float]]:
    if duration < 300:
        return [
            ("early", min(max(0.5, duration * 0.08), max(0, duration - 0.2))),
            ("middle", max(0, duration * 0.5)),
            ("late", max(0, duration - min(1.0, duration * 0.08))),
        ]

    times: list[tuple[str, float]] = []
    t = 0.5
    while t < duration:
        times.append((f"{int(t // 60):02d}min", t))
        t += 240
    if times and duration - times[-1][1] > 90:
        times.append(("end", max(0, duration - 1.0)))
    return times


def extract_frame(video: Path, out: Path, at: float, ffmpeg: str) -> None:
    run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{at:.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            "-vf",
            "scale='min(960,iw)':-2",
            "-y",
            str(out),
        ]
    )


def extract_audio(video: Path, out: Path, ffmpeg: str) -> None:
    run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            "-y",
            str(out),
        ]
    )


def transcribe_whisper_cpp(
    audio: Path,
    outbase: Path,
    model_file: Path,
    whisper_cli: str,
    language: str,
    no_gpu: bool,
) -> None:
    cmd = [
        whisper_cli,
    ]
    if no_gpu:
        cmd.append("-ng")
    cmd.extend(
        [
            "-m",
            str(model_file),
            "-f",
            str(audio),
            "-l",
            language,
            "-otxt",
            "-ocsv",
            "-of",
            str(outbase),
            "-pp",
            "-sns",
        ]
    )
    run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def read_csv_transcript(path: Path) -> list[tuple[float, float, str]]:
    rows: list[tuple[float, float, str]] = []
    if not path.exists():
        return rows
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            text = row.get("text", "").strip()
            if not text:
                continue
            rows.append((float(row["start"]) / 1000, float(row["end"]) / 1000, text))
    return rows


def rules_path(name_or_path: str):
    path = Path(name_or_path).expanduser()
    if path.exists():
        return path
    if path.suffix == ".json":
        return files("footage_scribe").joinpath("rules", path.name)
    return files("footage_scribe").joinpath("rules", f"{name_or_path}.json")


def load_rules(name_or_path: str) -> list[dict]:
    path = rules_path(name_or_path)
    if not path.exists():
        raise FileNotFoundError(f"Label rules not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("rules", [])


def selected_rules(language: str, requested: str) -> str:
    if requested != "auto":
        return requested
    if language in {"en", "ko"}:
        return language
    return DEFAULT_RULES


def rough_label(
    original: str,
    transcript_rows: list[tuple[float, float, str]],
    rules: list[dict],
) -> tuple[str, str]:
    name = unicodedata.normalize("NFC", Path(original).stem).lower()
    text = " ".join(t for _, _, t in transcript_rows).lower()
    combined = f"{name} {text}"

    for rule in rules:
        slug = rule.get("slug")
        label = rule.get("label")
        if not slug or not label:
            continue
        keywords = [str(k).lower() for k in rule.get("keywords", [])]
        if any(keyword in combined for keyword in keywords):
            return str(slug), str(label)

    if transcript_rows:
        words = re.findall(r"[A-Za-z가-힣]{3,}", " ".join(t for _, _, t in transcript_rows))
        suffix = "_".join(words[:4]) if words else "talking_clip"
        return clean_name(f"talk_{suffix}").lower(), "talking clip"
    return clean_name(Path(original).stem).lower(), "visual label needed"


def transcript_confidence(transcript_rows: list[tuple[float, float, str]]) -> str:
    if not transcript_rows:
        return "low"
    texts = [t for _, _, t in transcript_rows]
    if len(set(texts)) <= max(1, len(texts) // 3):
        return "low"
    return "medium"


def write_script(
    path: Path,
    original: str,
    recommended: str,
    final_file: str,
    duration: float,
    model: str,
    label: str,
    confidence: str,
    original_modified: bool,
    transcript_rows: list[tuple[float, float, str]],
) -> None:
    lines = [
        f"Original file: {original}",
        f"Suggested name: {recommended}",
        f"Final file: {final_file}",
        f"Duration: {fmt_duration(duration)}",
        f"Transcription model: {model}",
        f"Original modified: {'yes' if original_modified else 'no'}",
        f"Scene label: {label}",
        f"Confidence: {confidence}",
        "",
        "Summary:",
        "Review the transcript and sampled frames, then add a human summary if needed.",
        "",
        "Transcript:",
    ]
    if transcript_rows:
        for start, end, text in transcript_rows:
            lines.append(f"[{fmt_ts(start)} - {fmt_ts(end)}] {text}")
    else:
        lines.append("(No transcript, or visual-only mode.)")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="footage-scribe",
        description="Label raw footage and generate agent-ready timestamped txt scripts.",
    )
    parser.add_argument("--root", default=".", help="Folder containing source videos.")
    parser.add_argument("--output", default="_footage_scribe", help="Output folder.")
    parser.add_argument(
        "--mode",
        choices=["transcribe", "visual-only"],
        default="transcribe",
        help="Whether to run local transcription.",
    )
    parser.add_argument("--model", default="base", help="whisper.cpp model name or .bin path.")
    parser.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR), help="GGML model directory.")
    parser.add_argument(
        "--language",
        default="auto",
        help="Whisper language code, for example auto, en, ko, ja, es.",
    )
    parser.add_argument("--include", help="Only process relative paths matching this regex.")
    parser.add_argument("--limit", type=int, help="Process only the first N matching videos.")
    parser.add_argument(
        "--apply-renames",
        action="store_true",
        help="Rename original video files to the suggested names after sidecar files are written.",
    )
    parser.add_argument("--ffmpeg", default=DEFAULT_FFMPEG)
    parser.add_argument("--ffprobe", default=DEFAULT_FFPROBE)
    parser.add_argument("--whisper-cli", default=DEFAULT_WHISPER_CLI)
    parser.add_argument(
        "--no-model-download",
        action="store_true",
        help="Fail if the requested Whisper model is missing instead of downloading it.",
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="Pass -ng to whisper.cpp and disable GPU/Metal acceleration.",
    )
    parser.add_argument(
        "--rules",
        default="auto",
        help="Label rule set name or JSON path. Built-ins: auto, default, en, ko.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    out = (root / args.output).resolve()
    scripts = out / "scripts"
    audio_dir = out / "audio"
    frames = out / "frames"
    for folder in [scripts, audio_dir, frames]:
        folder.mkdir(parents=True, exist_ok=True)

    rule_set = selected_rules(args.language, args.rules)
    label_rules = load_rules(rule_set)
    videos = list_videos(root, args.include, args.limit)
    model_file: Path | None = None
    if args.mode == "transcribe" and videos:
        try:
            model_file = ensure_model(
                args.model,
                Path(args.model_dir).expanduser(),
                not args.no_model_download,
            )
        except Exception as exc:
            print(f"Error preparing Whisper model: {exc}", file=sys.stderr)
            return 2
    manifest_rows = []
    rename_rows = []

    for idx, video in enumerate(videos, 1):
        rel = str(video.relative_to(root))
        duration = duration_seconds(video, args.ffprobe)
        stem = clean_name(Path(rel).stem)

        frame_files = []
        for slot, seconds in sample_times(duration):
            frame = frames / f"{idx:03d}_{stem}_{slot}.jpg"
            try:
                extract_frame(video, frame, seconds, args.ffmpeg)
                frame_files.append(str(frame.relative_to(out)))
            except Exception:
                pass

        transcript_rows: list[tuple[float, float, str]] = []
        model_used = "none"
        if args.mode == "transcribe":
            wav = audio_dir / f"{idx:03d}_{stem}.wav"
            rawbase = scripts / f"{idx:03d}_{stem}.raw"
            try:
                extract_audio(video, wav, args.ffmpeg)
                if model_file is None:
                    raise FileNotFoundError("Whisper model was not prepared.")
                transcribe_whisper_cpp(
                    wav,
                    rawbase,
                    model_file,
                    args.whisper_cli,
                    args.language,
                    args.no_gpu,
                )
                raw_csv = rawbase.with_suffix(".raw.csv")
                raw_txt = rawbase.with_suffix(".raw.txt")
                transcript_rows = read_csv_transcript(raw_csv)
                raw_csv.unlink(missing_ok=True)
                raw_txt.unlink(missing_ok=True)
                model_used = f"whisper.cpp ggml-{args.model}"
            except Exception as exc:
                model_used = f"failed: {exc}"

        label_slug, scene_label = rough_label(rel, transcript_rows, label_rules)
        stem_lower = stem.lower()
        if stem_lower.startswith(f"{label_slug}_"):
            recommended = stem_lower + video.suffix.lower()
        else:
            recommended = clean_name(f"{label_slug}_{stem}").lower() + video.suffix.lower()
        confidence = transcript_confidence(transcript_rows)
        script_name = f"{idx:03d}_{clean_name(Path(recommended).stem).lower()}.txt"
        final_file = rel
        renamed = "no"
        if args.apply_renames:
            try:
                target = video.with_name(recommended)
                if target == video:
                    renamed = "already"
                else:
                    target = unique_path(target)
                    video.rename(target)
                    renamed = "yes"
                final_file = str(target.relative_to(root))
            except Exception as exc:
                renamed = f"failed: {exc}"
        write_script(
            scripts / script_name,
            rel,
            recommended,
            final_file,
            duration,
            model_used,
            scene_label,
            confidence,
            renamed == "yes",
            transcript_rows,
        )

        manifest_rows.append(
            [idx, rel, final_file, fmt_duration(duration), script_name, ";".join(frame_files), model_used, confidence]
        )
        rename_rows.append([idx, rel, recommended, final_file, renamed])

    with (out / "manifest.tsv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            [
                "index",
                "original_file",
                "final_file",
                "duration",
                "script_txt",
                "frames",
                "transcription_model",
                "confidence",
            ]
        )
        writer.writerows(manifest_rows)

    with (out / "rename_suggestions.tsv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["index", "original_file", "suggested_name", "final_file", "renamed"])
        writer.writerows(rename_rows)

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
