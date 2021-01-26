import textwrap
import unittest

from jinsi import dumpyaml


class YamlDumpTest(unittest.TestCase):

    def test_dump_yaml(self):
        self.assertEqual(textwrap.dedent("""\
            abc: 123
            xyz: 789
        """), dumpyaml({
            "xyz": 789,
            "abc": 123,
        }))
