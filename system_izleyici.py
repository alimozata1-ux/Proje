#!/usr/bin/env python3
"""
Linux odaklı sistem izleyici:
- SSD/HDD/NVMe(M.2) disk varlığı ve anlık hız takibi
- Disk hızının eşik altı/üstü alarmı
- RAM kullanımı
- SD Kart / USB bellek tespiti
- CPU kullanımı
- GPU kullanım ve sıcaklık (nvidia-smi varsa)

Kurulum:
  pip install psutil

Çalıştırma örnekleri:
  python system_izleyici.py
  python system_izleyici.py --disk-min-mbps 5 --cpu-max 85 --gpu-max 90 --interval 2
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import psutil


@dataclass
class DiskStatSnapshot:
    read_bytes: int
    write_bytes: int
    ts: float


def read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def list_block_devices() -> List[str]:
    sys_block = "/sys/block"
    try:
        return sorted(os.listdir(sys_block))
    except FileNotFoundError:
        return []


def disk_type_for_device(dev: str) -> str:
    """Linux için disk tipini tahmin eder."""
    if dev.startswith("nvme"):
        return "M.2/NVMe"

    rotational = read_text(f"/sys/block/{dev}/queue/rotational")
    if rotational == "0":
        return "SSD"
    if rotational == "1":
        return "HDD"
    return "Bilinmiyor"


def is_usb_device(dev: str) -> bool:
    real_path = os.path.realpath(f"/sys/block/{dev}")
    return "/usb" in real_path.lower()


def is_sd_card_device(dev: str) -> bool:
    # mmcblk* tipik SD/eMMC aygıt adlandırmasıdır.
    if dev.startswith("mmcblk"):
        return True

    removable = read_text(f"/sys/block/{dev}/removable")
    # USB hariç tak-çıkar aygıtları SD olma ihtimali yüksek diye işaretliyoruz.
    return removable == "1" and not is_usb_device(dev)


def collect_storage_presence() -> Dict[str, List[str]]:
    disks = list_block_devices()
    result = {
        "SSD": [],
        "HDD": [],
        "M.2/NVMe": [],
        "SD": [],
        "USB": [],
    }

    for dev in disks:
        dtype = disk_type_for_device(dev)
        if dtype in result:
            result[dtype].append(dev)

        if is_sd_card_device(dev):
            result["SD"].append(dev)
        if is_usb_device(dev):
            result["USB"].append(dev)

    # tekrarları kaldır
    for key in result:
        result[key] = sorted(set(result[key]))

    return result


def current_disk_counters() -> Dict[str, DiskStatSnapshot]:
    now = time.time()
    counters = psutil.disk_io_counters(perdisk=True) or {}
    out: Dict[str, DiskStatSnapshot] = {}
    for dev, c in counters.items():
        out[dev] = DiskStatSnapshot(read_bytes=c.read_bytes, write_bytes=c.write_bytes, ts=now)
    return out


def disk_speeds_mbps(
    prev: Dict[str, DiskStatSnapshot],
    curr: Dict[str, DiskStatSnapshot],
) -> Dict[str, float]:
    speeds: Dict[str, float] = {}
    for dev, curr_stat in curr.items():
        old = prev.get(dev)
        if not old:
            continue
        dt = curr_stat.ts - old.ts
        if dt <= 0:
            continue
        delta = (curr_stat.read_bytes - old.read_bytes) + (curr_stat.write_bytes - old.write_bytes)
        mbps = (delta / dt) / (1024 * 1024)
        speeds[dev] = max(0.0, mbps)
    return speeds


def nvidia_gpu_stats() -> List[Tuple[str, float, float]]:
    """(isim, kullanım%, sıcaklıkC) döner. nvidia-smi yoksa boş."""
    if not shutil.which("nvidia-smi"):
        return []

    cmd = [
        "nvidia-smi",
        "--query-gpu=name,utilization.gpu,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        raw = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    gpus = []
    for line in raw.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            continue
        name, util_str, temp_str = parts
        try:
            gpus.append((name, float(util_str), float(temp_str)))
        except ValueError:
            continue
    return gpus


def fmt_devices(devs: List[str]) -> str:
    return ", ".join(devs) if devs else "Yok"


def monitor_loop(args: argparse.Namespace) -> None:
    prev = current_disk_counters()
    print("Sistem izleyici başlatıldı. Çıkmak için Ctrl+C.\n")

    while True:
        time.sleep(args.interval)
        curr = current_disk_counters()

        cpu = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        ram_percent = vm.percent
        ram_used_gb = vm.used / (1024**3)
        ram_total_gb = vm.total / (1024**3)

        storage = collect_storage_presence()
        speeds = disk_speeds_mbps(prev, curr)
        gpus = nvidia_gpu_stats()

        print("=" * 70)
        print(f"CPU: %{cpu:.1f}")
        if cpu >= args.cpu_max:
            print(f"[UYARI] CPU kullanımı yüksek! (eşik: %{args.cpu_max})")

        print(f"RAM: %{ram_percent:.1f} ({ram_used_gb:.1f} / {ram_total_gb:.1f} GB)")
        if ram_percent >= args.ram_max:
            print(f"[UYARI] RAM kullanımı yüksek! (eşik: %{args.ram_max})")

        print(f"SSD: {fmt_devices(storage['SSD'])}")
        print(f"HDD: {fmt_devices(storage['HDD'])}")
        print(f"M.2/NVMe: {fmt_devices(storage['M.2/NVMe'])}")
        print(f"SD Kart: {fmt_devices(storage['SD'])}")
        print(f"USB Bellek: {fmt_devices(storage['USB'])}")

        if speeds:
            print("Disk Hızları (MB/s):")
            for dev, mbps in sorted(speeds.items()):
                flag = ""
                if mbps < args.disk_min_mbps:
                    flag = f" [UYARI: {args.disk_min_mbps} MB/s altı]"
                if mbps > args.disk_max_mbps:
                    flag = f" [UYARI: {args.disk_max_mbps} MB/s üstü]"
                print(f"  - {dev}: {mbps:.2f}{flag}")
        else:
            print("Disk hız verisi henüz yok.")

        if gpus:
            print("GPU:")
            for name, util, temp in gpus:
                msg = f"  - {name}: %{util:.1f}, {temp:.0f}°C"
                if util >= args.gpu_max:
                    msg += f" [UYARI: %{args.gpu_max} üstü]"
                print(msg)
        else:
            print("GPU: Veri yok (nvidia-smi bulunamadı ya da NVIDIA GPU yok).")

        prev = curr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SSD/HDD/RAM/CPU/GPU/USB/SD izleyici")
    p.add_argument("--interval", type=float, default=2.0, help="Ölçüm aralığı (saniye)")

    p.add_argument("--cpu-max", type=float, default=85.0, help="CPU kullanım üst eşiği (%)")
    p.add_argument("--ram-max", type=float, default=90.0, help="RAM kullanım üst eşiği (%)")
    p.add_argument("--gpu-max", type=float, default=90.0, help="GPU kullanım üst eşiği (%)")

    p.add_argument("--disk-min-mbps", type=float, default=1.0, help="Disk hız alt eşiği (MB/s)")
    p.add_argument("--disk-max-mbps", type=float, default=1500.0, help="Disk hız üst eşiği (MB/s)")

    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        monitor_loop(args)
    except KeyboardInterrupt:
        print("\nİzleyici sonlandırıldı.")


if __name__ == "__main__":
    main()
