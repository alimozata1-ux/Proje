import json
import re
import shlex
import subprocess
import threading
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import DictProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

KV = r'''
#:import dp kivy.metrics.dp

<ThemedCard@BoxLayout>:
    padding: dp(8)
    spacing: dp(6)
    canvas.before:
        Color:
            rgba: app.theme["card"]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]

<TopBar@BoxLayout>:
    size_hint_y: None
    height: dp(54)
    spacing: dp(8)
    padding: dp(8)
    canvas.before:
        Color:
            rgba: app.theme["surface"]
        Rectangle:
            pos: self.pos
            size: self.size

<StatusBar@BoxLayout>:
    size_hint_y: None
    height: dp(28)
    padding: dp(8), 0
    canvas.before:
        Color:
            rgba: app.theme["surface"]
        Rectangle:
            pos: self.pos
            size: self.size

<BrowserScreen>:
    name: "browser"
    BoxLayout:
        orientation: "vertical"
        spacing: dp(6)
        padding: dp(6)
        canvas.before:
            Color:
                rgba: app.theme["bg"]
            Rectangle:
                pos: self.pos
                size: self.size

        TopBar:
            Button:
                text: "◀"
                size_hint_x: None
                width: dp(54)
                on_release: root.go_back()
            Button:
                text: "▶"
                size_hint_x: None
                width: dp(54)
                on_release: root.go_forward()
            Button:
                text: "⟳"
                size_hint_x: None
                width: dp(54)
                on_release: root.reload_page()
            TextInput:
                id: address
                text: root.address
                hint_text: "URL ya da arama"
                multiline: False
                on_text_validate: root.open_url(self.text)
            Button:
                text: "Git"
                size_hint_x: None
                width: dp(72)
                on_release: root.open_url(address.text)

        TopBar:
            Button:
                text: "Sekme +"
                on_release: root.new_tab()
            Button:
                text: "Yer İmleri"
                on_release: root.open_bookmarks()
            Button:
                text: "İndirmeler"
                on_release: app.root.current = "downloads"
            Button:
                text: "Paketler"
                on_release: app.root.current = "packages"
            Button:
                text: "Ayarlar"
                on_release: app.root.current = "settings"

        ScrollView:
            size_hint_y: None
            height: dp(36)
            do_scroll_y: False
            BoxLayout:
                id: tabs
                size_hint_x: None
                width: self.minimum_width
                spacing: dp(4)

        ThemedCard:
            orientation: "vertical"
            size_hint_y: None
            height: dp(42)
            Label:
                text: root.page_title
                color: app.theme["text"]
                text_size: self.width - dp(12), None
                halign: "left"

        ThemedCard:
            orientation: "vertical"
            ScrollView:
                bar_width: dp(5)
                Label:
                    text: root.page_content
                    color: app.theme["text"]
                    text_size: self.width - dp(16), None
                    halign: "left"
                    valign: "top"
                    size_hint_y: None
                    height: self.texture_size[1] + dp(16)

        StatusBar:
            Label:
                text: root.status
                color: app.theme["muted"]
                halign: "left"
                valign: "middle"
                text_size: self.size

<DownloadsScreen>:
    name: "downloads"
    BoxLayout:
        orientation: "vertical"
        spacing: dp(6)
        padding: dp(6)
        canvas.before:
            Color:
                rgba: app.theme["bg"]
            Rectangle:
                pos: self.pos
                size: self.size

        TopBar:
            Button:
                text: "← Tarayıcı"
                size_hint_x: None
                width: dp(120)
                on_release: app.root.current = "browser"
            TextInput:
                id: file_url
                multiline: False
                hint_text: "İndirilecek dosya URL"
            Button:
                text: "İndir"
                size_hint_x: None
                width: dp(90)
                on_release: root.start_download(file_url.text)

        ScrollView:
            GridLayout:
                id: rows
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(6)

<PackagesScreen>:
    name: "packages"
    log_text: "Paket yöneticisi hazır"
    BoxLayout:
        orientation: "vertical"
        spacing: dp(6)
        padding: dp(6)
        canvas.before:
            Color:
                rgba: app.theme["bg"]
            Rectangle:
                pos: self.pos
                size: self.size

        TopBar:
            Button:
                text: "← Tarayıcı"
                size_hint_x: None
                width: dp(120)
                on_release: app.root.current = "browser"
            TextInput:
                id: package_input
                multiline: False
                hint_text: "Paket adı (örn: requests==2.32.3)"
            Button:
                text: "Kur"
                size_hint_x: None
                width: dp(76)
                on_release: root.install(package_input.text)
            Button:
                text: "Sil"
                size_hint_x: None
                width: dp(76)
                on_release: root.uninstall(package_input.text)
            Button:
                text: "Liste"
                size_hint_x: None
                width: dp(76)
                on_release: root.list_packages()

        ThemedCard:
            TextInput:
                text: root.log_text
                readonly: True
                foreground_color: app.theme["text"]
                background_color: app.theme["card"]

<SettingsScreen>:
    name: "settings"
    BoxLayout:
        orientation: "vertical"
        spacing: dp(6)
        padding: dp(6)
        canvas.before:
            Color:
                rgba: app.theme["bg"]
            Rectangle:
                pos: self.pos
                size: self.size

        TopBar:
            Button:
                text: "← Tarayıcı"
                size_hint_x: None
                width: dp(120)
                on_release: app.root.current = "browser"
            Label:
                text: "Detaylı Ayarlar"
                color: app.theme["text"]

        ScrollView:
            GridLayout:
                id: form
                cols: 2
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(6)
                row_force_default: True
                row_default_height: dp(42)

        Button:
            text: "Kaydet"
            size_hint_y: None
            height: dp(44)
            on_release: root.save_settings()
'''


