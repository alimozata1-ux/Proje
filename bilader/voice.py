from __future__ import annotations

import threading
from dataclasses import dataclass
from queue import Queue
from typing import Callable, Optional

import pyttsx3
import speech_recognition as sr


@dataclass(slots=True)
class VoiceEvent:
    kind: str
    payload: dict


class TTSService:
    def __init__(self, rate: int, volume: float) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self.lock = threading.Lock()

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        with self.lock:
            self.engine.say(text)
            self.engine.runAndWait()


class WakeWordListener:
    def __init__(self, wake_words: tuple[str, ...]) -> None:
        self.wake_words = tuple(w.strip().lower() for w in wake_words if w.strip())
        self.recognizer = sr.Recognizer()
        self.microphone: Optional[sr.Microphone] = None
        self.active = False
        self._thread: Optional[threading.Thread] = None
        self._events: Queue[VoiceEvent] = Queue()

    def start(self, callback: Callable[[str], None]) -> None:
        if self.active:
            return
        self.active = True
        self._thread = threading.Thread(
            target=self._loop,
            args=(callback,),
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self.active = False

    def _loop(self, callback: Callable[[str], None]) -> None:
        try:
            self.microphone = sr.Microphone()
        except Exception as exc:
            self._events.put(VoiceEvent(kind="error", payload={"error": str(exc)}))
            return

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.6)

        while self.active:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(
                        source,
                        timeout=1,
                        phrase_time_limit=3,
                    )
                text = self.recognizer.recognize_google(audio, language="tr-TR")
                low = text.lower()
                if any(ww in low for ww in self.wake_words):
                    self._events.put(VoiceEvent(kind="wake", payload={"text": text}))
                    callback(text)
                else:
                    self._events.put(VoiceEvent(kind="passive", payload={"text": text}))
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as exc:
                self._events.put(VoiceEvent(kind="error", payload={"error": str(exc)}))

    def poll_event(self) -> Optional[VoiceEvent]:
        if self._events.empty():
            return None
        return self._events.get_nowait()
