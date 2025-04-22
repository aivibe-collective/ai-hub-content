"""
Simple test case to verify the test environment is working.
"""

import unittest

class TestSimple(unittest.TestCase):
    """Simple test case."""
    
    def test_addition(self):
        """Test that addition works."""
        self.assertEqual(1 + 1, 2)
    
    def test_subtraction(self):
        """Test that subtraction works."""
        self.assertEqual(3 - 1, 2)
    
    def test_multiplication(self):
        """Test that multiplication works."""
        self.assertEqual(2 * 2, 4)
    
    def test_division(self):
        """Test that division works."""
        self.assertEqual(4 / 2, 2)

if __name__ == '__main__':
    unittest.main()
