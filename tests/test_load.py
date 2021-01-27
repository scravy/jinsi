import unittest

from apm import *
from dezimal import *

from jinsi import *


class LoadTest(unittest.TestCase):

    def test_load(self):
        doc = load_yaml("""\
            foo: bar
            qux: quux
            """)
        self.assertTrue(match(doc, Strict(Object(
            foo='bar',
            qux='quux',
        ))))

    def test_load_dezimal(self):
        doc = load_yaml("""\
            foo: 1.34
            """, numtype=Dezimal)
        self.assertFalse(match(doc, Strict(Object(
            foo=Strict(float("1.34"))
        ))))
        self.assertTrue(match(doc, Strict(Object(
            foo=Strict(Dezimal("1.34"))
        ))))

    def test_load_float(self):
        doc = load_yaml("""\
            foo: 1.34
            """)
        self.assertFalse(match(doc, Strict(Object(
            foo=Strict(Dezimal("1.34"))
        ))))
        self.assertTrue(match(doc, Strict(Object(
            foo=Strict(float("1.34"))
        ))))

    def test_load_verbatim_and_ignore(self):
        doc = load_yaml("""\
            foo:
              ::verbatim:
                some text
            ::ignore:
              some shit
        """)
        self.assertEqual({'foo': 'some text'}, doc)
