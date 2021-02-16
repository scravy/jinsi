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


if __name__ == '__main__':
    unittest.main()
