import unittest

from .common import JinsiTestCase


class JinsiExamples(JinsiTestCase):

    def test_conditional_with_let(self):
        doc = """\
            ::let:
                a: 1
            ::when:
                ::get: a == 1
            ::then:
                foo: one
            ::else:
                bar: two
        """

        expected = {'foo': 'one'}

        self.check(expected, doc)

    def test_when_with_let(self):
        doc = """\
            ::when:
                ::let:
                    a: 1
                ::get: a == 1
            ::then:
                foo: one
            ::else:
                bar: two
        """

        expected = {'foo': 'one'}

        self.check(expected, doc)

    def test_case(self):
        doc = """\
            value:
                ::let:
                    x: 3
                ::case:
                    x == 1: one
                    x == 2: two
                    x == 3: three
                    x == 4: four
        """

        expected = {'value': 'three'}

        self.check(expected, doc)


if __name__ == '__main__':
    unittest.main()
