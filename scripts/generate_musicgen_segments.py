#!/usr/bin/env python3
"""Generate instrumental segments via MusicGen (CPU) and concatenate to WAV."""

from __future__ import annotations

import argparse
import gc
import sys
from pathlib import Path

import numpy as np
import scipy.io.wavfile as wavfile
import torch
from transformers import MusicgenForConditionalGeneration, AutoProcessor


def generate_segment(
    model: MusicgenForConditionalGeneration,
    processor: AutoProcessor,
    prompt: str,
    max_new_tokens: int,
    guidance_scale: float,
) -> tuple[np.ndarray, int]:
    inputs = processor(text=[prompt], padding=True, return_tensors="pt")
    with torch.no_grad():
        audio_values = model.generate(
            **inputs,
            do_sample=True,
            guidance_scale=guidance_scale,
            max_new_tokens=max_new_tokens,
        )
    audio = audio_values[0, 0].cpu().numpy()
    return audio, model.config.audio_encoder.sampling_rate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("output/chongqing_instrumental.wav"))
    parser.add_argument("--segment-seconds", type=float, default=12.0)
    parser.add_argument("--total-seconds", type=float, default=120.0)
    parser.add_argument("--model", default="facebook/musicgen-small")
    args = parser.parse_args()

    # ~50 Hz codebooks; tokens scale roughly with duration
    max_new_tokens = max(256, int(args.segment_seconds * 50))
    n_segments = int(np.ceil(args.total_seconds / args.segment_seconds))

    prompts = [
        "Chinese folk pop instrumental, erhu and pipa, moderate tempo 92 BPM, "
        "Chongqing night city mood, yangtze river atmosphere, warm and nostalgic",
        "modern Chinese city pop instrumental, subtle electronic beat, erhu melody, "
        "hopeful uplift, Chongqing hills and lights",
        "cinematic Chinese instrumental bridge, strings and dizi flute, emotional swell",
        "Chinese folk pop instrumental outro, erhu, soft drums, fading night scene",
    ]

    print(f"Loading {args.model} on CPU...", flush=True)
    processor = AutoProcessor.from_pretrained(args.model)
    model = MusicgenForConditionalGeneration.from_pretrained(args.model)
    model.eval()

    segments: list[np.ndarray] = []
    sample_rate: int | None = None

    for i in range(n_segments):
        prompt = prompts[i % len(prompts)]
        print(f"Segment {i + 1}/{n_segments}: {prompt[:60]}...", flush=True)
        audio, sr = generate_segment(model, processor, prompt, max_new_tokens, 3.0)
        if sample_rate is None:
            sample_rate = sr
        segments.append(audio.astype(np.float32))
        gc.collect()

    full = np.concatenate(segments)[: int(args.total_seconds * sample_rate)]
    args.out.parent.mkdir(parents=True, exist_ok=True)

    # Normalize to 16-bit PCM
    peak = np.max(np.abs(full)) or 1.0
    pcm = (full / peak * 0.95 * 32767).astype(np.int16)
    wavfile.write(args.out, sample_rate, pcm)
    print(f"Wrote {args.out} ({len(full) / sample_rate:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
