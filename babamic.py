#!/usr/bin/env python3
"""
BABAMIC - Klasik Tkinter tabanlı mikrofon efekt uygulaması.

Bu sürüm CLI odaklı basit denemeden farklı olarak tam bir GUI içerir.
- Efekt seçimi
- Mikrofon / hoparlör cihaz seçimi
- Başlat / Durdur
- Gerçek zamanlı seviye göstergesi
- Preset benzeri kontrol slider'ları

Not:
- Çalıştırma için: pip install -r requirements.txt
- Bazı platformlarda PortAudio / sistem ses sürücülerinin yüklü olması gerekir.
"""

from __future__ import annotations

import math
import queue
import threading
import time
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import messagebox
from tkinter import ttk
from typing import Callable
from typing import Iterable

import numpy as np
import sounddevice as sd


APP_NAME = "BABAMIC"
APP_VERSION = "2.0 GUI"


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


DEFAULT_COLORS = {
    "bg": "#121212",
    "panel": "#1B1B1B",
    "panel_alt": "#202020",
    "fg": "#EAEAEA",
    "muted": "#9AA0A6",
    "accent": "#4FC3F7",
    "accent_alt": "#81C784",
    "warn": "#FFB74D",
    "danger": "#EF5350",
}


def db_to_linear(db: float) -> float:
    return 10 ** (db / 20.0)


def clip_audio(audio: np.ndarray) -> np.ndarray:
    return np.clip(audio, -1.0, 1.0)


def rms_level(audio: np.ndarray) -> float:
    if len(audio) == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio), dtype=np.float64)))


def linear_interpolate(source: np.ndarray, target_length: int) -> np.ndarray:
    if len(source) == 0:
        return np.zeros(target_length, dtype=np.float32)
    if target_length <= 1:
        return np.array([source[0]], dtype=np.float32)

    old_idx = np.arange(len(source), dtype=np.float32)
    new_idx = np.linspace(0, len(source) - 1, num=target_length, dtype=np.float32)
    out = np.interp(new_idx, old_idx, source)
    return out.astype(np.float32)


def simple_pitch_shift(audio: np.ndarray, semitones: float) -> np.ndarray:
    factor = 2 ** (semitones / 12.0)
    if factor <= 0:
        return audio.copy().astype(np.float32)

    idx = np.arange(0, len(audio), factor, dtype=np.float32)
    if len(idx) < 2:
        return audio.copy().astype(np.float32)

    shifted = np.interp(idx, np.arange(len(audio), dtype=np.float32), audio)
    restored = linear_interpolate(shifted.astype(np.float32), len(audio))
    return restored.astype(np.float32)


def simple_lowpass(audio: np.ndarray, sample_rate: int, cutoff: float = 200.0) -> np.ndarray:
    alpha = math.exp(-2.0 * math.pi * cutoff / sample_rate)
    out = np.zeros_like(audio)
    for i in range(1, len(audio)):
        out[i] = (1.0 - alpha) * audio[i] + alpha * out[i - 1]
    return out


def simple_highpass(audio: np.ndarray, sample_rate: int, cutoff: float = 1200.0) -> np.ndarray:
    alpha = math.exp(-2.0 * math.pi * cutoff / sample_rate)
    low = np.zeros_like(audio)
    for i in range(1, len(audio)):
        low[i] = (1.0 - alpha) * audio[i] + alpha * low[i - 1]
    return audio - low


def add_noise(audio: np.ndarray, amount: float = 0.01) -> np.ndarray:
    noise = np.random.normal(0.0, amount, size=len(audio)).astype(np.float32)
    return audio + noise


def bitcrush(audio: np.ndarray, bits: int = 6) -> np.ndarray:
    bits = max(2, min(16, int(bits)))
    levels = float(2**bits)
    return np.round(audio * levels) / levels


def soft_distortion(audio: np.ndarray, drive: float = 2.5) -> np.ndarray:
    return np.tanh(audio * drive)


def simple_reverb(audio: np.ndarray, sample_rate: int, wet: float = 0.2) -> np.ndarray:
    wet = max(0.0, min(1.0, wet))
    delays_ms = [35, 70, 110, 170]
    gains = [0.40, 0.25, 0.18, 0.12]
    wet_sig = np.zeros_like(audio)

    for delay_ms, gain in zip(delays_ms, gains):
        delay_samples = int(sample_rate * delay_ms / 1000.0)
        if delay_samples <= 0 or delay_samples >= len(audio):
            continue
        wet_sig[delay_samples:] += audio[:-delay_samples] * gain

    return clip_audio(audio * (1.0 - wet) + wet_sig * wet)


