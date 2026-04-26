import os
import queue
import tempfile
import unittest

import main


class FakeArduino:
    def __init__(self):
        self.commands = []

    def connect(self):
        return True, "ok"

    def disconnect(self):
        return "bye"

    def send(self, cmd):
        self.commands.append(cmd)
        return True, "25.3"


class CodeFilterTests(unittest.TestCase):
    def test_code_is_separated_from_spoken_text(self):
        cf = main.CodeFilter()
        spoken, code = cf.split("Merhaba ```python\nprint('x')\n``` tamam")
        self.assertIn("Kodları ekrana bastım bilader", spoken)
        self.assertTrue(code)


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.arduino = FakeArduino()
        self.router = main.LocalCommandRouter(self.arduino)

    def test_router_handles_temperature_command(self):
        out = self.router.route("sıcaklık kaç")
        self.assertIn("Sıcaklık", out)
        self.assertEqual(self.arduino.commands[-1], "T")

    def test_router_handles_greeting(self):
        out = self.router.route("merhaba bilader")
        self.assertIn("Buradayım", out)

    def test_router_handles_command_list(self):
        out = self.router.route("komut rehberi")
        self.assertIn("Komut rehberini", out)


class CoreEventTests(unittest.TestCase):
    def test_emit_event_flag_controls_queue(self):
        with tempfile.TemporaryDirectory() as td:
            main.DB_PATH = os.path.join(td, "test.sqlite3")  # type: ignore[assignment]
            main.ENV_PATH = os.path.join(td, ".env")  # type: ignore[assignment]
            core = main.BiladerCore()
            core.speaker.enabled = False
            core.router.route = lambda _: "yerel cevap"

            core.process_input("test", emit_event=False)
            self.assertTrue(core.events.empty())

            core.process_input("test", emit_event=True)
            self.assertIsInstance(core.events, queue.Queue)
            self.assertFalse(core.events.empty())

            exported = core.memory.export_bundle(limit=10)
            self.assertIn("conversations", exported)
            self.assertIn("events", exported)
            self.assertIn("core", main.CommandPlaybook.export())
            self.assertTrue(main.hint_slice(3))

            core.memory.clear_all()
            self.assertEqual(core.memory.history(5), [])
            core.stop()


if __name__ == "__main__":
    unittest.main()
