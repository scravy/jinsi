import textwrap
import unittest

from jinsi import dumpyaml


class YamlDumpTest(unittest.TestCase):

    def test_dump_yaml(self):
        self.assertEqual(textwrap.dedent("""\
            xyz: 123
            abc: 789
        """), dumpyaml({
            "xyz": 123,
            "abc": 789,
        }))
