#!/usr/bin/env python3
"""
Tek dosyalık Kivy tarayıcı uygulaması.

Özellikler:
- Sekmeler (yeni sekme / sekme kapatma)
- Geri / ileri / yenile / ana sayfa
- URL veya arama çubuğu
- Klavye kısayolları
- Fare ve dokunmatik (kaydırma ile geri/ileri)

Not:
- Gerçek web motoru için `kivy.uix.webview.WebView` gereklidir.
- Eğer bu sınıf platformda yoksa uygulama yine açılır, ancak içerik alanında
  "fallback" görünümü kullanılır.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote_plus

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.textinput import TextInput

try:
    from kivy.uix.webview import WebView  # type: ignore
except Exception:  # Platformda webview yoksa fallback kullan
    WebView = None


SEARCH_ENGINE = "https://duckduckgo.com/?q={}"
HOME_URL = "https://www.wikipedia.org"


@dataclass
class TabState:
    history: list[str] = field(default_factory=list)
    index: int = -1

    def push(self, url: str) -> None:
        # İleri geçmişi sil (back'ten sonra yeni URL)
        if self.index < len(self.history) - 1:
            self.history = self.history[: self.index + 1]
        self.history.append(url)
        self.index = len(self.history) - 1

    def can_go_back(self) -> bool:
        return self.index > 0

    def can_go_forward(self) -> bool:
        return self.index < len(self.history) - 1

    def go_back(self) -> str | None:
        if self.can_go_back():
            self.index -= 1
            return self.history[self.index]
        return None

    def go_forward(self) -> str | None:
        if self.can_go_forward():
            self.index += 1
            return self.history[self.index]
        return None

    def current(self) -> str | None:
        if 0 <= self.index < len(self.history):
            return self.history[self.index]
        return None


class FallbackWeb(BoxLayout):
    current_url = StringProperty("about:blank")

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.info = Label(
            text=(
                "[b]Bu platformda Kivy WebView bulunamadı.[/b]\n\n"
                "Yine de tarayıcı arayüzü çalışıyor.\n"
                "Gerçek sayfa motoru için Android/iOS ortamı veya\n"
                "WebView destekli Kivy kurulumu gerekir.\n\n"
                "Yüklenecek URL: about:blank"
            ),
            markup=True,
            halign="center",
            valign="middle",
        )
        self.info.bind(size=self._update_text_size)
        self.add_widget(self.info)

    def _update_text_size(self, *_):
        self.info.text_size = (self.info.width - dp(20), None)

    def load_url(self, url: str):
        self.current_url = url
        self.info.text = (
            "[b]Fallback görünümü[/b]\n\n"
            f"İstenen URL:\n[color=33aaff]{url}[/color]\n\n"
            "WebView mevcut değil; bu yüzden sayfa render edilmiyor."
        )

    def reload(self):
        self.load_url(self.current_url)


class BrowserTab(BoxLayout):
    state = ObjectProperty(None)

    def __init__(self, on_url_change, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.state = TabState()
        self._on_url_change = on_url_change

        if WebView is not None:
            self.web = WebView()
            if hasattr(self.web, "bind") and hasattr(self.web, "url"):
                self.web.bind(url=self._web_url_changed)
        else:
            self.web = FallbackWeb()

        # Dokunmatik kaydırma ile geri/ileri
        self._touch_start_x = None
        self.web.bind(on_touch_down=self._on_touch_down, on_touch_up=self._on_touch_up)

        self.add_widget(self.web)

    def _web_url_changed(self, _instance, value):
        if value:
            self._on_url_change(value)

    def _on_touch_down(self, _w, touch):
        self._touch_start_x = touch.x
        return False

    def _on_touch_up(self, _w, touch):
        if self._touch_start_x is None:
            return False
        delta = touch.x - self._touch_start_x
        threshold = dp(120)
        if delta > threshold:
            self.back()
            return True
        if delta < -threshold:
            self.forward()
            return True
        return False

    @staticmethod
    def normalize_url(text: str) -> str:
        text = text.strip()
        if not text:
            return HOME_URL
        if " " in text or "." not in text:
            return SEARCH_ENGINE.format(quote_plus(text))
        if not text.startswith(("http://", "https://")):
            return f"https://{text}"
        return text

    def load(self, text: str, add_to_history: bool = True):
        url = self.normalize_url(text)
        if WebView is not None and hasattr(self.web, "url"):
            self.web.url = url
        elif hasattr(self.web, "load_url"):
            self.web.load_url(url)

        if add_to_history:
            self.state.push(url)
        self._on_url_change(url)

    def back(self):
        url = self.state.go_back()
        if url:
            self.load(url, add_to_history=False)

    def forward(self):
        url = self.state.go_forward()
        if url:
            self.load(url, add_to_history=False)

    def reload(self):
        current = self.state.current()
        if current:
            self.load(current, add_to_history=False)
        elif hasattr(self.web, "reload"):
            self.web.reload()


class BrowserUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(6), padding=dp(6), **kwargs)

        self.top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(46), spacing=dp(6))

        self.btn_back = Button(text="◀", size_hint_x=None, width=dp(48), on_release=lambda *_: self.current_tab.back())
        self.btn_forward = Button(text="▶", size_hint_x=None, width=dp(48), on_release=lambda *_: self.current_tab.forward())
        self.btn_reload = Button(text="⟳", size_hint_x=None, width=dp(48), on_release=lambda *_: self.current_tab.reload())
        self.btn_home = Button(text="⌂", size_hint_x=None, width=dp(48), on_release=lambda *_: self.current_tab.load(HOME_URL))

        self.url_input = TextInput(multiline=False, hint_text="URL veya arama…")
        self.url_input.bind(on_text_validate=lambda *_: self.open_from_input())

        self.btn_go = Button(text="Git", size_hint_x=None, width=dp(64), on_release=lambda *_: self.open_from_input())
        self.btn_new_tab = Button(text="+", size_hint_x=None, width=dp(46), on_release=lambda *_: self.add_tab())

        for widget in [
            self.btn_back,
            self.btn_forward,
            self.btn_reload,
            self.btn_home,
            self.url_input,
            self.btn_go,
            self.btn_new_tab,
        ]:
            self.top.add_widget(widget)

        self.tabs = TabbedPanel(do_default_tab=False, tab_width=dp(180))
        self.add_widget(self.top)
        self.add_widget(self.tabs)

        self.add_tab(initial_url=HOME_URL)

        Window.bind(on_key_down=self._on_key_down)

    @property
    def current_tab(self) -> BrowserTab:
        content = self.tabs.current_tab.content
        return content  # type: ignore[return-value]

    def _set_address(self, url: str):
        self.url_input.text = url
        self._update_tab_title(url)

    def _update_tab_title(self, url: str):
        header = self.tabs.current_tab
        if not header:
            return
        title = url.replace("https://", "").replace("http://", "")[:24]
        header.text = title or "Yeni Sekme"

    def add_tab(self, *_args, initial_url: str = "about:blank"):
        header = TabbedPanelHeader(text="Yeni Sekme")
        tab_content = BrowserTab(on_url_change=self._set_address)
        header.content = tab_content
        self.tabs.add_widget(header)
        self.tabs.switch_to(header)
        Clock.schedule_once(lambda *_: tab_content.load(initial_url), 0)

        if len(self.tabs.tab_list) > 1:
            header.bind(on_release=lambda *_: self._bind_middle_click_close(header))

    def _bind_middle_click_close(self, header):
        # Kivy'de direkt orta tık olayı sınırlı; pratik bir alternatif olarak
        # tab başlığına çift tıklamayla kapatma davranışı tanımlanır.
        if not hasattr(header, "_double_tap_bound"):
            header._double_tap_bound = True
            header.bind(on_touch_down=lambda inst, t: self._tab_touch_close(inst, t))

    def _tab_touch_close(self, header, touch):
        if header.collide_point(*touch.pos) and touch.is_double_tap:
            self.close_tab(header)
            return True
        return False

    def close_tab(self, header: TabbedPanelHeader | None = None):
        header = header or self.tabs.current_tab
        if len(self.tabs.tab_list) <= 1 or header is None:
            return
        self.tabs.remove_widget(header)
        if self.tabs.current_tab:
            self._set_address(self.current_tab.state.current() or HOME_URL)

    def open_from_input(self):
        self.current_tab.load(self.url_input.text)

    def _on_key_down(self, _window, key, _scancode, text, modifiers):
        ctrl = "ctrl" in modifiers

        if ctrl and text.lower() == "l":
            self.url_input.focus = True
            self.url_input.select_all()
            return True
        if ctrl and text.lower() == "r":
            self.current_tab.reload()
            return True
        if ctrl and text.lower() == "t":
            self.add_tab(initial_url=HOME_URL)
            return True
        if ctrl and text.lower() == "w":
            self.close_tab()
            return True

        # Alt+Sol / Alt+Sağ
        if "alt" in modifiers and key == 276:
            self.current_tab.back()
            return True
        if "alt" in modifiers and key == 275:
            self.current_tab.forward()
            return True

        return False


class TekDosyaKivyTarayici(App):
    title = "Kivy Tek Dosya Tarayıcı"

    def build(self):
        Window.minimum_width = 900
        Window.minimum_height = 620
        return BrowserUI()


if __name__ == "__main__":
    TekDosyaKivyTarayici().run()
