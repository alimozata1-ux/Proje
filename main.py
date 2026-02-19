import random
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from tkinter import ttk
import json

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

    def step_rotors(self) -> None:
        mid_notch = self.middle.at_notch()
        right_notch = self.right.at_notch()
        if mid_notch:
            self.left.step()
        if right_notch or mid_notch:
            self.middle.step()
        self.right.step()

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
        self.root.title("Python Enigma - Modern Arayüz")
        self.root.geometry("1120x760")
        self.root.minsize(980, 680)

        self._setup_theme()
        self._build_widgets()

    def _setup_theme(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        bg = "#f4f6fb"
        card_bg = "#ffffff"
        primary = "#1f6feb"

        self.root.configure(bg=bg)
        style.configure("App.TFrame", background=bg)
        style.configure("Card.TLabelframe", background=card_bg)
        style.configure("Card.TLabelframe.Label", background=card_bg, foreground="#1f2937", font=("Segoe UI", 10, "bold"))
        style.configure("Header.TLabel", background=bg, foreground="#0f172a", font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel", background=bg, foreground="#475569", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=bg, foreground="#0b3d91", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", padding=8)
        style.map("Primary.TButton", background=[("active", "#2b7cff"), ("!active", primary)], foreground=[("!disabled", "white")])

    def _build_widgets(self) -> None:
        main = ttk.Frame(self.root, style="App.TFrame", padding=14)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Enigma Benzeri Mesaj Şifreleme / Çözme", style="Header.TLabel").pack(anchor="w")
        ttk.Label(main, text="Daha modern ve anlaşılır düzen: ayarlar solda, metin ve izleme sağda.", style="Sub.TLabel").pack(anchor="w", pady=(0, 10))

        body = ttk.Panedwindow(main, orient="horizontal")
        body.pack(fill="both", expand=True)

        left_panel = ttk.Frame(body, style="App.TFrame")
        right_panel = ttk.Frame(body, style="App.TFrame")
        body.add(left_panel, weight=1)
        body.add(right_panel, weight=3)

        settings_card = ttk.LabelFrame(left_panel, text="Ayarlar", style="Card.TLabelframe", padding=12)
        settings_card.pack(fill="x", pady=(0, 8))

        ttk.Label(settings_card, text="Sol Rotor (0-25)").grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Label(settings_card, text="Orta Rotor (0-25)").grid(row=2, column=0, sticky="w", pady=(4, 4))
        ttk.Label(settings_card, text="Sağ Rotor (0-25)").grid(row=4, column=0, sticky="w", pady=(4, 4))

        self.left_entry = ttk.Entry(settings_card, width=12)
        self.mid_entry = ttk.Entry(settings_card, width=12)
        self.right_entry = ttk.Entry(settings_card, width=12)
        self.left_entry.grid(row=1, column=0, sticky="ew")
        self.mid_entry.grid(row=3, column=0, sticky="ew")
        self.right_entry.grid(row=5, column=0, sticky="ew")

        ttk.Label(settings_card, text="Plugboard (örn: AB CD EF)").grid(row=6, column=0, sticky="w", pady=(8, 4))
        self.plug_entry = ttk.Entry(settings_card)
        self.plug_entry.grid(row=7, column=0, sticky="ew")

        self.keep_spaces_var = tk.BooleanVar(value=True)
        self.trace_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_card, text="Boşlukları koru", variable=self.keep_spaces_var).grid(row=8, column=0, sticky="w", pady=(8, 2))
        ttk.Checkbutton(settings_card, text="Tuş başına rotor izleme", variable=self.trace_var).grid(row=9, column=0, sticky="w")

        settings_card.columnconfigure(0, weight=1)

        actions_card = ttk.LabelFrame(left_panel, text="Hızlı İşlemler", style="Card.TLabelframe", padding=12)
        actions_card.pack(fill="x", pady=(0, 8))

        ttk.Button(actions_card, text="Şifrele", command=self.encrypt, style="Primary.TButton").pack(fill="x", pady=2)
        ttk.Button(actions_card, text="Çöz", command=self.decrypt).pack(fill="x", pady=2)
        ttk.Button(actions_card, text="Sıfırla", command=self.reset).pack(fill="x", pady=2)
        ttk.Separator(actions_card, orient="horizontal").pack(fill="x", pady=8)
        ttk.Button(actions_card, text="Rastgele Ayar", command=self.randomize).pack(fill="x", pady=2)
        ttk.Button(actions_card, text="Girdi / Çıktı Değiştir", command=self.swap_in_out).pack(fill="x", pady=2)
        ttk.Button(actions_card, text="Çıktıyı Girdiye Kopyala", command=self.copy_out_to_in).pack(fill="x", pady=2)
        ttk.Button(actions_card, text="Çıktıyı Panoya Kopyala", command=self.copy_output_to_clipboard).pack(fill="x", pady=2)
        ttk.Button(actions_card, text="Profili Kaydet (.json)", command=self.save_profile_file).pack(fill="x", pady=2)
        ttk.Button(actions_card, text="Profil Yükle (.json)", command=self.load_profile_file).pack(fill="x", pady=2)
        ttk.Button(actions_card, text="Şifreyi .Password Olarak Kaydet", command=self.save_password_file).pack(fill="x", pady=2)
        ttk.Button(actions_card, text="EXE Yapıcı", command=self.make_exe).pack(fill="x", pady=2)

        info_card = ttk.LabelFrame(left_panel, text="Durum", style="Card.TLabelframe", padding=12)
        info_card.pack(fill="x")

        self.rotor_state = tk.StringVar(value="Rotorlar (L-M-R): 0-0-0")
        self.status = tk.StringVar(value="Hazır")
        ttk.Label(info_card, textvariable=self.rotor_state).pack(anchor="w")
        ttk.Label(info_card, textvariable=self.status, style="Status.TLabel", wraplength=250).pack(anchor="w", pady=(4, 0))
        self.stats_var = tk.StringVar(value="Girdi: 0 karakter | Çıktı: 0 karakter")
        ttk.Label(info_card, textvariable=self.stats_var, wraplength=250).pack(anchor="w", pady=(4, 0))

        message_card = ttk.LabelFrame(right_panel, text="Mesaj Alanı", style="Card.TLabelframe", padding=10)
        message_card.pack(fill="both", expand=True, pady=(0, 8))

        ttk.Label(message_card, text="Giriş Mesajı").pack(anchor="w")
        self.input_text = scrolledtext.ScrolledText(message_card, height=8, font=("Consolas", 10), relief="flat", bd=1)
        self.input_text.pack(fill="x", pady=(2, 8))
        self.input_text.bind("<KeyRelease>", lambda _e: self.update_stats())

        ttk.Label(message_card, text="Çıktı Mesajı").pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(message_card, height=8, font=("Consolas", 10), relief="flat", bd=1)
        self.output_text.pack(fill="x", pady=(2, 0))

        trace_card = ttk.LabelFrame(right_panel, text="Rotor İzleme (Tuş Bazlı)", style="Card.TLabelframe", padding=10)
        trace_card.pack(fill="both", expand=True)

        self.trace_text = scrolledtext.ScrolledText(trace_card, height=11, font=("Consolas", 9), relief="flat", bd=1)
        self.trace_text.pack(fill="both", expand=True)

        self.reset()

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
            self.update_stats()
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

        for entry in (self.left_entry, self.mid_entry, self.right_entry):
            entry.delete(0, "end")
            entry.insert(0, "0")

        self.plug_entry.delete(0, "end")
        self.keep_spaces_var.set(True)
        self.trace_var.set(True)
        self.rotor_state.set("Rotorlar (L-M-R): 0-0-0")
        self.status.set("Sıfırlandı")
        self.update_stats()

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



    def update_stats(self) -> None:
        input_len = len(self.input_text.get("1.0", "end-1c"))
        output_len = len(self.output_text.get("1.0", "end-1c"))
        self.stats_var.set(f"Girdi: {input_len} karakter | Çıktı: {output_len} karakter")

    def copy_output_to_clipboard(self) -> None:
        out = self.output_text.get("1.0", "end-1c")
        if not out.strip():
            self.status.set("Panoya kopyalamak için çıktı yok")
            messagebox.showwarning("Uyarı", "Panoya kopyalanacak çıktı yok.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(out)
        self.status.set("Çıktı panoya kopyalandı")

    def save_profile_file(self) -> None:
        try:
            desktop = Path.home() / "Desktop"
            desktop.mkdir(parents=True, exist_ok=True)
            default = desktop / "EnigmaProfil.json"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                initialfile=default.name,
                initialdir=str(desktop),
                filetypes=[("JSON", "*.json")],
                title="Profili Kaydet",
            )
            if not file_path:
                return
            data = {
                "left": self.left_entry.get().strip(),
                "middle": self.mid_entry.get().strip(),
                "right": self.right_entry.get().strip(),
                "plugboard": self.plug_entry.get().strip(),
                "keep_spaces": self.keep_spaces_var.get(),
                "trace": self.trace_var.get(),
            }
            Path(file_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            self.status.set(f"Profil kaydedildi: {file_path}")
        except Exception as exc:
            self.status.set(f"Profil kaydetme hatası: {exc}")
            messagebox.showerror("Profil Hatası", str(exc))

    def load_profile_file(self) -> None:
        try:
            desktop = Path.home() / "Desktop"
            file_path = filedialog.askopenfilename(
                initialdir=str(desktop),
                filetypes=[("JSON", "*.json")],
                title="Profil Yükle",
            )
            if not file_path:
                return
            data = json.loads(Path(file_path).read_text(encoding="utf-8"))

            self.left_entry.delete(0, "end")
            self.mid_entry.delete(0, "end")
            self.right_entry.delete(0, "end")
            self.left_entry.insert(0, str(data.get("left", "0")))
            self.mid_entry.insert(0, str(data.get("middle", "0")))
            self.right_entry.insert(0, str(data.get("right", "0")))
            self.plug_entry.delete(0, "end")
            self.plug_entry.insert(0, data.get("plugboard", ""))
            self.keep_spaces_var.set(bool(data.get("keep_spaces", True)))
            self.trace_var.set(bool(data.get("trace", True)))
            self.status.set(f"Profil yüklendi: {file_path}")
        except Exception as exc:
            self.status.set(f"Profil yükleme hatası: {exc}")
            messagebox.showerror("Profil Hatası", str(exc))

    def save_password_file(self) -> None:
        try:
            desktop = Path.home() / "Desktop"
            desktop.mkdir(parents=True, exist_ok=True)

            base_name = "Şifre.Password"
            file_path = desktop / base_name

            if file_path.exists():
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = desktop / f"Şifre_{stamp}.Password"

            encrypted_text = self.output_text.get("1.0", "end-1c").strip()
            if not encrypted_text:
                raise ValueError("Kaydedilecek çıktı yok. Önce şifreleme/çözme yapın.")

            rotor_info = self.rotor_state.get()
            plugboard = self.plug_entry.get().strip() or "(boş)"
            content = (
                "ENIGMA PASSWORD DOSYASI\n"
                "======================\n"
                f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{rotor_info}\n"
                f"Plugboard: {plugboard}\n\n"
                "Şifreli Metin:\n"
                f"{encrypted_text}\n"
            )

            file_path.write_text(content, encoding="utf-8")
            self.status.set(f"Dosya kaydedildi: {file_path}")
            messagebox.showinfo("Kayıt Başarılı", f"Şifre dosyası kaydedildi:\n{file_path}")
        except Exception as exc:
            self.status.set(f"Kaydetme hatası: {exc}")
            messagebox.showerror("Kayıt Hatası", str(exc))

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
