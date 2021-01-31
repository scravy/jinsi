import textwrap
import unittest

from jinsi.yamlutil import dumpyaml


class YamlDumpTest(unittest.TestCase):

    def test_dump_yaml(self):
        self.assertEqual(textwrap.dedent("""\
            xyz: 123
            abc: 789
        """), dumpyaml({
            "xyz": 123,
            "abc": 789,
        }))


if __name__ == '__main__':
    unittest.main()
