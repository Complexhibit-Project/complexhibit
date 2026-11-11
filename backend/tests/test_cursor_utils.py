import unittest
import sys
import os
sys.path.append(os.getcwd())

from app.utils.cursor import encode_cursor, decode_cursor

class TestCursorUtils(unittest.TestCase):
    def test_encode_decode(self):
        label = "Test Label"
        uri = "http://example.org/123"
        
        encoded = encode_cursor(label, uri)
        print(f"Encoded: {encoded}")
        
        decoded = decode_cursor(encoded)
        print(f"Decoded: {decoded}")
        
        self.assertEqual(decoded, (label, uri))

    def test_decode_invalid(self):
        self.assertIsNone(decode_cursor("invalid_base64"))
        self.assertIsNone(decode_cursor(None))

if __name__ == "__main__":
    unittest.main()