def ring_mod(audio: np.ndarray, sample_rate: int, freq: float, phase: float) -> tuple[np.ndarray, float]:
    t = np.arange(len(audio), dtype=np.float32) / sample_rate
    osc = np.sin(2.0 * np.pi * freq * t + phase).astype(np.float32)
    out = audio * osc
    new_phase = phase + 2.0 * np.pi * freq * (len(audio) / sample_rate)
    return out.astype(np.float32), new_phase


def tremolo(audio: np.ndarray, sample_rate: int, freq: float, depth: float, phase: float) -> tuple[np.ndarray, float]:
    depth = max(0.0, min(1.0, depth))
    t = np.arange(len(audio), dtype=np.float32) / sample_rate
    lfo = (1.0 - depth) + depth * (0.5 + 0.5 * np.sin(2.0 * np.pi * freq * t + phase))
    out = audio * lfo
    new_phase = phase + 2.0 * np.pi * freq * (len(audio) / sample_rate)
    return out.astype(np.float32), new_phase


@dataclass
class EffectParams:
    input_gain_db: float = 0.0
    output_gain_db: float = 0.0
    effect_mix: float = 1.0
    drive: float = 2.5
    reverb_wet: float = 0.22
    bass_amount: float = 1.8
    bit_depth: int = 6
    tone: float = 0.5
    noise_amount: float = 0.01


@dataclass
class EffectState:
    phase_a: float = 0.0
    phase_b: float = 0.0
    last_peak: float = 0.0
    last_rms: float = 0.0
    last_clip: bool = False
    frames_processed: int = 0


@dataclass
class AudioConfig:
    sample_rate: int = 48000
    block_size: int = 1024
    input_device: int | None = None
    output_device: int | None = None
    channels: int = 2


