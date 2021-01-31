import unittest

from apm import *
from dezimal import *

from jinsi import *


class LoadTest(unittest.TestCase):

    def test_load(self):
        doc = load1s("""\
            foo: bar
            qux: quux
            """)
        self.assertTrue(match(doc, Strict(Object(
            foo='bar',
            qux='quux',
        ))))

    def test_load_dezimal(self):
        doc = load1s("""\
            foo: 1.34
            """, numtype=Dezimal)
        self.assertFalse(match(doc, Strict(Object(
            foo=Strict(float("1.34"))
        ))))
        self.assertTrue(match(doc, Strict(Object(
            foo=Strict(Dezimal("1.34"))
        ))))

    def test_load_float(self):
        doc = load1s("""\
            foo: 1.34
            """)
        self.assertFalse(match(doc, Strict(Object(
            foo=Strict(Dezimal("1.34"))
        ))))
        self.assertTrue(match(doc, Strict(Object(
            foo=Strict(float("1.34"))
        ))))

    def test_load_verbatim_and_ignore(self):
        doc = load1s("""\
            foo:
              ::verbatim:
                some text
            ::ignore:
              some shit
        """)
        self.assertEqual({'foo': 'some text'}, doc)

    def test_load_verbatim_object(self):
        doc = load1s("""\
            ::let:
                x: 'x'
            foo:
              qu<<x>>: quuz
            ::ignore:
              some shit
        """)
        self.assertEqual({'foo': {'qux': 'quuz'}}, doc)
        doc = load1s("""\
            ::let:
                x: 'x'
            foo:
              ::verbatim:
                qu<<x>>: quuz
            ::ignore:
              some shit
        """)
        self.assertEqual({'foo': {'qu<<x>>': 'quuz'}}, doc)


if __name__ == '__main__':
    unittest.main()
