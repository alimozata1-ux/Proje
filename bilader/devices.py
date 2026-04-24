from __future__ import annotations

import platform
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

import psutil
import serial
import serial.tools.list_ports


@dataclass(slots=True)
class ArduinoState:
    connected: bool = False
    port: str | None = None
    baud: int | None = None
    last_error: str = ""


class ArduinoHub:
    def __init__(self, default_port: str, default_baud: int, timeout: float) -> None:
        self.default_port = default_port
        self.default_baud = default_baud
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.state = ArduinoState()

    def available_ports(self) -> list[dict]:
        ports = serial.tools.list_ports.comports()
        return [
            {
                "device": p.device,
                "name": p.name,
                "description": p.description,
                "manufacturer": p.manufacturer,
                "vid": p.vid,
                "pid": p.pid,
            }
            for p in ports
        ]

    def connect(self, port: str | None = None, baud: int | None = None) -> dict:
        if self.serial_conn and self.serial_conn.is_open:
            return {"ok": True, "connected": True, "port": self.state.port}

        target_port = port or self.default_port
        target_baud = baud or self.default_baud

        try:
            self.serial_conn = serial.Serial(
                port=target_port,
                baudrate=target_baud,
                timeout=self.timeout,
            )
            self.state.connected = True
            self.state.port = target_port
            self.state.baud = target_baud
            self.state.last_error = ""
            return {"ok": True, "connected": True, "port": target_port, "baud": target_baud}
        except serial.SerialException as exc:
            self.state.connected = False
            self.state.last_error = str(exc)
            return {"ok": False, "connected": False, "error": str(exc)}

    def disconnect(self) -> dict:
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.state.connected = False
        self.state.port = None
        return {"ok": True, "connected": False}

    def toggle(self) -> dict:
        if self.state.connected:
            return self.disconnect()
        return self.connect()

    def send(self, payload: str, expect_response: bool = True) -> dict:
        if not self.serial_conn or not self.serial_conn.is_open:
            return {"ok": False, "error": "Arduino bağlı değil."}
        try:
            self.serial_conn.write(payload.encode("utf-8"))
            self.serial_conn.flush()
            if not expect_response:
                return {"ok": True, "response": ""}
            time.sleep(0.25)
            raw = self.serial_conn.readline().decode("utf-8", errors="ignore").strip()
            return {"ok": True, "response": raw}
        except Exception as exc:
            self.state.last_error = str(exc)
            return {"ok": False, "error": str(exc)}

    def sensor_temperature(self) -> dict:
        return self.send("T")

    def light_on(self) -> dict:
        return self.send("L1", expect_response=False)

    def light_off(self) -> dict:
        return self.send("L0", expect_response=False)


class SystemHub:
    def snapshot(self) -> dict:
        vm = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.3),
            "ram_percent": vm.percent,
            "ram_total_gb": round(vm.total / 1024**3, 2),
            "ram_available_gb": round(vm.available / 1024**3, 2),
            "disk_percent": du.percent,
            "disk_total_gb": round(du.total / 1024**3, 2),
            "disk_free_gb": round(du.free / 1024**3, 2),
            "boot_time": psutil.boot_time(),
            "platform": platform.platform(),
        }

    def process_table(self, limit: int = 12) -> list[dict]:
        rows = []
        for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
            info = proc.info
            rows.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name"),
                    "cpu": info.get("cpu_percent"),
                    "memory": round(float(info.get("memory_percent") or 0.0), 2),
                }
            )
        rows.sort(key=lambda x: (x["cpu"] or 0, x["memory"] or 0), reverse=True)
        return rows[:limit]

    def open_application(self, app_name: str) -> dict:
        try:
            subprocess.Popen(app_name, shell=True)
            return {"ok": True, "app": app_name}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
