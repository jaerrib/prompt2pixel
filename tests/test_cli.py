import unittest
from unittest.mock import MagicMock, patch

from prompt2pixel.cli import build_parser, main


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


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.default_kwargs = dict(
            text="hello",
            cmyk_format=False,
            random_sentence=False,
            size=8,
            hash_type="sha512",
            salt="",
            video=False,
            frames=60,
            image_size=8,
            fps=30,
            vh=480,
            vw=640,
            palette_path=None,
        )

    @patch("prompt2pixel.cli.ImageGenerator")
    @patch("prompt2pixel.cli.HashConverter")
    @patch("prompt2pixel.cli.Halo")
    def test_main_generates_image(self, mock_halo, mock_hash, mock_imagegen):
        kwargs = self.default_kwargs.copy()
        mock_hash.return_value.text_to_hash.return_value = "abc123"
        mock_hash.return_value.hash_to_dec.return_value = [1, 2, 3]
        mock_img = MagicMock()
        mock_img.resize.return_value = mock_img
        mock_imagegen.return_value.dec_to_image.return_value = mock_img
        main(**kwargs)
        mock_hash.return_value.text_to_hash.assert_called_once()
        mock_imagegen.return_value.dec_to_image.assert_called_once()
        mock_img.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
