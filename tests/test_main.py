import re
import textwrap
import unittest
import io
from typing import Dict

from jinsi.main import main as jinsi_main


def capture(into: io.StringIO):
    def _print(arg, end='\n'):
        into.write(arg)
        into.write(end)

    return _print


def provide(dct: Dict[str, str]):
    def _open(arg):
        val = dct[arg]
        return io.StringIO(textwrap.dedent(val))

    return _open


class MainTest(unittest.TestCase):

    def test_version(self):
        res = io.StringIO()
        jinsi_main("--version", _print=capture(res), _open=provide({}), _stdin=io.StringIO(""))
        self.assertRegex(res.getvalue(), re.compile(r"0\.[1-9][0-9]*\.[0-9]"))

    def test_single_json_object_as_yaml(self):
        res = io.StringIO()
        jinsi_main("-", _print=capture(res), _open=provide({}), _stdin=io.StringIO("""{"x":3}"""))
        self.assertEqual("x: 3\n", res.getvalue())

    def test_multi_json_object_as_yaml(self):
        res = io.StringIO()
        jinsi_main("-", _print=capture(res), _open=provide({}), _stdin=io.StringIO("""{"x":3}\n{"y":3}\n"""))
        self.assertEqual("x: 3\n---\ny: 3\n", res.getvalue())

    def test_single_yaml_object_as_yaml(self):
        res = io.StringIO()
        jinsi_main("-", _print=capture(res), _open=provide({}), _stdin=io.StringIO("x: 3"))
        self.assertEqual("x: 3\n", res.getvalue())

    def test_multi_yaml_object_as_yaml(self):
        res = io.StringIO()
        jinsi_main("-", _print=capture(res), _open=provide({}), _stdin=io.StringIO("x: 3\n---\ny: 3\n"))
        self.assertEqual("x: 3\n---\ny: 3\n", res.getvalue())

    def test_single_json_object_as_json(self):
        res = io.StringIO()
        jinsi_main("-j", "-", _print=capture(res), _open=provide({}), _stdin=io.StringIO("""{"x":3}"""))
        self.assertEqual("""{"x":3}\n""", res.getvalue())

    def test_multi_json_object_as_json(self):
        res = io.StringIO()
        jinsi_main("-j", "-", _print=capture(res), _open=provide({}), _stdin=io.StringIO("""{"x":3}\n{"y":3}\n"""))
        self.assertEqual("""{"x":3}\n{"y":3}\n""", res.getvalue())

    def test_single_yaml_object_as_json(self):
        res = io.StringIO()
        jinsi_main("-j", "-", _print=capture(res), _open=provide({}), _stdin=io.StringIO("x: 3"))
        self.assertEqual("""{"x":3}\n""", res.getvalue())

    def test_multi_yaml_object_as_json(self):
        res = io.StringIO()
        jinsi_main("-j", "-", _print=capture(res), _open=provide({}), _stdin=io.StringIO("x: 3\n---\ny: 3\n"))
        self.assertEqual("""{"x":3}\n{"y":3}\n""", res.getvalue())


if __name__ == '__main__':
    unittest.main()
