import unittest

from .common import JinsiTestCase


class JinsiExamples(JinsiTestCase):

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

        self.check(expected, doc)

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

        self.check(expected, doc)

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

        self.check(expected, doc)

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

        self.check(expected, doc)

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

        self.check(expected, doc)


if __name__ == '__main__':
    unittest.main()
