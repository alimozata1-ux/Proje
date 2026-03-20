#!/usr/bin/env python3
"""BABAMIC - Gerçek zamanlı mikrofon efekt uygulaması.

Kullanım:
    python babamic.py --effect "Kız sesi"
    python babamic.py --list
"""

from __future__ import annotations

import argparse
import math
import queue
import sys
from dataclasses import dataclass

import numpy as np
import sounddevice as sd


EFFECT_NAMES = [
    "Ses artırma",
    "Cinnet modu",
    "Cin modu",
    "Mini P.E.K.K.A",
    "MC köylü",
    "Yüksek bass",
    "Adam Kalın ses",
    "Kız sesi",
    "Veled sesi",
    "Cızırtılı Mod",
]


@dataclass
class EffectState:
    phase: float = 0.0


def db_to_linear(db: float) -> float:
    return 10 ** (db / 20.0)


def clip(audio: np.ndarray) -> np.ndarray:
    return np.clip(audio, -1.0, 1.0)


def bitcrush(audio: np.ndarray, bits: int = 6) -> np.ndarray:
    levels = float(2**bits)
    return np.round(audio * levels) / levels


def simple_reverb(audio: np.ndarray, sr: int, mix: float = 0.25) -> np.ndarray:
    delay_ms = [40, 75, 120]
    gains = [0.45, 0.28, 0.18]
    wet = np.zeros_like(audio)
    for dms, g in zip(delay_ms, gains):
        d = int(sr * dms / 1000)
        if d < len(audio):
            wet[d:] += audio[:-d] * g
    return clip(audio * (1 - mix) + wet * mix)


def pitch_shift_simple(audio: np.ndarray, semitones: float) -> np.ndarray:
    # Basit resampling tabanlı pitch shift (robotik ama hızlı).
    factor = 2 ** (semitones / 12)
    idx = np.arange(0, len(audio), factor)
    shifted = np.interp(idx, np.arange(len(audio)), audio)
    out_idx = np.linspace(0, len(shifted) - 1, num=len(audio))
    out = np.interp(out_idx, np.arange(len(shifted)), shifted)
    return out.astype(np.float32)


def low_boost(audio: np.ndarray, sr: int, amount: float = 1.8) -> np.ndarray:
    # Hızlı low-pass ile bass katmanı ekle.
    alpha = math.exp(-2 * math.pi * 180 / sr)
    low = np.zeros_like(audio)
    for i in range(1, len(audio)):
        low[i] = (1 - alpha) * audio[i] + alpha * low[i - 1]
    return clip(audio + (amount - 1.0) * low)


def apply_effect(name: str, audio: np.ndarray, sr: int, state: EffectState) -> np.ndarray:
    x = audio.astype(np.float32)

    if name == "Ses artırma":
        return clip(x * db_to_linear(8))

    if name == "Cinnet modu":
        t = np.arange(len(x)) / sr
        trem = 0.55 + 0.45 * np.sin(2 * np.pi * 22 * t + state.phase)
        state.phase += 2 * np.pi * 22 * len(x) / sr
        y = np.tanh(x * 5.2) * trem
        return clip(y)

    if name == "Cin modu":
        y = pitch_shift_simple(x, 5)
        y = simple_reverb(y, sr, mix=0.35)
        return clip(y * 0.9)

    if name == "Mini P.E.K.K.A":
        y = pitch_shift_simple(x, -5)
        metallic = np.sin(2 * np.pi * 35 * np.arange(len(x)) / sr + state.phase) * 0.08
        state.phase += 2 * np.pi * 35 * len(x) / sr
        return clip(np.tanh((y + metallic) * 2.5))

    if name == "MC köylü":
        # Lo-fi + nazal band etkisi.
        y = bitcrush(x, bits=5)
        y = pitch_shift_simple(y, -2)
        return clip(y * 1.1)

    if name == "Yüksek bass":
        return clip(low_boost(x, sr, amount=2.2) * 1.05)

    if name == "Adam Kalın ses":
        y = pitch_shift_simple(x, -4)
        return clip(low_boost(y, sr, amount=1.35))

    if name == "Kız sesi":
        y = pitch_shift_simple(x, 5)
        return clip(y * 0.95)

    if name == "Veled sesi":
        y = pitch_shift_simple(x, 8)
        return clip(y * 0.9)

    if name == "Cızırtılı Mod":
        noise = np.random.normal(0, 0.01, size=len(x)).astype(np.float32)
        y = bitcrush(x * 1.4, bits=4)
        return clip(y + noise)

    return x


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BABAMIC - Mikrofon efekt uygulaması")
    parser.add_argument("--effect", default="Ses artırma", help="Efekt adı")
    parser.add_argument("--samplerate", type=int, default=48000, help="Örnekleme hızı")
    parser.add_argument("--blocksize", type=int, default=1024, help="Buffer boyutu")
    parser.add_argument("--list", action="store_true", help="Efektleri listele")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list:
        print("BABAMIC efektleri:")
        for n in EFFECT_NAMES:
            print(f" - {n}")
        return 0

    if args.effect not in EFFECT_NAMES:
        print("Hata: Geçersiz efekt.", file=sys.stderr)
        print("Kullanılabilir efektler:", ", ".join(EFFECT_NAMES), file=sys.stderr)
        return 2

    print("=" * 48)
    print("BABAMIC başlatıldı")
    print(f"Efekt: {args.effect}")
    print("Durdurmak için Ctrl+C")
    print("=" * 48)

    state = EffectState()
    q_err: queue.Queue[str] = queue.Queue()

    def callback(indata, outdata, frames, time_info, status):
        if status:
            q_err.put(str(status))
        mono = indata[:, 0].copy()
        processed = apply_effect(args.effect, mono, args.samplerate, state)
        outdata[:, 0] = processed
        if outdata.shape[1] > 1:
            outdata[:, 1] = processed

    try:
        with sd.Stream(
            channels=2,
            callback=callback,
            samplerate=args.samplerate,
            blocksize=args.blocksize,
            dtype="float32",
            latency="low",
        ):
            while True:
                try:
                    err = q_err.get_nowait()
                    print(f"[Uyarı] {err}")
                except queue.Empty:
                    pass
                sd.sleep(80)
    except KeyboardInterrupt:
        print("\nBABAMIC kapatıldı.")
        return 0
    except Exception as exc:
        print(f"Çalıştırma hatası: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
