import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from proton.interpreter import ProtonInterpreter
from proton.packager import build_runner


class ProtonRuntimeTests(unittest.TestCase):
    def test_basic_execution(self):
        src = 'x:10\n@ x\n'
        interp = ProtonInterpreter(plugin_dir='plugins')
        result = interp.run(src)
        self.assertIsNone(result)
        self.assertEqual(interp.context.locals['x'], 10)

    def test_last_result_slot(self):
        src = 'calc> 2 + 3\ny:_\n'
        interp = ProtonInterpreter()
        interp.run(src)
        self.assertEqual(interp.context.locals['y'], 5)

    def test_data_commands(self):
        src = 'nums:[1,2,3,4]\nmap> (lambda x: x*2, nums)\na:_\nreduce> (lambda a,b:a+b, nums)\nb:_\n'
        interp = ProtonInterpreter()
        interp.run(src)
        self.assertEqual(interp.context.locals['a'], [2, 4, 6, 8])
        self.assertEqual(interp.context.locals['b'], 10)

    def test_file_commands_with_sandbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = f'w> ({tmp!r} + "/a.txt", "hello")\nr< {tmp!r} + "/a.txt"\nvalue:_\n'
            interp = ProtonInterpreter()
            interp.run(script)
            self.assertEqual(interp.context.locals['value'], 'hello')
            self.assertTrue(Path(tmp, 'a.txt').exists())

    def test_build_runner_from_pt(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pt_file = tmp_path / 'hello.pt'
            out_py = tmp_path / 'hello_runner.py'
            pt_file.write_text('@ "runner_ok"\n', encoding='utf-8')
            build_runner(str(pt_file), str(out_py), plugin_dir='plugins', sandbox=False)
            result = subprocess.run([sys.executable, str(out_py)], capture_output=True, text=True, check=True)
            self.assertIn('runner_ok', result.stdout)


if __name__ == '__main__':
    unittest.main()
