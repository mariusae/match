import unittest

from match import M, A, A_

class TestMatch(unittest.TestCase):
    def test_basic(self):
        x = [1, 2, 3]

        self.assertEquals(True, ~M([1, 2, 3]) == x)
        self.assertRaises(ValueError, M((1, 2, 3)).__eq__, x)
        self.assertEquals(tuple(), M([1, A_, 3]) == x)
        self.assertEquals((3,), M([1, A_, A/0]) == x)
        self.assertEquals((3, 1), M([A/2, A_, A/0]) == x)

    def test_nested(self):
        x = [1, 2, 3]
        y = [1, x, x, 4]

        self.assertEquals((x,), M([1, x, A/0, 4]) == y)
        self.assertRaises(ValueError, M([1, [1, 3, 2], A/0, 4]).__eq__, y)
        self.assert_(not ~M([1, [1, 3, 2], A/0, 4]) == y)
        self.assertEquals((1, 2, 2), M([1, [1, A/1, 3], [A/0, A/2, 3], A_]) == y)


if __name__ == '__main__':
    unittest.main()

    
