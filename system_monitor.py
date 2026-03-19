#!/usr/bin/env python3
"""Gelişmiş Sistem İzleyici (psutil zorunlu değildir)."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import platform
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PSUTIL_AVAILABLE = importlib.util.find_spec("psutil") is not None
if PSUTIL_AVAILABLE:
    psutil = importlib.import_module("psutil")
else:
    psutil = None


@dataclass
class Thresholds:
    min_disk_read_mb_s: float = 5.0
    min_disk_write_mb_s: float = 5.0
    max_cpu_percent: float = 90.0
    max_ram_percent: float = 90.0
    max_gpu_percent: float = 90.0


@dataclass
class DeviceInfo:
    name: str
    mountpoint: Optional[str]
    fs_type: Optional[str]
    removable: bool
    interface: str
    kind: str


def _safe_read(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return None


def _read_proc_stat_cpu() -> Optional[Tuple[int, int]]:
    data = _safe_read(Path("/proc/stat"))
    if not data:
        return None
    line = data.splitlines()[0]
    parts = [int(x) for x in line.split()[1:]]
    idle = parts[3] + (parts[4] if len(parts) > 4 else 0)
    total = sum(parts)
    return idle, total


def _cpu_percent_linux(interval: float = 1.0) -> float:
    a = _read_proc_stat_cpu()
    time.sleep(interval)
    b = _read_proc_stat_cpu()
    if not a or not b:
        return 0.0
    idle_delta = b[0] - a[0]
    total_delta = b[1] - a[1]
    if total_delta <= 0:
        return 0.0
    return max(0.0, min(100.0, 100.0 * (1.0 - idle_delta / total_delta)))


def _cpu_freq_linux_mhz() -> Optional[float]:
    text = _safe_read(Path("/proc/cpuinfo"))
    if not text:
        return None
    for line in text.splitlines():
        if "cpu MHz" in line:
            try:
                return float(line.split(":", 1)[1].strip())
            except Exception:
                return None
    return None


def _ram_usage_linux() -> Tuple[float, float]:
    """return total_gb, used_percent"""
    text = _safe_read(Path("/proc/meminfo"))
    if not text:
        return 0.0, 0.0
    vals: Dict[str, int] = {}
    for line in text.splitlines():
        key, rest = line.split(":", 1)
        vals[key] = int(rest.strip().split()[0])
    total = vals.get("MemTotal", 0)
    avail = vals.get("MemAvailable", vals.get("MemFree", 0))
    used = max(0, total - avail)
    if total == 0:
        return 0.0, 0.0
    return total / (1024 * 1024), (used / total) * 100.0


def _disk_io_linux() -> Tuple[int, int]:
    """read_bytes, write_bytes (aggregated)"""
    text = _safe_read(Path("/proc/diskstats"))
    if not text:
        return 0, 0
    read_sectors = 0
    write_sectors = 0
    for line in text.splitlines():
        p = line.split()
        if len(p) < 14:
            continue
        name = p[2]
        if name.startswith(("loop", "ram")):
            continue
        read_sectors += int(p[5])
        write_sectors += int(p[9])
    return read_sectors * 512, write_sectors * 512


def _disk_speed_interval(interval: float = 1.0) -> Dict[str, float]:
    if PSUTIL_AVAILABLE:
        io1 = psutil.disk_io_counters()
        time.sleep(interval)
        io2 = psutil.disk_io_counters()
        if not io1 or not io2:
            return {"read_mb_s": 0.0, "write_mb_s": 0.0}
        read_speed = (io2.read_bytes - io1.read_bytes) / (1024 * 1024 * interval)
        write_speed = (io2.write_bytes - io1.write_bytes) / (1024 * 1024 * interval)
        return {"read_mb_s": max(0.0, read_speed), "write_mb_s": max(0.0, write_speed)}

    r1, w1 = _disk_io_linux()
    time.sleep(interval)
    r2, w2 = _disk_io_linux()
    return {
        "read_mb_s": max(0.0, (r2 - r1) / (1024 * 1024 * interval)),
        "write_mb_s": max(0.0, (w2 - w1) / (1024 * 1024 * interval)),
    }


def _linux_block_device_info(device: str) -> Dict[str, Any]:
    result = {"kind": "Bilinmiyor", "removable": False, "interface": "Bilinmiyor"}
    dev_name = Path(device).name
    base = re.sub(r"p?\d+$", "", dev_name)
    sys_block = Path("/sys/class/block") / base
    if not sys_block.exists():
        return result

    rotational = _safe_read(sys_block / "queue/rotational")
    if rotational == "0":
        result["kind"] = "SSD"
    elif rotational == "1":
        result["kind"] = "HDD"

    if base.startswith("nvme"):
        result["kind"] = "NVMe (M.2 olası)"
        result["interface"] = "NVMe"
    elif base.startswith("sd"):
        result["interface"] = "SATA/USB"
    elif base.startswith("mmc"):
        result["interface"] = "MMC/SD"
        result["kind"] = "SD/eMMC"

    removable = _safe_read(sys_block / "removable")
    result["removable"] = removable == "1"

    uevent = _safe_read(sys_block / "device/uevent") or ""
    if "DRIVER=usb-storage" in uevent:
        result["interface"] = "USB"
    return result


def _disk_partitions_linux() -> List[Tuple[str, str, str]]:
    mounts = _safe_read(Path("/proc/mounts"))
    out: List[Tuple[str, str, str]] = []
    if not mounts:
        return out
    for line in mounts.splitlines():
        dev, mnt, fstype = line.split()[:3]
        if dev.startswith("/dev/"):
            out.append((dev, mnt, fstype))
    return out


def get_storage_devices() -> List[DeviceInfo]:
    devices: List[DeviceInfo] = []
    seen: set[str] = set()

    if PSUTIL_AVAILABLE:
        rows = [(p.device, p.mountpoint, p.fstype) for p in psutil.disk_partitions(all=True)]
    else:
        rows = _disk_partitions_linux()

    for device, mountpoint, fstype in rows:
        if device in seen:
            continue
        seen.add(device)

        kind = "Bilinmiyor"
        removable = False
        interface = "Bilinmiyor"
        if platform.system().lower() == "linux":
            info = _linux_block_device_info(device)
            kind = info["kind"]
            removable = info["removable"]
            interface = info["interface"]

        devices.append(DeviceInfo(device, mountpoint, fstype, removable, interface, kind))
    return devices


def _detect_gpu_usage() -> Optional[float]:
    try:
        proc = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            vals = [float(x.strip()) for x in proc.stdout.splitlines() if x.strip()]
            if vals:
                return sum(vals) / len(vals)
    except Exception:
        pass

    if importlib.util.find_spec("GPUtil") is not None:
        gputil = importlib.import_module("GPUtil")
        gpus = gputil.getGPUs()
        if gpus:
            return sum(g.load * 100.0 for g in gpus) / len(gpus)
    return None


def classify_external_devices(devices: List[DeviceInfo]) -> Dict[str, bool]:
    return {
        "usb_takili": any(d.interface == "USB" or "usb" in d.name.lower() for d in devices),
        "sd_kart_takili": any("mmc" in d.name.lower() or "sd" in d.kind.lower() for d in devices),
        "m2_nvme_takili": any("nvme" in d.kind.lower() for d in devices),
        "ssd_takili": any("ssd" in d.kind.lower() for d in devices),
        "hdd_takili": any("hdd" in d.kind.lower() for d in devices),
    }


def collect_snapshot(th: Thresholds) -> Dict[str, Any]:
    if PSUTIL_AVAILABLE:
        cpu_percent = psutil.cpu_percent(interval=1.0)
        cpu_freq_mhz = psutil.cpu_freq().current if psutil.cpu_freq() else None
        mem = psutil.virtual_memory()
        ram_total_gb = mem.total / (1024**3)
        ram_percent = mem.percent
    else:
        cpu_percent = _cpu_percent_linux(interval=1.0)
        cpu_freq_mhz = _cpu_freq_linux_mhz()
        ram_total_gb, ram_percent = _ram_usage_linux()

    disk_speeds = _disk_speed_interval(interval=1.0)
    gpu_percent = _detect_gpu_usage()
    devices = get_storage_devices()
    flags = classify_external_devices(devices)

    alerts: List[str] = []
    if cpu_percent >= th.max_cpu_percent:
        alerts.append(f"CPU kullanımı çok yüksek: %{cpu_percent:.1f}")
    if ram_percent >= th.max_ram_percent:
        alerts.append(f"RAM kullanımı çok yüksek: %{ram_percent:.1f}")
    if disk_speeds["read_mb_s"] < th.min_disk_read_mb_s:
        alerts.append(f"Disk okuma hızı düşük: {disk_speeds['read_mb_s']:.2f} MB/s (< {th.min_disk_read_mb_s} MB/s)")
    if disk_speeds["write_mb_s"] < th.min_disk_write_mb_s:
        alerts.append(f"Disk yazma hızı düşük: {disk_speeds['write_mb_s']:.2f} MB/s (< {th.min_disk_write_mb_s} MB/s)")
    if gpu_percent is not None and gpu_percent >= th.max_gpu_percent:
        alerts.append(f"GPU kullanımı çok yüksek: %{gpu_percent:.1f}")

    return {
        "system": {
            "platform": platform.platform(),
            "cpu_percent": cpu_percent,
            "cpu_freq_mhz": cpu_freq_mhz,
            "ram_total_gb": ram_total_gb,
            "ram_used_percent": ram_percent,
            "gpu_percent": gpu_percent,
            "psutil_available": PSUTIL_AVAILABLE,
        },
        "storage": {
            "read_mb_s": disk_speeds["read_mb_s"],
            "write_mb_s": disk_speeds["write_mb_s"],
            "devices": [asdict(d) for d in devices],
            **flags,
        },
        "alerts": alerts,
    }


def pretty_print(snapshot: Dict[str, Any]) -> None:
    s, st = snapshot["system"], snapshot["storage"]
    print("\n=== Sistem Özeti ===")
    print(f"Platform      : {s['platform']}")
    print(f"CPU Kullanımı : %{s['cpu_percent']:.1f}")
    print(f"CPU Frekans   : {s['cpu_freq_mhz']:.0f} MHz" if s["cpu_freq_mhz"] else "CPU Frekans   : Bilinmiyor")
    print(f"RAM Kullanımı : %{s['ram_used_percent']:.1f} / {s['ram_total_gb']:.1f} GB")
    print("GPU Kullanımı : Tespit edilemedi" if s["gpu_percent"] is None else f"GPU Kullanımı : %{s['gpu_percent']:.1f}")
    print(f"psutil        : {'Var' if s.get('psutil_available') else 'Yok (fallback aktif)'}")

    print("\n=== Depolama ===")
    print(f"Okuma Hızı    : {st['read_mb_s']:.2f} MB/s")
    print(f"Yazma Hızı    : {st['write_mb_s']:.2f} MB/s")
    print(f"SSD Takılı    : {'Evet' if st['ssd_takili'] else 'Hayır'}")
    print(f"HDD Takılı    : {'Evet' if st['hdd_takili'] else 'Hayır'}")
    print(f"M.2/NVMe      : {'Evet' if st['m2_nvme_takili'] else 'Hayır'}")
    print(f"USB Bellek    : {'Evet' if st['usb_takili'] else 'Hayır'}")
    print(f"SD Kart       : {'Evet' if st['sd_kart_takili'] else 'Hayır'}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SSD/HDD/USB/SD/CPU/GPU/RAM izleyici")
    p.add_argument("--json", action="store_true")
    p.add_argument("--watch", type=int, default=0)
    p.add_argument("--min-read", type=float, default=5.0)
    p.add_argument("--min-write", type=float, default=5.0)
    p.add_argument("--max-cpu", type=float, default=90.0)
    p.add_argument("--max-ram", type=float, default=90.0)
    p.add_argument("--max-gpu", type=float, default=90.0)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    th = Thresholds(args.min_read, args.min_write, args.max_cpu, args.max_ram, args.max_gpu)
    while True:
        snap = collect_snapshot(th)
        print(json.dumps(snap, ensure_ascii=False, indent=2) if args.json else "")
        if not args.json:
            pretty_print(snap)
        if args.watch <= 0:
            break
        time.sleep(args.watch)


if __name__ == "__main__":
    main()
