import unittest

from jinsi.functions import Functions


class FunctionsTest(unittest.TestCase):
    def test_concat_list(self):
        self.assertEqual([1, 2, 3], Functions.concat([1, 2], [3]))

    def test_concat_string(self):
        self.assertEqual("123", Functions.concat("12", "3"))

    def test_drop_right_list(self):
        self.assertEqual([1, 2], Functions.drop_right(2, [1, 2, 3, 4]))

    def test_drop_list(self):
        self.assertEqual([3, 4], Functions.drop(2, [1, 2, 3, 4]))

    def test_drop_right_string(self):
        self.assertEqual("ab", Functions.drop_right(2, "abcd"))

    def test_drop_string(self):
        self.assertEqual("cd", Functions.drop(2, "abcd"))

    def test_take_right_list(self):
        self.assertEqual([3, 4], Functions.take_right(2, [1, 2, 3, 4]))

    def test_take_list(self):
        self.assertEqual([1, 2], Functions.take(2, [1, 2, 3, 4]))

    def test_take_right_string(self):
        self.assertEqual("cd", Functions.take_right(2, "abcd"))

    def test_take_string(self):
        self.assertEqual("ab", Functions.take(2, "abcd"))

    def test_pad_left(self):
        self.assertEqual("00123", Functions.pad_left("123", "0", "5"))

    def test_pad_right(self):
        self.assertEqual("12300", Functions.pad_right("123", "0", "5"))

    def test_replace(self):
        self.assertEqual("foo qux bar foo qux", Functions.str_replace("foo", "foo qux", "foo bar foo"))

    def test_deepmerge(self):
        def o(**kw):
            return kw

        self.assertEqual(o(a=1, b=2, c=3), Functions.deepmerge(o(a=1), o(b=2), o(c=3)))
        self.assertEqual(o(a=1, b=2, c=3), Functions.deepmerge(o(a=8), o(b=2, a=1), o(c=3)))
        self.assertEqual(o(a=1, b=o(c=7)), Functions.deepmerge(o(a=1, b=o(c=3)), o(b=o(c=7))))

    def test_flatten(self):
        self.assertEqual([1, 2, 3], Functions.flatten([[1], [2, 3]]))

    def test_deepflatten(self):
        self.assertEqual([1, 2, 3, 4], Functions.deepflatten([1], [[2], [[3, 4]]]))


if __name__ == '__main__':
    unittest.main()
