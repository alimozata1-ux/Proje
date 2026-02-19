import random
import string
import subprocess
import sys
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

ALPHABET = string.ascii_uppercase


@dataclass
class Rotor:
    wiring: str
    notch: str
    position: int = 0

    def __post_init__(self) -> None:
        if len(self.wiring) != 26 or sorted(self.wiring) != list(ALPHABET):
            raise ValueError("Rotor wiring must be a 26-char A-Z permutation")
        self.wiring_idx = [ALPHABET.index(c) for c in self.wiring]
        self.reverse_idx = [0] * 26
        for i, mapped in enumerate(self.wiring_idx):
            self.reverse_idx[mapped] = i
        self.notch_idx = ALPHABET.index(self.notch)
        self.position %= 26

    def step(self) -> None:
        self.position = (self.position + 1) % 26

    def at_notch(self) -> bool:
        return self.position == self.notch_idx

    def forward(self, c: int) -> int:
        shifted = (c + self.position) % 26
        wired = self.wiring_idx[shifted]
        return (wired - self.position) % 26

    def backward(self, c: int) -> int:
        shifted = (c + self.position) % 26
        wired = self.reverse_idx[shifted]
        return (wired - self.position) % 26


@dataclass
class Reflector:
    mapping: str

    def __post_init__(self) -> None:
        if len(self.mapping) != 26:
            raise ValueError("Reflector mapping must have length 26")
        self.map_idx = [ALPHABET.index(c) for c in self.mapping]
        for i in range(26):
            if self.map_idx[self.map_idx[i]] != i or self.map_idx[i] == i:
                raise ValueError("Reflector must be symmetric and have no self-map")

    def reflect(self, c: int) -> int:
        return self.map_idx[c]


class Plugboard:
    def __init__(self, spec: str = "") -> None:
        self.map_idx = list(range(26))
        self.parse(spec)

    def parse(self, spec: str) -> None:
        self.map_idx = list(range(26))
        used = set()
        spec = " ".join(spec.upper().split())
        if not spec:
            return
        for pair in spec.split(" "):
            if len(pair) != 2 or pair[0] == pair[1] or any(ch not in ALPHABET for ch in pair):
                raise ValueError(f"Invalid plugboard pair: {pair}")
            a, b = ALPHABET.index(pair[0]), ALPHABET.index(pair[1])
            if a in used or b in used:
                raise ValueError(f"Plugboard letter reused in pair: {pair}")
            used.add(a)
            used.add(b)
            self.map_idx[a], self.map_idx[b] = b, a

    def swap(self, c: int) -> int:
        return self.map_idx[c]


class EnigmaMachine:
    def __init__(self, left: Rotor, middle: Rotor, right: Rotor, reflector: Reflector, plugboard: Plugboard) -> None:
        self.left = left
        self.middle = middle
        self.right = right
        self.reflector = reflector
        self.plugboard = plugboard

    @staticmethod
    def default(positions: tuple[int, int, int], plug_spec: str) -> "EnigmaMachine":
        return EnigmaMachine(
            left=Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q", positions[0]),
            middle=Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E", positions[1]),
            right=Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V", positions[2]),
            reflector=Reflector("YRUHQSLDPXNGOKMIEBFZCWVJAT"),
            plugboard=Plugboard(plug_spec),
        )

    # Enigma double-step mechanism.
    def step_rotors(self) -> None:
        mid_notch = self.middle.at_notch()
        right_notch = self.right.at_notch()
        if mid_notch:
            self.left.step()
        if right_notch or mid_notch:
            self.middle.step()
        self.right.step()

    # Same flow encrypts and decrypts (Enigma symmetry).
    def process_char(self, ch: str) -> str:
        if ch not in ALPHABET:
            return ch
        self.step_rotors()
        c = ALPHABET.index(ch)
        c = self.plugboard.swap(c)
        c = self.right.forward(c)
        c = self.middle.forward(c)
        c = self.left.forward(c)
        c = self.reflector.reflect(c)
        c = self.left.backward(c)
        c = self.middle.backward(c)
        c = self.right.backward(c)
        c = self.plugboard.swap(c)
        return ALPHABET[c]

    def process_message(self, text: str, keep_spaces: bool = True) -> tuple[str, list[str]]:
        out = []
        trace = []
        for ch in text.upper():
            if ch in ALPHABET:
                before = f"{self.left.position:02d}-{self.middle.position:02d}-{self.right.position:02d}"
                encoded = self.process_char(ch)
                after = f"{self.left.position:02d}-{self.middle.position:02d}-{self.right.position:02d}"
                out.append(encoded)
                trace.append(f"{ch} -> {encoded} | rotor {before} -> {after}")
            elif keep_spaces and ch in {" ", "\n", "\t"}:
                out.append(ch)
        return "".join(out), trace


