import unittest
from unittest.mock import patch

from prompt2pixel.cli import build_parser


class TestCLIParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = build_parser()

    def test_defaults(self):
        args = self.parser.parse_args([])

        self.assertEqual(args.text, "test string")
        self.assertFalse(args.cmyk_format)
        self.assertFalse(args.random_sentence)
        self.assertEqual(args.image_size, 8)
        self.assertEqual(args.salt, "")
        self.assertEqual(args.hash_type, "sha512")
        self.assertFalse(args.video)
        self.assertEqual(args.frames, 60)
        self.assertEqual(args.fps, 30)
        self.assertEqual(args.vh, 480)
        self.assertEqual(args.vw, 640)
        self.assertIsNone(args.palette)

    def test_text_override(self):
        args = self.parser.parse_args(["hello world"])
        self.assertEqual(args.text, "hello world")

    def test_video_flag(self):
        args = self.parser.parse_args(["--video"])
        self.assertTrue(args.video)

    def test_cmyk_flag(self):
        args = self.parser.parse_args(["--cmyk_format"])
        self.assertTrue(args.cmyk_format)

    def test_random_sentence_flag(self):
        args = self.parser.parse_args(["--random_sentence"])
        self.assertTrue(args.random_sentence)

    def test_frames_flag(self):
        args = self.parser.parse_args(["--frames", "120"])
        self.assertEqual(args.frames, 120)

    def test_fps_flag(self):
        args = self.parser.parse_args(["--fps", "12"])
        self.assertEqual(args.fps, 12)

    def test_image_size_flag(self):
        args = self.parser.parse_args(["--image_size", "16"])
        self.assertEqual(args.image_size, 16)

    def test_dimensions_flags(self):
        args = self.parser.parse_args(["--vh", "720", "--vw", "1280"])
        self.assertEqual(args.vh, 720)
        self.assertEqual(args.vw, 1280)

    def test_salt_flag(self):
        args = self.parser.parse_args(["--salt", "pepper"])
        self.assertEqual(args.salt, "pepper")

    def test_palette_flag(self):
        args = self.parser.parse_args(["--palette", "colors.gpl"])
        self.assertEqual(args.palette, "colors.gpl")

    def test_hash_type_choice(self):
        args = self.parser.parse_args(["--hash-type", "sha256"])
        self.assertEqual(args.hash_type, "sha256")

    @patch("sys.stderr")
    def test_hash_type_invalid(self, _mock_stderr):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["--hash-type", "notahash"])


if __name__ == "__main__":
    unittest.main()
