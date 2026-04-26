#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import random
import string
import struct
import time
import urllib.request
import zlib

HEADER_FMT = "<I H Q Q"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
BAG_MAGIC = 0x42414730


def read_header(path: str):
    with open(path, "rb") as f:
        data = f.read(HEADER_SIZE)
    magic, version, entry_count, last_offset = struct.unpack(HEADER_FMT, data)
    return {
        "magic": magic,
        "version": version,
        "entry_count": entry_count,
        "last_offset": last_offset,
    }


def inspect_bag(path: str):
    out = {"file": path, "records": 0, "corruptions": [], "header": None}
    with open(path, "rb") as f:
        hdr = f.read(HEADER_SIZE)
        if len(hdr) != HEADER_SIZE:
            out["corruptions"].append("header too short")
            return out
        magic, version, entry_count, last_offset = struct.unpack(HEADER_FMT, hdr)
        out["header"] = {
            "magic": hex(magic),
            "version": version,
            "entry_count": entry_count,
            "last_offset": last_offset,
        }
        if magic != BAG_MAGIC:
            out["corruptions"].append(f"magic mismatch: got {hex(magic)}")
            return out

        offset = HEADER_SIZE
        idx = 0
        while offset < last_offset:
            f.seek(offset)
            base = f.read(2)
            if len(base) != 2:
                out["corruptions"].append(f"record {idx}: missing key_len")
                break
            (key_len,) = struct.unpack("<H", base)
            key = f.read(key_len)
            dtype = f.read(1)
            payload_len_raw = f.read(8)
            if len(key) != key_len or len(dtype) != 1 or len(payload_len_raw) != 8:
                out["corruptions"].append(f"record {idx}: truncated preamble")
                break

            (payload_len,) = struct.unpack("<Q", payload_len_raw)
            payload = f.read(payload_len)
            crc_raw = f.read(4)
            if len(payload) != payload_len or len(crc_raw) != 4:
                out["corruptions"].append(f"record {idx}: truncated payload")
                break

            (stored_crc,) = struct.unpack("<I", crc_raw)
            calc_crc = zlib.crc32(payload) & 0xFFFFFFFF
            if stored_crc != calc_crc:
                digest = hashlib.sha1(key).hexdigest()[:8]
                out["corruptions"].append(
                    f"record {idx} key={digest}: crc mismatch {stored_crc} != {calc_crc}"
                )
            offset += 2 + key_len + 1 + 8 + payload_len + 4
            idx += 1

        out["records"] = idx
        if idx != entry_count:
            out["corruptions"].append(
                f"entry_count mismatch header={entry_count} scanned={idx}"
            )
    return out


def random_ascii(n: int) -> str:
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))


def make_payload(kind: str):
    if kind == "string":
        return random_ascii(random.randint(16, 1024)).encode("utf-8")
    if kind == "xml":
        body = f"<event><id>{random.randint(1, 999999)}</id><msg>{random_ascii(24)}</msg></event>"
        return body.encode("utf-8")
    size = random.randint(256, 16 * 1024)
    return os.urandom(size)


def stress(base_url: str, count: int, sleep_ms: int):
    sent = 0
    kinds = ["string", "binary", "xml"]
    started = time.time()
    for i in range(count):
        kind = random.choice(kinds)
        payload = make_payload(kind)
        body = {
            "key": f"k_{random_ascii(12)}_{i}",
            "data_type": kind,
            "data": payload.decode("latin1"),
        }
        req = urllib.request.Request(
            f"{base_url}/api/put",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"write failed: {resp.status}")
        sent += 1
        if sleep_ms > 0:
            time.sleep(sleep_ms / 1000.0)

    elapsed = max(time.time() - started, 1e-6)
    print(json.dumps({"sent": sent, "seconds": elapsed, "rps": sent / elapsed}, indent=2))


def main():
    p = argparse.ArgumentParser(description="LİB-BAG tools")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("inspect", help="Inspect a .bag file")
    pi.add_argument("path")

    ps = sub.add_parser("stress", help="Run stress test against engine")
    ps.add_argument("--url", default="http://127.0.0.1:8080")
    ps.add_argument("--count", type=int, default=1000)
    ps.add_argument("--sleep-ms", type=int, default=0)

    args = p.parse_args()
    if args.cmd == "inspect":
        print(json.dumps(inspect_bag(args.path), indent=2))
    elif args.cmd == "stress":
        stress(args.url, args.count, args.sleep_ms)


if __name__ == "__main__":
    main()
