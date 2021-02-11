import json
import unittest

import dezimal
import yaml

from jinsi import *
from jinsi.yamlutil import Loader


class JinsiExamples(unittest.TestCase):

    def _check(self, expected, doc: str, dezimal_foo: bool = False, args: dict = None):
        rendered = render1s(doc, as_json=True, args=args)
        if dezimal_foo:
            self.assertEqual(expected, json.loads(rendered, parse_int=dezimal.Dezimal, parse_float=dezimal.Dezimal))
        else:
            self.assertEqual(expected, json.loads(rendered))

        rendered = render1s(doc, as_json=False, args=args)
        if dezimal_foo:
            self.assertEqual(expected, yaml.load(rendered, Loader=Loader))
        else:
            self.assertEqual(expected, yaml.safe_load(rendered))

        if dezimal_foo:
            loaded = load1s(doc, numtype=dezimal.Dezimal, args=args)
        else:
            loaded = load1s(doc, args=args)
        self.assertEqual(expected, loaded)

    def test_flatten(self):
        doc = """\
            ::let:
                xs:
                    - - 1
                    - - 2
                    - - 3
            xs:
                ::flatten:
                    ::get: xs
        """

        expected = {
            'xs': [1, 2, 3]
        }

        self._check(expected, doc)

    def test_select_from_list(self):
        doc = """\
            ::let:
                xs:
                    - - 1
                    - - 2
                    - - 3
            xs:
                ::select:
                    - ::get: xs
                    - 1
        """

        expected = {
            'xs': [2]
        }

        self._check(expected, doc)

    def test_select_from_object(self):
        doc = """\
            ::let:
                xs:
                    foo: 1
                    bar: 2
            xs:
                ::select:
                    - ::get: xs
                    - bar
        """

        expected = {
            'xs': 2
        }

        self._check(expected, doc)

    def test_select_range_from_list(self):
        doc = """\
            ::let:
                xs:
                    - 1
                    - 2
                    - 3
            xs:
                ::select:
                    - ::get: xs
                    - 0
                    - 2
        """

        expected = {
            'xs': [1, 2]
        }

        self._check(expected, doc)

    def test_select_range_from_string(self):
        doc = """\
            ::let:
                xs: "abc"
            xs:
                ::select:
                    - ::get: xs
                    - 0
                    - 2
        """

        expected = {
            'xs': "ab"
        }

        self._check(expected, doc)


if __name__ == '__main__':
    unittest.main()