class EffectEngine:
    def __init__(self, params: EffectParams | None = None) -> None:
        self.params = params or EffectParams()
        self.state = EffectState()

    def apply_gain(self, audio: np.ndarray, db: float) -> np.ndarray:
        return audio * db_to_linear(db)

    def dry_wet_mix(self, dry: np.ndarray, wet: np.ndarray, mix: float) -> np.ndarray:
        mix = max(0.0, min(1.0, mix))
        return dry * (1.0 - mix) + wet * mix

    def apply_effect(self, name: str, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        x = audio.astype(np.float32)

        x = self.apply_gain(x, self.params.input_gain_db)

        if name == "Ses artırma":
            y = self.effect_ses_artirma(x, sample_rate)
        elif name == "Cinnet modu":
            y = self.effect_cinnet(x, sample_rate)
        elif name == "Cin modu":
            y = self.effect_cin_modu(x, sample_rate)
        elif name == "Mini P.E.K.K.A":
            y = self.effect_mini_pekka(x, sample_rate)
        elif name == "MC köylü":
            y = self.effect_mc_koylu(x, sample_rate)
        elif name == "Yüksek bass":
            y = self.effect_yuksek_bass(x, sample_rate)
        elif name == "Adam Kalın ses":
            y = self.effect_adam_kalin(x, sample_rate)
        elif name == "Kız sesi":
            y = self.effect_kiz_sesi(x, sample_rate)
        elif name == "Veled sesi":
            y = self.effect_veled(x, sample_rate)
        elif name == "Cızırtılı Mod":
            y = self.effect_cizirtili(x, sample_rate)
        else:
            y = x.copy()

        mixed = self.dry_wet_mix(x, y, self.params.effect_mix)
        mixed = self.apply_gain(mixed, self.params.output_gain_db)
        mixed = clip_audio(mixed)

        self.state.last_peak = float(np.max(np.abs(mixed))) if len(mixed) else 0.0
        self.state.last_rms = rms_level(mixed)
        self.state.last_clip = bool(self.state.last_peak >= 0.999)
        self.state.frames_processed += len(mixed)

        return mixed.astype(np.float32)

    def effect_ses_artirma(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        _ = sample_rate
        return clip_audio(x * db_to_linear(8.0))

    def effect_cinnet(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        y, self.state.phase_a = tremolo(
            x,
            sample_rate=sample_rate,
            freq=18.0,
            depth=0.85,
            phase=self.state.phase_a,
        )
        y = soft_distortion(y, drive=max(2.0, self.params.drive + 2.2))
        y, self.state.phase_b = ring_mod(y, sample_rate, freq=40.0, phase=self.state.phase_b)
        return clip_audio(y)

    def effect_cin_modu(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        y = simple_pitch_shift(x, 5.0)
        y = simple_reverb(y, sample_rate, wet=max(0.2, self.params.reverb_wet))
        high = simple_highpass(y, sample_rate, cutoff=1400.0)
        y = 0.55 * y + 0.45 * high
        return clip_audio(y * 0.95)

    def effect_mini_pekka(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        y = simple_pitch_shift(x, -5.0)
        robot, self.state.phase_a = ring_mod(y, sample_rate, freq=32.0, phase=self.state.phase_a)
        y = 0.75 * y + 0.25 * robot
        y = soft_distortion(y, drive=max(2.0, self.params.drive + 0.8))
        return clip_audio(y)

    def effect_mc_koylu(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        y = simple_pitch_shift(x, -2.0)
        y = bitcrush(y, bits=max(3, min(8, self.params.bit_depth)))
        band_low = simple_lowpass(y, sample_rate, cutoff=2200.0)
        band_high = simple_highpass(y, sample_rate, cutoff=350.0)
        y = 0.6 * band_low + 0.4 * band_high
        y = soft_distortion(y, drive=max(1.7, self.params.drive))
        return clip_audio(y)

    def effect_yuksek_bass(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        low = simple_lowpass(x, sample_rate, cutoff=190.0)
        amount = max(1.0, self.params.bass_amount)
        y = x + (amount - 1.0) * low
        y = simple_reverb(y, sample_rate, wet=min(0.18, self.params.reverb_wet * 0.6))
        return clip_audio(y)

    def effect_adam_kalin(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        y = simple_pitch_shift(x, -4.0)
        low = simple_lowpass(y, sample_rate, cutoff=210.0)
        y = y + 0.35 * low
        return clip_audio(y)

    def effect_kiz_sesi(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        y = simple_pitch_shift(x, 5.0)
        y = simple_highpass(y, sample_rate, cutoff=140.0) + 0.2 * y
        return clip_audio(y * 0.95)

    def effect_veled(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        y = simple_pitch_shift(x, 8.0)
        y, self.state.phase_a = tremolo(
            y,
            sample_rate=sample_rate,
            freq=6.5,
            depth=0.2,
            phase=self.state.phase_a,
        )
        return clip_audio(y * 0.92)

    def effect_cizirtili(self, x: np.ndarray, sample_rate: int) -> np.ndarray:
        _ = sample_rate
        y = bitcrush(x * 1.35, bits=max(2, min(6, self.params.bit_depth - 1)))
        y = soft_distortion(y, drive=max(2.2, self.params.drive + 0.6))
        y = add_noise(y, amount=max(0.003, self.params.noise_amount))
        return clip_audio(y)


class AudioController:
    def __init__(self, engine: EffectEngine) -> None:
        self.engine = engine
        self.config = AudioConfig()
        self.selected_effect: str = EFFECT_NAMES[0]
        self.running = False
        self.stream: sd.Stream | None = None
        self.status_queue: queue.Queue[str] = queue.Queue()
        self.meter_queue: queue.Queue[tuple[float, float, bool]] = queue.Queue(maxsize=8)
        self.lock = threading.Lock()

    def set_effect(self, name: str) -> None:
        with self.lock:
            self.selected_effect = name

    def set_config(
        self,
        sample_rate: int,
        block_size: int,
        input_device: int | None,
        output_device: int | None,
    ) -> None:
        with self.lock:
            self.config.sample_rate = int(sample_rate)
            self.config.block_size = int(block_size)
            self.config.input_device = input_device
            self.config.output_device = output_device

    def _put_meter(self, peak: float, rms: float, clipped: bool) -> None:
        item = (peak, rms, clipped)
        if self.meter_queue.full():
            try:
                self.meter_queue.get_nowait()
            except queue.Empty:
                pass
        try:
            self.meter_queue.put_nowait(item)
        except queue.Full:
            pass

    def _callback(self, indata, outdata, frames, time_info, status) -> None:
        _ = frames
        _ = time_info

        if status:
            self.status_queue.put(f"Stream status: {status}")

        with self.lock:
            effect_name = self.selected_effect
            sample_rate = self.config.sample_rate

        mono = indata[:, 0].copy().astype(np.float32)
        processed = self.engine.apply_effect(effect_name, mono, sample_rate)

        if outdata.shape[1] == 1:
            outdata[:, 0] = processed
        else:
            outdata[:, 0] = processed
            outdata[:, 1] = processed

        self._put_meter(
            self.engine.state.last_peak,
            self.engine.state.last_rms,
            self.engine.state.last_clip,
        )

    def start(self) -> None:
        if self.running:
            return

        cfg = self.config
        try:
            self.stream = sd.Stream(
                samplerate=cfg.sample_rate,
                blocksize=cfg.block_size,
                channels=cfg.channels,
                dtype="float32",
                callback=self._callback,
                latency="low",
                device=(cfg.input_device, cfg.output_device),
            )
            self.stream.start()
            self.running = True
            self.status_queue.put("Ses akışı başlatıldı.")
        except Exception as exc:
            self.stream = None
            self.running = False
            self.status_queue.put(f"Başlatma hatası: {exc}")
            raise

    def stop(self) -> None:
        if not self.running:
            return

        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
                self.stream = None
        finally:
            self.running = False
            self.status_queue.put("Ses akışı durduruldu.")

    def read_status_messages(self) -> list[str]:
        messages: list[str] = []
        while True:
            try:
                messages.append(self.status_queue.get_nowait())
            except queue.Empty:
                break
        return messages

    def read_latest_meter(self) -> tuple[float, float, bool] | None:
        latest = None
        while True:
            try:
                latest = self.meter_queue.get_nowait()
            except queue.Empty:
                break
        return latest


class MeterCanvas(tk.Canvas):
    def __init__(self, master: tk.Misc, width: int = 340, height: int = 24, **kwargs) -> None:
        super().__init__(master, width=width, height=height, highlightthickness=0, **kwargs)
        self.width_px = width
        self.height_px = height
        self.bg_color = "#0F0F0F"
        self.ok_color = "#66BB6A"
        self.warn_color = "#FFCA28"
        self.clip_color = "#EF5350"
        self.configure(bg=self.bg_color)
        self._peak = 0.0
        self._rms = 0.0
        self._clipped = False
        self.draw_meter()

    def set_level(self, peak: float, rms: float, clipped: bool) -> None:
        self._peak = max(0.0, min(1.0, peak))
        self._rms = max(0.0, min(1.0, rms * 2.2))
        self._clipped = clipped
        self.draw_meter()

    def draw_meter(self) -> None:
        self.delete("all")

        w = self.width_px
        h = self.height_px

        self.create_rectangle(0, 0, w, h, fill=self.bg_color, outline="#2B2B2B")

        rms_w = int(w * self._rms)
        peak_w = int(w * self._peak)

        meter_color = self.ok_color
        if self._peak > 0.85:
            meter_color = self.warn_color
        if self._clipped:
            meter_color = self.clip_color

        if rms_w > 0:
            self.create_rectangle(0, 0, rms_w, h, fill=meter_color, outline="")

        if peak_w > 0:
            self.create_line(peak_w, 0, peak_w, h, fill="#FFFFFF", width=2)

        for db_mark in [0.2, 0.4, 0.6, 0.8]:
            x = int(w * db_mark)
            self.create_line(x, 0, x, h, fill="#2A2A2A")


class LabeledScale(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        text: str,
        from_: float,
        to: float,
        initial: float,
        command: Callable[[float], None],
        resolution: float = 0.1,
    ) -> None:
        super().__init__(master)
        self.command = command
        self.var = tk.DoubleVar(value=initial)

        self.label = ttk.Label(self, text=text)
        self.label.grid(row=0, column=0, sticky="w")

        self.value_label = ttk.Label(self, text=f"{initial:.2f}", width=8)
        self.value_label.grid(row=0, column=1, sticky="e", padx=(8, 0))

        self.scale = ttk.Scale(
            self,
            from_=from_,
            to=to,
            orient="horizontal",
            command=self._on_scale,
        )
        self.scale.set(initial)
        self.scale.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        self.from_ = from_
        self.to = to
        self.resolution = resolution

        self.columnconfigure(0, weight=1)

    def _on_scale(self, value: str) -> None:
        v = float(value)
        if self.resolution > 0:
            v = round(v / self.resolution) * self.resolution
        v = max(min(v, self.to), self.from_)
        self.value_label.configure(text=f"{v:.2f}")
        self.var.set(v)
        self.command(v)

    def set(self, value: float) -> None:
        self.scale.set(value)
        self._on_scale(str(value))


class BabamicGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_NAME} - {APP_VERSION}")
        self.root.geometry("980x720")
        self.root.minsize(920, 650)

        self.engine = EffectEngine()
        self.controller = AudioController(self.engine)

        self.theme = DEFAULT_COLORS.copy()
        self._configure_style()

        self.devices_cache: list[dict] = []
        self.device_display_to_index: dict[str, int] = {}

        self.effect_var = tk.StringVar(value=EFFECT_NAMES[0])
        self.sample_rate_var = tk.StringVar(value="48000")
        self.block_size_var = tk.StringVar(value="1024")
        self.status_var = tk.StringVar(value="Hazır")
        self.stats_var = tk.StringVar(value="Peak: 0.00 | RMS: 0.00 | Clip: Hayır")

        self.input_device_var = tk.StringVar(value="Varsayılan")
        self.output_device_var = tk.StringVar(value="Varsayılan")

        self._build_layout()
        self._bind_events()
        self.refresh_devices()
        self._schedule_ui_tick()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        self.root.configure(bg=self.theme["bg"])

        style.configure("TFrame", background=self.theme["bg"])
        style.configure("Panel.TFrame", background=self.theme["panel"])
        style.configure("AltPanel.TFrame", background=self.theme["panel_alt"])
        style.configure("TLabel", background=self.theme["bg"], foreground=self.theme["fg"])
        style.configure("Panel.TLabel", background=self.theme["panel"], foreground=self.theme["fg"])
        style.configure("AltPanel.TLabel", background=self.theme["panel_alt"], foreground=self.theme["fg"])
        style.configure("Muted.TLabel", background=self.theme["panel"], foreground=self.theme["muted"])

        style.configure("TButton", padding=8)
        style.configure("Accent.TButton", padding=8)

        style.configure("TEntry", fieldbackground="#2A2A2A", foreground=self.theme["fg"])
        style.configure("TCombobox", fieldbackground="#2A2A2A", foreground=self.theme["fg"])

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=14, pady=14)

        top = ttk.Frame(main, style="Panel.TFrame")
        top.pack(fill="x", pady=(0, 12))

        title = ttk.Label(
            top,
            text=f"{APP_NAME} - Canlı Mikrofon Efektleri",
            style="Panel.TLabel",
            font=("TkDefaultFont", 14, "bold"),
        )
        title.pack(anchor="w", padx=14, pady=(12, 4))

        subtitle = ttk.Label(
            top,
            text="Tkinter GUI / Python / Gerçek zamanlı ses işleme",
            style="Muted.TLabel",
        )
        subtitle.pack(anchor="w", padx=14, pady=(0, 12))

        body = ttk.Frame(main)
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, style="Panel.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = ttk.Frame(body, style="AltPanel.TFrame", width=310)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        self._build_left_panel(left)
        self._build_right_panel(right)

        footer = ttk.Frame(main, style="Panel.TFrame")
        footer.pack(fill="x", pady=(12, 0))

        self.status_label = ttk.Label(footer, textvariable=self.status_var, style="Panel.TLabel")
        self.status_label.pack(side="left", padx=12, pady=10)

        self.stats_label = ttk.Label(footer, textvariable=self.stats_var, style="Panel.TLabel")
        self.stats_label.pack(side="right", padx=12, pady=10)

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        frame = parent

        row0 = ttk.Frame(frame, style="Panel.TFrame")
        row0.pack(fill="x", padx=12, pady=(12, 8))

        ttk.Label(row0, text="Efekt", style="Panel.TLabel").pack(anchor="w")
        self.effect_combo = ttk.Combobox(
            row0,
            textvariable=self.effect_var,
            values=EFFECT_NAMES,
            state="readonly",
        )
        self.effect_combo.pack(fill="x", pady=(4, 0))

        row1 = ttk.Frame(frame, style="Panel.TFrame")
        row1.pack(fill="x", padx=12, pady=8)

        ttk.Label(row1, text="Input cihaz", style="Panel.TLabel").pack(anchor="w")
        self.input_combo = ttk.Combobox(
            row1,
            textvariable=self.input_device_var,
            values=["Varsayılan"],
            state="readonly",
        )
        self.input_combo.pack(fill="x", pady=(4, 10))

        ttk.Label(row1, text="Output cihaz", style="Panel.TLabel").pack(anchor="w")
        self.output_combo = ttk.Combobox(
            row1,
            textvariable=self.output_device_var,
            values=["Varsayılan"],
            state="readonly",
        )
        self.output_combo.pack(fill="x", pady=(4, 0))

        row2 = ttk.Frame(frame, style="Panel.TFrame")
        row2.pack(fill="x", padx=12, pady=8)

        ttk.Label(row2, text="Sample Rate", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        self.sample_rate_combo = ttk.Combobox(
            row2,
            textvariable=self.sample_rate_var,
            values=["16000", "22050", "32000", "44100", "48000", "96000"],
            state="readonly",
            width=12,
        )
        self.sample_rate_combo.grid(row=1, column=0, sticky="w", pady=(4, 0))

        ttk.Label(row2, text="Block Size", style="Panel.TLabel").grid(row=0, column=1, sticky="w", padx=(14, 0))
        self.block_size_combo = ttk.Combobox(
            row2,
            textvariable=self.block_size_var,
            values=["128", "256", "512", "1024", "2048"],
            state="readonly",
            width=12,
        )
        self.block_size_combo.grid(row=1, column=1, sticky="w", padx=(14, 0), pady=(4, 0))

        row3 = ttk.Frame(frame, style="Panel.TFrame")
        row3.pack(fill="x", padx=12, pady=12)

        self.start_button = ttk.Button(row3, text="Başlat", command=self.on_start)
        self.start_button.pack(side="left", padx=(0, 8))

        self.stop_button = ttk.Button(row3, text="Durdur", command=self.on_stop)
        self.stop_button.pack(side="left")

        self.refresh_button = ttk.Button(row3, text="Cihazları Yenile", command=self.refresh_devices)
        self.refresh_button.pack(side="right")

        row4 = ttk.Frame(frame, style="Panel.TFrame")
        row4.pack(fill="x", padx=12, pady=(6, 10))

        ttk.Label(row4, text="Seviye", style="Panel.TLabel").pack(anchor="w")
        self.meter = MeterCanvas(row4, width=540, height=26)
        self.meter.pack(fill="x", pady=(6, 0))

        row5 = ttk.Frame(frame, style="Panel.TFrame")
        row5.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        ttk.Label(row5, text="Sistem Log", style="Panel.TLabel").pack(anchor="w")
        self.log_text = tk.Text(
            row5,
            height=10,
            bg="#0F0F0F",
            fg="#DADADA",
            insertbackground="#DADADA",
            relief="flat",
        )
        self.log_text.pack(fill="both", expand=True, pady=(6, 0))
        self.log_text.configure(state="disabled")

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent, style="AltPanel.TFrame")
        container.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(
            container,
            text="Efekt Kontrolleri",
            style="AltPanel.TLabel",
            font=("TkDefaultFont", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.scales: list[LabeledScale] = []

        s1 = LabeledScale(
            container,
            text="Input Gain (dB)",
            from_=-18,
            to=18,
            initial=0,
            command=self.on_input_gain,
            resolution=0.5,
        )
        s1.pack(fill="x", pady=6)
        self.scales.append(s1)

        s2 = LabeledScale(
            container,
            text="Output Gain (dB)",
            from_=-18,
            to=18,
            initial=0,
            command=self.on_output_gain,
            resolution=0.5,
        )
        s2.pack(fill="x", pady=6)
        self.scales.append(s2)

        s3 = LabeledScale(
            container,
            text="Effect Mix",
            from_=0.0,
            to=1.0,
            initial=1.0,
            command=self.on_effect_mix,
            resolution=0.01,
        )
        s3.pack(fill="x", pady=6)
        self.scales.append(s3)

        s4 = LabeledScale(
            container,
            text="Drive",
            from_=1.0,
            to=8.0,
            initial=2.5,
            command=self.on_drive,
            resolution=0.1,
        )
        s4.pack(fill="x", pady=6)
        self.scales.append(s4)

        s5 = LabeledScale(
            container,
            text="Reverb Wet",
            from_=0.0,
            to=1.0,
            initial=0.22,
            command=self.on_reverb_wet,
            resolution=0.01,
        )
        s5.pack(fill="x", pady=6)
        self.scales.append(s5)

        s6 = LabeledScale(
            container,
            text="Bass Amount",
            from_=1.0,
            to=3.0,
            initial=1.8,
            command=self.on_bass_amount,
            resolution=0.01,
        )
        s6.pack(fill="x", pady=6)
        self.scales.append(s6)

        s7 = LabeledScale(
            container,
            text="Bit Depth",
            from_=2,
            to=12,
            initial=6,
            command=self.on_bit_depth,
            resolution=1,
        )
        s7.pack(fill="x", pady=6)
        self.scales.append(s7)

        s8 = LabeledScale(
            container,
            text="Noise Amount",
            from_=0.0,
            to=0.05,
            initial=0.01,
            command=self.on_noise_amount,
            resolution=0.001,
        )
        s8.pack(fill="x", pady=6)
        self.scales.append(s8)

        button_row = ttk.Frame(container, style="AltPanel.TFrame")
        button_row.pack(fill="x", pady=(10, 0))

        ttk.Button(button_row, text="Preset: Standart", command=self.preset_standard).pack(fill="x", pady=3)
        ttk.Button(button_row, text="Preset: Agresif", command=self.preset_aggressive).pack(fill="x", pady=3)
        ttk.Button(button_row, text="Preset: Temiz", command=self.preset_clean).pack(fill="x", pady=3)

    def _bind_events(self) -> None:
        self.effect_combo.bind("<<ComboboxSelected>>", self.on_effect_change)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, text: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        line = f"[{stamp}] {text}\n"
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def safe_int(self, value: str, fallback: int) -> int:
        try:
            return int(value)
        except Exception:
            return fallback

    def get_device_display_name(self, idx: int, name: str, max_input: int, max_output: int) -> str:
        return f"[{idx}] {name} (in:{max_input}, out:{max_output})"

    def refresh_devices(self) -> None:
        try:
            devices = sd.query_devices()
            self.devices_cache = list(devices)
        except Exception as exc:
            self.log(f"Cihaz listesi alınamadı: {exc}")
            messagebox.showerror(APP_NAME, f"Cihaz listesi alınamadı:\n{exc}")
            return

        self.device_display_to_index.clear()
        input_items = ["Varsayılan"]
        output_items = ["Varsayılan"]

        for i, dev in enumerate(self.devices_cache):
            max_in = int(dev.get("max_input_channels", 0))
            max_out = int(dev.get("max_output_channels", 0))
            name = str(dev.get("name", f"Device {i}"))
            display = self.get_device_display_name(i, name, max_in, max_out)

            if max_in > 0:
                input_items.append(display)
                self.device_display_to_index[display] = i
            if max_out > 0:
                output_items.append(display)
                self.device_display_to_index[display] = i

        self.input_combo["values"] = input_items
        self.output_combo["values"] = output_items

        if self.input_device_var.get() not in input_items:
            self.input_device_var.set("Varsayılan")
        if self.output_device_var.get() not in output_items:
            self.output_device_var.set("Varsayılan")

        self.log("Ses cihazları yenilendi.")

    def _device_index_from_var(self, value: str) -> int | None:
        if value == "Varsayılan":
            return None
        return self.device_display_to_index.get(value)

    def apply_runtime_config(self) -> None:
        sample_rate = self.safe_int(self.sample_rate_var.get(), 48000)
        block_size = self.safe_int(self.block_size_var.get(), 1024)

        input_index = self._device_index_from_var(self.input_device_var.get())
        output_index = self._device_index_from_var(self.output_device_var.get())

        self.controller.set_config(
            sample_rate=sample_rate,
            block_size=block_size,
            input_device=input_index,
            output_device=output_index,
        )
        self.controller.set_effect(self.effect_var.get())

    def on_start(self) -> None:
        if self.controller.running:
            self.log("Akış zaten çalışıyor.")
            return

        self.apply_runtime_config()
        try:
            self.controller.start()
            self.status_var.set("Çalışıyor")
            self.log(
                f"Başlatıldı | Efekt={self.effect_var.get()} | SR={self.sample_rate_var.get()} | BS={self.block_size_var.get()}"
            )
        except Exception as exc:
            self.status_var.set("Hata")
            self.log(f"Başlatma hatası: {exc}")
            messagebox.showerror(APP_NAME, f"Akış başlatılamadı:\n{exc}")

    def on_stop(self) -> None:
        if not self.controller.running:
            self.log("Akış zaten durdurulmuş.")
            return

        self.controller.stop()
        self.status_var.set("Durduruldu")
        self.log("Akış durduruldu.")

    def on_effect_change(self, event=None) -> None:
        _ = event
        name = self.effect_var.get()
        self.controller.set_effect(name)
        self.log(f"Efekt değiştirildi: {name}")

    def on_input_gain(self, value: float) -> None:
        self.engine.params.input_gain_db = float(value)

    def on_output_gain(self, value: float) -> None:
        self.engine.params.output_gain_db = float(value)

    def on_effect_mix(self, value: float) -> None:
        self.engine.params.effect_mix = float(value)

    def on_drive(self, value: float) -> None:
        self.engine.params.drive = float(value)

    def on_reverb_wet(self, value: float) -> None:
        self.engine.params.reverb_wet = float(value)

    def on_bass_amount(self, value: float) -> None:
        self.engine.params.bass_amount = float(value)

    def on_bit_depth(self, value: float) -> None:
        self.engine.params.bit_depth = int(round(value))

    def on_noise_amount(self, value: float) -> None:
        self.engine.params.noise_amount = float(value)

    def preset_standard(self) -> None:
        self._apply_preset(
            input_gain_db=0.0,
            output_gain_db=0.0,
            effect_mix=1.0,
            drive=2.5,
            reverb_wet=0.22,
            bass_amount=1.8,
            bit_depth=6,
            noise_amount=0.01,
        )
        self.log("Preset uygulandı: Standart")

    def preset_aggressive(self) -> None:
        self._apply_preset(
            input_gain_db=2.0,
            output_gain_db=-1.0,
            effect_mix=1.0,
            drive=4.6,
            reverb_wet=0.35,
            bass_amount=2.3,
            bit_depth=4,
            noise_amount=0.015,
        )
        self.log("Preset uygulandı: Agresif")

    def preset_clean(self) -> None:
        self._apply_preset(
            input_gain_db=-1.0,
            output_gain_db=0.5,
            effect_mix=0.72,
            drive=1.7,
            reverb_wet=0.12,
            bass_amount=1.2,
            bit_depth=10,
            noise_amount=0.002,
        )
        self.log("Preset uygulandı: Temiz")

    def _apply_preset(
        self,
        input_gain_db: float,
        output_gain_db: float,
        effect_mix: float,
        drive: float,
        reverb_wet: float,
        bass_amount: float,
        bit_depth: int,
        noise_amount: float,
    ) -> None:
        self.engine.params.input_gain_db = input_gain_db
        self.engine.params.output_gain_db = output_gain_db
        self.engine.params.effect_mix = effect_mix
        self.engine.params.drive = drive
        self.engine.params.reverb_wet = reverb_wet
        self.engine.params.bass_amount = bass_amount
        self.engine.params.bit_depth = bit_depth
        self.engine.params.noise_amount = noise_amount

        mapping: Iterable[tuple[LabeledScale, float]] = [
            (self.scales[0], input_gain_db),
            (self.scales[1], output_gain_db),
            (self.scales[2], effect_mix),
            (self.scales[3], drive),
            (self.scales[4], reverb_wet),
            (self.scales[5], bass_amount),
            (self.scales[6], float(bit_depth)),
            (self.scales[7], noise_amount),
        ]
        for scale, value in mapping:
            scale.set(value)

    def _schedule_ui_tick(self) -> None:
        self.root.after(70, self._ui_tick)

    def _ui_tick(self) -> None:
        for msg in self.controller.read_status_messages():
            self.log(msg)

        meter = self.controller.read_latest_meter()
        if meter is not None:
            peak, rms, clipped = meter
            self.meter.set_level(peak, rms, clipped)
            self.stats_var.set(
                f"Peak: {peak:.2f} | RMS: {rms:.2f} | Clip: {'Evet' if clipped else 'Hayır'}"
            )

        self._schedule_ui_tick()

    def on_close(self) -> None:
        try:
            self.controller.stop()
        except Exception:
            pass
        self.root.destroy()


def main() -> int:
    root = tk.Tk()
    app = BabamicGUI(root)
    app.log("BABAMIC GUI hazır.")
    app.log("Efekti seç, cihazları kontrol et ve Başlat butonuna bas.")
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