@dataclass
class Tab:
    url: str = "https://duckduckgo.com"
    title: str = "Yeni Sekme"
    content: str = "Hoş geldiniz. URL girin veya arama yapın."
    history: List[str] = field(default_factory=list)
    history_index: int = -1


class BrowserScreen(Screen):
    address = StringProperty("")
    page_title = StringProperty("Kivy Modern Browser")
    page_content = StringProperty("Hazır")
    status = StringProperty("Hazır")

    def on_kv_post(self, *_):
        self.app = App.get_running_app()
        self.refresh_tabs()
        self.open_url(self.app.settings_data.get("home_url", "https://duckduckgo.com"))

    def _active_tab(self) -> Tab:
        return self.app.tabs[self.app.active_tab_index]

    def refresh_tabs(self):
        holder = self.ids.tabs
        holder.clear_widgets()
        for i, tab in enumerate(self.app.tabs):
            label = ("● " if i == self.app.active_tab_index else "") + (tab.title[:18] or "Sekme")
            btn = Button(text=label, size_hint=(None, None), size=(dp(180), dp(30)))
            btn.bind(on_release=lambda *_a, idx=i: self.switch_tab(idx))
            holder.add_widget(btn)

    def switch_tab(self, index: int):
        self.app.active_tab_index = index
        tab = self._active_tab()
        self.address = tab.url
        self.page_title = tab.title
        self.page_content = tab.content
        self.status = f"Sekme {index + 1} aktif"
        self.refresh_tabs()

    def new_tab(self):
        home = self.app.settings_data.get("home_url", "https://duckduckgo.com")
        self.app.tabs.append(Tab(url=home))
        self.switch_tab(len(self.app.tabs) - 1)

    def _normalize_url(self, text: str) -> str:
        value = (text or "").strip()
        if not value:
            return self.app.settings_data.get("home_url", "https://duckduckgo.com")
        if re.match(r"^https?://", value):
            return value
        if "." in value and " " not in value:
            return f"https://{value}"
        template = self.app.settings_data.get("search_url", "https://duckduckgo.com/?q={query}")
        return template.format(query=requests.utils.quote(value))

    def open_url(self, text: str):
        url = self._normalize_url(text)
        blocked = self.app.blocked_domain(url)
        if blocked:
            self.status = f"Engellendi: {blocked}"
            return

        tab = self._active_tab()
        tab.url = url
        self.address = url
        self.status = f"Yükleniyor: {url}"

        def worker():
            timeout = float(self.app.settings_data.get("timeout", 12))
            headers = {"User-Agent": self.app.settings_data.get("user_agent", "KivyModernBrowser/1.0")}
            started = time.time()
            try:
                response = requests.get(url, timeout=timeout, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                title = (soup.title.text.strip() if soup.title else url)[:140]
                body = "\n".join(soup.stripped_strings)
                body = body[:25000] if body else "İçerik bulunamadı."
                elapsed = int((time.time() - started) * 1000)
                Clock.schedule_once(lambda *_: self._apply_success(url, title, body, elapsed))
            except Exception as exc:
                Clock.schedule_once(lambda *_: self._apply_error(url, str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_success(self, url: str, title: str, body: str, elapsed_ms: int):
        tab = self._active_tab()
        tab.title = title
        tab.content = body

        if tab.history_index == -1 or tab.history[tab.history_index] != url:
            tab.history = tab.history[: tab.history_index + 1]
            tab.history.append(url)
            tab.history_index += 1

        self.page_title = title
        self.page_content = body
        self.status = f"Tamamlandı ({elapsed_ms} ms)"
        self.app.history.append({"title": title, "url": url, "time": int(time.time())})
        self.app.history = self.app.history[-1000:]
        self.app.save_state()
        self.refresh_tabs()

    def _apply_error(self, url: str, error: str):
        self.page_title = "Yükleme Hatası"
        self.page_content = f"URL: {url}\n\n{error}"
        self.status = "Hata"

    def go_back(self):
        tab = self._active_tab()
        if tab.history_index > 0:
            tab.history_index -= 1
            self.open_url(tab.history[tab.history_index])

    def go_forward(self):
        tab = self._active_tab()
        if 0 <= tab.history_index < len(tab.history) - 1:
            tab.history_index += 1
            self.open_url(tab.history[tab.history_index])

    def reload_page(self):
        self.open_url(self._active_tab().url)

    def open_bookmarks(self):
        content = BoxLayout(orientation="vertical", spacing=6, padding=6)
        add_url = TextInput(text=self._active_tab().url, multiline=False)
        add_button = Button(text="Mevcut URL'yi Yer İmlerine Ekle", size_hint_y=None, height=42)
        content.add_widget(add_url)
        content.add_widget(add_button)

        for item in self.app.bookmarks[-15:]:
            btn = Button(
                text=f"{item['title'][:26]} → {item['url'][:35]}",
                size_hint_y=None,
                height=32,
            )
            btn.bind(on_release=lambda *_a, u=item["url"]: self.open_url(u))
            content.add_widget(btn)

        popup = Popup(title="Yer İmleri", content=content, size_hint=(0.9, 0.9))

        def do_add(*_):
            self.app.bookmarks.append({"title": self.page_title, "url": add_url.text.strip()})
            self.app.bookmarks = self.app.bookmarks[-300:]
            self.app.save_state()
            popup.dismiss()

        add_button.bind(on_release=do_add)
        popup.open()


class DownloadsScreen(Screen):
    def on_kv_post(self, *_):
        self.app = App.get_running_app()
        self.refresh()

    def refresh(self):
        container = self.ids.rows
        container.clear_widgets()

        for item in self.app.downloads:
            card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(80), padding=dp(8), spacing=dp(4))
            card.add_widget(Label(text=f"{item['file_name']} | {item['status']}", size_hint_y=None, height=dp(26)))
            card.add_widget(ProgressBar(max=100, value=item.get("progress", 0)))
            container.add_widget(card)

    def start_download(self, url: str):
        target = (url or "").strip()
        if not target:
            return

        folder = Path(self.app.settings_data.get("download_dir", "downloads"))
        folder.mkdir(parents=True, exist_ok=True)
        file_name = target.rstrip("/").split("/")[-1] or f"download_{int(time.time())}.bin"
        file_path = folder / file_name

        job = {
            "url": target,
            "file_name": file_name,
            "path": str(file_path),
            "status": "başlatıldı",
            "progress": 0,
        }
        self.app.downloads.append(job)
        self.refresh()

        def worker():
            try:
                with requests.get(target, stream=True, timeout=45) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("content-length", 0))
                    written = 0
                    with open(file_path, "wb") as handle:
                        for chunk in response.iter_content(chunk_size=16384):
                            if not chunk:
                                continue
                            handle.write(chunk)
                            written += len(chunk)
                            if total > 0:
                                job["progress"] = min(100, int((written / total) * 100))
                            job["status"] = "indiriliyor"
                            Clock.schedule_once(lambda *_: self.refresh())
                job["progress"] = 100
                job["status"] = "tamamlandı"
            except Exception as exc:
                job["status"] = f"hata: {exc}"
            finally:
                Clock.schedule_once(lambda *_: self.refresh())
                self.app.save_state()

        threading.Thread(target=worker, daemon=True).start()


class PackagesScreen(Screen):
    log_text = StringProperty("Paket yöneticisi hazır")

    def _run_pip(self, args: List[str]):
        self.log_text = "Komut çalışıyor..."

        def worker():
            cmd = ["python", "-m", "pip"] + args
            proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
            out = "$ " + " ".join(shlex.quote(x) for x in cmd)
            out += "\n\nSTDOUT:\n" + proc.stdout
            out += "\n\nSTDERR:\n" + proc.stderr
            out += f"\n\nÇıkış Kodu: {proc.returncode}"
            Clock.schedule_once(lambda *_: setattr(self, "log_text", out))

        threading.Thread(target=worker, daemon=True).start()

    def install(self, package_name: str):
        package_name = package_name.strip()
        if package_name:
            self._run_pip(["install", package_name])

    def uninstall(self, package_name: str):
        package_name = package_name.strip()
        if package_name:
            self._run_pip(["uninstall", "-y", package_name])

    def list_packages(self):
        self._run_pip(["list"])


class SettingsScreen(Screen):
    field_order = [
        ("home_url", "Anasayfa URL"),
        ("search_url", "Arama URL Şablonu ({query})"),
        ("download_dir", "İndirme Klasörü"),
        ("timeout", "Timeout (sn)"),
        ("user_agent", "User-Agent"),
        ("theme", "Tema (dark/light)"),
        ("adblock_domains", "Adblock Domainleri (, ile)"),
    ]

    def on_kv_post(self, *_):
        self.app = App.get_running_app()
        self.inputs: Dict[str, TextInput] = {}
        self._build_form()

    def _build_form(self):
        form: GridLayout = self.ids.form
        form.clear_widgets()
        self.inputs.clear()

        for key, label in self.field_order:
            form.add_widget(Label(text=label))
            value = self.app.settings_data.get(key, "")
            if isinstance(value, list):
                value = ",".join(value)
            input_box = TextInput(text=str(value), multiline=False)
            self.inputs[key] = input_box
            form.add_widget(input_box)

    def save_settings(self):
        for key, input_box in self.inputs.items():
            self.app.settings_data[key] = input_box.text.strip()

        try:
            self.app.settings_data["timeout"] = float(self.app.settings_data.get("timeout", 12))
        except ValueError:
            self.app.settings_data["timeout"] = 12.0

        adblock_raw = str(self.app.settings_data.get("adblock_domains", ""))
        self.app.settings_data["adblock_domains"] = [x.strip() for x in adblock_raw.split(",") if x.strip()]
        self.app.settings_data["theme"] = str(self.app.settings_data.get("theme", "dark")).lower() or "dark"

        self.app.apply_theme()
        self.app.save_state()


class ModernBrowserApp(App):
    theme = DictProperty({})
    tabs = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_file = Path("browser_state.json")
        self.tabs: List[Tab] = [Tab()]
        self.active_tab_index = 0
        self.history: List[Dict[str, Any]] = []
        self.bookmarks: List[Dict[str, str]] = []
        self.downloads: List[Dict[str, Any]] = []
        self.settings_data: Dict[str, Any] = {
            "home_url": "https://duckduckgo.com",
            "search_url": "https://duckduckgo.com/?q={query}",
            "download_dir": "downloads",
            "timeout": 12,
            "user_agent": "KivyModernBrowser/1.0",
            "theme": "dark",
            "adblock_domains": ["doubleclick.net", "googlesyndication.com"],
        }
        self.load_state()
        self._normalize_settings()
        self.apply_theme()

    def build(self):
        return Builder.load_string(KV)

    def _normalize_settings(self):
        try:
            self.settings_data["timeout"] = float(self.settings_data.get("timeout", 12))
        except Exception:
            self.settings_data["timeout"] = 12.0

        if not isinstance(self.settings_data.get("adblock_domains"), list):
            raw = str(self.settings_data.get("adblock_domains", ""))
            self.settings_data["adblock_domains"] = [x.strip() for x in raw.split(",") if x.strip()]

        self.settings_data["theme"] = str(self.settings_data.get("theme", "dark")).lower().strip() or "dark"

    def apply_theme(self):
        if self.settings_data.get("theme") == "light":
            self.theme = {
                "bg": (0.95, 0.96, 0.98, 1),
                "surface": (0.88, 0.90, 0.94, 1),
                "card": (1, 1, 1, 1),
                "text": (0.08, 0.10, 0.12, 1),
                "muted": (0.33, 0.36, 0.40, 1),
            }
        else:
            self.theme = {
                "bg": (0.08, 0.09, 0.11, 1),
                "surface": (0.13, 0.14, 0.17, 1),
                "card": (0.16, 0.17, 0.21, 1),
                "text": (0.93, 0.95, 0.98, 1),
                "muted": (0.65, 0.68, 0.73, 1),
            }

    def blocked_domain(self, url: str) -> Optional[str]:
        for domain in self.settings_data.get("adblock_domains", []):
            if domain and domain.lower() in url.lower():
                return domain
        return None

    def save_state(self):
        payload = {
            "tabs": [asdict(tab) for tab in self.tabs],
            "active_tab_index": self.active_tab_index,
            "history": self.history,
            "bookmarks": self.bookmarks,
            "downloads": self.downloads,
            "settings_data": self.settings_data,
        }
        self.state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_state(self):
        if not self.state_file.exists():
            return
        try:
            payload = json.loads(self.state_file.read_text(encoding="utf-8"))
            tabs = payload.get("tabs", [])
            if tabs:
                self.tabs = [Tab(**item) for item in tabs]
            self.active_tab_index = min(int(payload.get("active_tab_index", 0)), len(self.tabs) - 1)
            self.history = payload.get("history", [])
            self.bookmarks = payload.get("bookmarks", [])
            self.downloads = payload.get("downloads", [])
            self.settings_data.update(payload.get("settings_data", {}))
        except Exception:
            pass


if __name__ == "__main__":
    ModernBrowserApp().run()
