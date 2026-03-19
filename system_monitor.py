#!/usr/bin/env python3
"""
Gelişmiş Sistem İzleyici

İzlenen bileşenler:
- CPU kullanımı / frekansı
- GPU kullanımı (nvidia-smi veya GPUtil varsa)
- RAM kullanımı
- Disk türleri (SSD/HDD/NVMe-M.2) ve okuma/yazma hızları
- USB depolama aygıtı takılı mı
- SD kart takılı mı

Not:
- Bazı bilgiler işletim sistemi ve yetkilere göre kısıtlı olabilir.
- Linux üzerinde /sys/class/block kullanılarak SSD/HDD/NVMe tespiti yapılır.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil


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


def _linux_block_device_info(device: str) -> Dict[str, Any]:
    """/dev/sda -> {'kind': 'HDD/SSD/NVMe', 'removable': bool, 'interface': str}"""
    result = {"kind": "Bilinmiyor", "removable": False, "interface": "Bilinmiyor"}
    dev_name = Path(device).name

    # partition ise disk adını bul (sda1 -> sda, nvme0n1p1 -> nvme0n1)
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

    # transport bilgisi (usb/sata vb.)
    uevent = _safe_read(sys_block / "device/uevent") or ""
    if "DRIVER=usb-storage" in uevent:
        result["interface"] = "USB"

    return result


def get_storage_devices() -> List[DeviceInfo]:
    devices: List[DeviceInfo] = []
    seen: set[str] = set()

    for p in psutil.disk_partitions(all=True):
        if p.device in seen or not p.device.startswith("/dev/"):
            continue
        seen.add(p.device)

        kind = "Bilinmiyor"
        removable = False
        interface = "Bilinmiyor"

        if platform.system().lower() == "linux":
            info = _linux_block_device_info(p.device)
            kind = info["kind"]
            removable = info["removable"]
            interface = info["interface"]

        devices.append(
            DeviceInfo(
                name=p.device,
                mountpoint=p.mountpoint,
                fs_type=p.fstype,
                removable=removable,
                interface=interface,
                kind=kind,
            )
        )

    return devices


def _detect_gpu_usage() -> Optional[float]:
    """GPU kullanımını % döndür. Yoksa None."""
    # 1) nvidia-smi
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

    # 2) GPUtil (opsiyonel)
    try:
        import GPUtil  # type: ignore

        gpus = GPUtil.getGPUs()
        if gpus:
            vals = [gpu.load * 100.0 for gpu in gpus]
            return sum(vals) / len(vals)
    except Exception:
        pass

    return None


def _disk_speed_interval(interval: float = 1.0) -> Dict[str, float]:
    io1 = psutil.disk_io_counters()
    time.sleep(interval)
    io2 = psutil.disk_io_counters()

    if not io1 or not io2:
        return {"read_mb_s": 0.0, "write_mb_s": 0.0}

    read_speed = (io2.read_bytes - io1.read_bytes) / (1024 * 1024 * interval)
    write_speed = (io2.write_bytes - io1.write_bytes) / (1024 * 1024 * interval)
    return {"read_mb_s": max(0.0, read_speed), "write_mb_s": max(0.0, write_speed)}


def classify_external_devices(devices: List[DeviceInfo]) -> Dict[str, bool]:
    usb = any(d.interface == "USB" or "usb" in d.name.lower() for d in devices)
    sd = any("mmc" in d.name.lower() or "sd" in d.kind.lower() for d in devices)
    has_m2 = any("nvme" in d.kind.lower() for d in devices)
    has_ssd = any("ssd" in d.kind.lower() for d in devices)
    has_hdd = any("hdd" in d.kind.lower() for d in devices)

    return {
        "usb_takili": usb,
        "sd_kart_takili": sd,
        "m2_nvme_takili": has_m2,
        "ssd_takili": has_ssd,
        "hdd_takili": has_hdd,
    }


def collect_snapshot(th: Thresholds) -> Dict[str, Any]:
    cpu_percent = psutil.cpu_percent(interval=1.0)
    cpu_freq = psutil.cpu_freq()
    ram = psutil.virtual_memory()
    disk_speeds = _disk_speed_interval(interval=1.0)
    gpu_percent = _detect_gpu_usage()
    devices = get_storage_devices()
    flags = classify_external_devices(devices)

    alerts: List[str] = []

    if cpu_percent >= th.max_cpu_percent:
        alerts.append(f"CPU kullanımı çok yüksek: %{cpu_percent:.1f}")

    if ram.percent >= th.max_ram_percent:
        alerts.append(f"RAM kullanımı çok yüksek: %{ram.percent:.1f}")

    if disk_speeds["read_mb_s"] < th.min_disk_read_mb_s:
        alerts.append(
            f"Disk okuma hızı düşük: {disk_speeds['read_mb_s']:.2f} MB/s (< {th.min_disk_read_mb_s} MB/s)"
        )

    if disk_speeds["write_mb_s"] < th.min_disk_write_mb_s:
        alerts.append(
            f"Disk yazma hızı düşük: {disk_speeds['write_mb_s']:.2f} MB/s (< {th.min_disk_write_mb_s} MB/s)"
        )

    if gpu_percent is not None and gpu_percent >= th.max_gpu_percent:
        alerts.append(f"GPU kullanımı çok yüksek: %{gpu_percent:.1f}")

    snapshot = {
        "system": {
            "platform": platform.platform(),
            "cpu_percent": cpu_percent,
            "cpu_freq_mhz": cpu_freq.current if cpu_freq else None,
            "ram_total_gb": ram.total / (1024**3),
            "ram_used_percent": ram.percent,
            "gpu_percent": gpu_percent,
        },
        "storage": {
            "read_mb_s": disk_speeds["read_mb_s"],
            "write_mb_s": disk_speeds["write_mb_s"],
            "devices": [asdict(d) for d in devices],
            **flags,
        },
        "alerts": alerts,
    }
    return snapshot


def pretty_print(snapshot: Dict[str, Any]) -> None:
    s = snapshot["system"]
    st = snapshot["storage"]

    print("\n=== Sistem Özeti ===")
    print(f"Platform      : {s['platform']}")
    print(f"CPU Kullanımı : %{s['cpu_percent']:.1f}")
    print(f"CPU Frekans   : {s['cpu_freq_mhz']:.0f} MHz" if s["cpu_freq_mhz"] else "CPU Frekans   : Bilinmiyor")
    print(f"RAM Kullanımı : %{s['ram_used_percent']:.1f} / {s['ram_total_gb']:.1f} GB")
    if s["gpu_percent"] is None:
        print("GPU Kullanımı : Tespit edilemedi")
    else:
        print(f"GPU Kullanımı : %{s['gpu_percent']:.1f}")

    print("\n=== Depolama ===")
    print(f"Okuma Hızı    : {st['read_mb_s']:.2f} MB/s")
    print(f"Yazma Hızı    : {st['write_mb_s']:.2f} MB/s")
    print(f"SSD Takılı    : {'Evet' if st['ssd_takili'] else 'Hayır'}")
    print(f"HDD Takılı    : {'Evet' if st['hdd_takili'] else 'Hayır'}")
    print(f"M.2/NVMe      : {'Evet' if st['m2_nvme_takili'] else 'Hayır'}")
    print(f"USB Bellek    : {'Evet' if st['usb_takili'] else 'Hayır'}")
    print(f"SD Kart       : {'Evet' if st['sd_kart_takili'] else 'Hayır'}")

    if st["devices"]:
        print("\nAygıtlar:")
        for d in st["devices"]:
            print(
                f"- {d['name']} | {d['kind']} | {d['interface']} | removable={d['removable']} | {d['mountpoint']}"
            )

    print("\n=== Uyarılar ===")
    if snapshot["alerts"]:
        for a in snapshot["alerts"]:
            print(f"! {a}")
    else:
        print("Uyarı yok.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SSD/HDD/USB/SD/CPU/GPU/RAM izleyici")
    p.add_argument("--json", action="store_true", help="JSON çıktı ver")
    p.add_argument("--watch", type=int, default=0, help="N saniyede bir sürekli izle (0=tek sefer)")
    p.add_argument("--min-read", type=float, default=5.0, help="Min disk okuma hızı MB/s")
    p.add_argument("--min-write", type=float, default=5.0, help="Min disk yazma hızı MB/s")
    p.add_argument("--max-cpu", type=float, default=90.0, help="Maks CPU kullanım eşiği %")
    p.add_argument("--max-ram", type=float, default=90.0, help="Maks RAM kullanım eşiği %")
    p.add_argument("--max-gpu", type=float, default=90.0, help="Maks GPU kullanım eşiği %")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    th = Thresholds(
        min_disk_read_mb_s=args.min_read,
        min_disk_write_mb_s=args.min_write,
        max_cpu_percent=args.max_cpu,
        max_ram_percent=args.max_ram,
        max_gpu_percent=args.max_gpu,
    )

    while True:
        snap = collect_snapshot(th)
        if args.json:
            print(json.dumps(snap, ensure_ascii=False, indent=2))
        else:
            pretty_print(snap)

        if args.watch <= 0:
            break
        time.sleep(args.watch)


if __name__ == "__main__":
    main()
