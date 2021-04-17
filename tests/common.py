import json
import unittest
from decimal import Decimal

import yaml

from jinsi import *
from jinsi.yamlutil import Loader


class JinsiTestCase(unittest.TestCase):

    def check(self, expected, doc: str, dezimal_foo: bool = False, args: dict = None):
        rendered = render1s(doc, as_json=True, args=args)
        if dezimal_foo:
            self.assertEqual(expected, json.loads(rendered, parse_int=Decimal, parse_float=Decimal))
        else:
            self.assertEqual(expected, json.loads(rendered))

        rendered = render1s(doc, as_json=False, args=args)
        if dezimal_foo:
            self.assertEqual(expected, yaml.load(rendered, Loader=Loader))
        else:
            self.assertEqual(expected, yaml.safe_load(rendered))

        if dezimal_foo:
            loaded = load1s(doc, numtype=Decimal, args=args)
        else:
            loaded = load1s(doc, args=args)
        self.assertEqual(expected, loaded)
