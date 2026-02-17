import unittest

from prompt2pixel.cli import build_parser
from prompt2pixel.hashing import HashConverter


class TestHashConverter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hash_converter = HashConverter()
        cls.parser = build_parser()
        cls.args = cls.parser.parse_args()

    def test_default_text_hash(self):
        self.assertEqual(
            self.hash_converter.text_to_hash(
                self.args.text, self.args.hash_type, self.args.salt
            ),
            "1b3dbf4b83b4bad0723c7de32e17e700331607f1b9116f3497134a84b5305b62f2b4d930b906b2b6f03c71353b08bc59d764a9c4a52566c096f573139da02bf5",
        )

    def test_alternate_text(self):
        result = self.hash_converter.text_to_hash("hello world", "sha512", "")
        self.assertEqual(
            result,
            "309ecc489c12d6eb4cc40f50c902f2b4d0ed77ee511a7c7a9bcd3ca86d4cd86f989dd35bc5ff499670da34255b45b0cfd830e81f605dcf7dc5542e93ae9cd76f",
        )

    def test_all_hash_types_match_hashlib(self):
        text = "hello world"
        salt = "mysalt"
        for algo in self.hash_converter.hash_functions:
            with self.subTest(algo=algo):
                expected = self.hash_converter.hash_functions[algo](
                    (text + salt).encode()
                ).hexdigest()
                result = self.hash_converter.text_to_hash(text, algo, salt)
                self.assertEqual(result, expected)

    def test_invalid_hash_type(self):
        with self.assertRaises(ValueError):
            self.hash_converter.text_to_hash("x", "nope", "salt")

    def test_salt_affects_output(self):
        h1 = self.hash_converter.text_to_hash("hello", "sha256", "a")
        h2 = self.hash_converter.text_to_hash("hello", "sha256", "b")
        self.assertNotEqual(h1, h2)

    def test_hash_to_dec(self):
        self.assertEqual(HashConverter.hash_to_dec("0a1b2c"), [10, 27, 44])


if __name__ == "__main__":
    unittest.main()