def random_plugboard_pairs(pair_count: int = 5) -> str:
    letters = list(ALPHABET)
    random.shuffle(letters)
    pairs = [letters[i] + letters[i + 1] for i in range(0, pair_count * 2, 2)]
    pairs.sort()
    return " ".join(pairs)


def build_exe() -> tuple[bool, str]:
    try:
        cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--windowed", "main.py"]
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode != 0:
            return False, (run.stderr or run.stdout or "PyInstaller failed").strip()
        return True, "EXE oluşturuldu: dist/main.exe"
    except Exception as exc:
        return False, str(exc)


class EnigmaGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Python Enigma Benzeri Şifreleme")
        root.geometry("980x780")

        self._build_widgets()

    def _build_widgets(self) -> None:
        frm = tk.Frame(self.root, padx=10, pady=10)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Enigma Benzeri Mesaj Şifreleme / Çözme", font=("Arial", 14, "bold")).pack(anchor="w")
        tk.Label(frm, text="A-Z işlenir. Şifrele ve Çöz simetriktir.").pack(anchor="w", pady=(0, 8))

        settings = tk.Frame(frm)
        settings.pack(fill="x")

        tk.Label(settings, text="Sol Rotor (0-25)").grid(row=0, column=0, sticky="w")
        tk.Label(settings, text="Orta Rotor (0-25)").grid(row=0, column=1, sticky="w")
        tk.Label(settings, text="Sağ Rotor (0-25)").grid(row=0, column=2, sticky="w")

        self.left_entry = tk.Entry(settings, width=8)
        self.mid_entry = tk.Entry(settings, width=8)
        self.right_entry = tk.Entry(settings, width=8)
        self.left_entry.grid(row=1, column=0, padx=4, sticky="w")
        self.mid_entry.grid(row=1, column=1, padx=4, sticky="w")
        self.right_entry.grid(row=1, column=2, padx=4, sticky="w")
        self.left_entry.insert(0, "0")
        self.mid_entry.insert(0, "0")
        self.right_entry.insert(0, "0")

        tk.Label(settings, text="Plugboard (örn: AB CD EF)").grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        self.plug_entry = tk.Entry(settings, width=40)
        self.plug_entry.grid(row=3, column=0, columnspan=3, sticky="w")

        self.keep_spaces_var = tk.BooleanVar(value=True)
        self.trace_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings, text="Boşlukları koru", variable=self.keep_spaces_var).grid(row=4, column=0, sticky="w", pady=8)
        tk.Checkbutton(settings, text="Tuş başına rotor izleme", variable=self.trace_var).grid(row=4, column=1, sticky="w", pady=8)

        tk.Label(frm, text="Giriş Mesajı").pack(anchor="w")
        self.input_text = scrolledtext.ScrolledText(frm, height=6)
        self.input_text.pack(fill="x", pady=(0, 8))

        btns1 = tk.Frame(frm)
        btns1.pack(fill="x", pady=(0, 4))
        tk.Button(btns1, text="Şifrele", command=self.encrypt).pack(side="left", padx=4)
        tk.Button(btns1, text="Çöz", command=self.decrypt).pack(side="left", padx=4)
        tk.Button(btns1, text="Sıfırla", command=self.reset).pack(side="left", padx=4)
        tk.Button(btns1, text="Girdi/Çıktı Değiştir", command=self.swap_in_out).pack(side="left", padx=4)

        btns2 = tk.Frame(frm)
        btns2.pack(fill="x", pady=(0, 8))
        tk.Button(btns2, text="Rastgele Ayar", command=self.randomize).pack(side="left", padx=4)
        tk.Button(btns2, text="Çıktıyı Girdiye Kopyala", command=self.copy_out_to_in).pack(side="left", padx=4)
        tk.Button(btns2, text="EXE Yapıcı", command=self.make_exe).pack(side="left", padx=4)

        tk.Label(frm, text="Çıktı Mesajı").pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(frm, height=6)
        self.output_text.pack(fill="x", pady=(0, 8))

        tk.Label(frm, text="Rotor İzleme").pack(anchor="w")
        self.trace_text = scrolledtext.ScrolledText(frm, height=10)
        self.trace_text.pack(fill="both", expand=True)

        self.rotor_state = tk.StringVar(value="Rotorlar (L-M-R): 0-0-0")
        self.status = tk.StringVar(value="Hazır")
        tk.Label(frm, textvariable=self.rotor_state).pack(anchor="w", pady=(6, 0))
        tk.Label(frm, textvariable=self.status, fg="blue").pack(anchor="w")

    def _read_positions(self) -> tuple[int, int, int]:
        try:
            l = int(self.left_entry.get().strip())
            m = int(self.mid_entry.get().strip())
            r = int(self.right_entry.get().strip())
        except ValueError as exc:
            raise ValueError("Rotor değerleri tam sayı olmalı") from exc
        for val in (l, m, r):
            if val < 0 or val > 25:
                raise ValueError("Rotor değerleri 0-25 arasında olmalı")
        return l, m, r

    def _process(self, action: str) -> None:
        try:
            machine = EnigmaMachine.default(self._read_positions(), self.plug_entry.get().strip())
            text = self.input_text.get("1.0", "end-1c")
            output, trace = machine.process_message(text, self.keep_spaces_var.get())
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", output)
            self.rotor_state.set(
                f"Rotorlar (L-M-R): {machine.left.position}-{machine.middle.position}-{machine.right.position}"
            )
            self.trace_text.delete("1.0", "end")
            if self.trace_var.get():
                self.trace_text.insert("1.0", "\n".join(trace))
            self.status.set(f"{action} tamamlandı")
        except Exception as exc:
            messagebox.showerror("Hata", str(exc))
            self.status.set(f"Hata: {exc}")

    def encrypt(self) -> None:
        self._process("Şifreleme")

    def decrypt(self) -> None:
        self._process("Çözme")

    def reset(self) -> None:
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.trace_text.delete("1.0", "end")
        self.left_entry.delete(0, "end")
        self.mid_entry.delete(0, "end")
        self.right_entry.delete(0, "end")
        self.left_entry.insert(0, "0")
        self.mid_entry.insert(0, "0")
        self.right_entry.insert(0, "0")
        self.plug_entry.delete(0, "end")
        self.keep_spaces_var.set(True)
        self.trace_var.set(True)
        self.rotor_state.set("Rotorlar (L-M-R): 0-0-0")
        self.status.set("Sıfırlandı")

    def randomize(self) -> None:
        self.left_entry.delete(0, "end")
        self.mid_entry.delete(0, "end")
        self.right_entry.delete(0, "end")
        self.left_entry.insert(0, str(random.randint(0, 25)))
        self.mid_entry.insert(0, str(random.randint(0, 25)))
        self.right_entry.insert(0, str(random.randint(0, 25)))
        self.plug_entry.delete(0, "end")
        self.plug_entry.insert(0, random_plugboard_pairs(5))
        self.status.set("Rastgele ayarlar üretildi")

    def swap_in_out(self) -> None:
        i = self.input_text.get("1.0", "end-1c")
        o = self.output_text.get("1.0", "end-1c")
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.input_text.insert("1.0", o)
        self.output_text.insert("1.0", i)
        self.status.set("Girdi/çıktı alanları değiştirildi")

    def copy_out_to_in(self) -> None:
        o = self.output_text.get("1.0", "end-1c")
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", o)
        self.status.set("Çıktı girdiye kopyalandı")

    def make_exe(self) -> None:
        ok, msg = build_exe()
        if ok:
            messagebox.showinfo("EXE Yapıcı", msg)
            self.status.set(msg)
        else:
            messagebox.showerror("EXE Yapıcı", msg)
            self.status.set(f"EXE hatası: {msg}")


def main() -> None:
    root = tk.Tk()
    EnigmaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
