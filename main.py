import argparse
import hashlib
import math
import os

import cv2
import numpy as np
from halo import Halo
from PIL import Image
from wonderwords import RandomSentence


class PaletteLoader:
    @staticmethod
    def load_gpl_palette(path: str) -> list[tuple[int, int, int]]:
        palette = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line[0].isdigit():
                    parts = line.split()
                    r, g, b = map(int, parts[:3])
                    palette.append((r, g, b))
        return palette

    @staticmethod
    def nearest_color(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]]):
        r, g, b = rgb
        best = None
        best_dist = float("inf")
        for pr, pg, pb in palette:
            dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if dist < best_dist:
                best_dist = dist
                best = (pr, pg, pb)
        return best


class HashConverter:
    def __init__(self):
        self.hash_functions = {
            "sha256": hashlib.sha256,
            "sha384": hashlib.sha384,
            "sha512": hashlib.sha512,
            "sha3_256": hashlib.sha3_256,
            "sha3_384": hashlib.sha3_384,
            "sha3_512": hashlib.sha3_512,
            "blake2b": hashlib.blake2b,
            "blake2s": hashlib.blake2s,
        }

    def text_to_hash(self, text: str, hash_type: str, salt: str) -> str:
        if hash_type not in self.hash_functions:
            raise ValueError(
                f"Unsupported hash type. Supported types: {', '.join(self.hash_functions.keys())}"
            )
        return self.hash_functions[hash_type]((text + salt).encode()).hexdigest()

    @staticmethod
    def hash_to_dec(hash_string: str) -> list[int]:
        integer_list: list[int] = []
        for i in range(0, len(hash_string) - 1, 2):
            c: str = hash_string[i] + hash_string[i + 1]
            dec: int = int(c, 16)
            integer_list.append(dec)
        return integer_list


class ImageGenerator:
    def __init__(self, palette=None):
        self.palette = palette

    def map_to_palette(self, rgb: tuple[int, int, int]) -> tuple[int, int, int]:
        if not self.palette:
            return rgb
        return PaletteLoader.nearest_color(rgb, self.palette)

    @staticmethod
    def rgb_to_cmyk(rgb: list[int]) -> tuple[int, int, int] | tuple[int, int, int, int]:
        r, g, b = [x / 255.0 for x in rgb]
        k: float = 1 - max(r, g, b)
        if k == 255:
            return 0, 0, 0, 255
        c: float = (1 - r - k) / (1 - k)
        m: float = (1 - g - k) / (1 - k)
        y: float = (1 - b - k) / (1 - k)
        return (
            math.ceil(c * 255),
            math.ceil(m * 255),
            math.ceil(y * 255),
            math.ceil(k * 255),
        )

    @staticmethod
    def create_image(cmyk_format: bool, size: int) -> Image.Image:
        mode = "CMYK" if cmyk_format else "RGB"
        return Image.new(mode=mode, size=(size, size))

    def set_pixels(
        self, img: Image.Image, dec_str: list[int], cmyk_format: bool, size: int
    ) -> None:
        pixels = img.load()
        index: int = 0
        for y_pos in range(0, size):
            for x_pos in range(0, size):
                r: int = dec_str[index]
                g: int = dec_str[index + 1]
                b: int = dec_str[index + 2]
                rgb: tuple[int, int, int] = self.map_to_palette((r, g, b))
                if cmyk_format:
                    pixels[x_pos, y_pos] = self.rgb_to_cmyk(list(rgb))
                else:
                    pixels[x_pos, y_pos] = rgb
                index += 1
                if index > (len(dec_str)) / 3:
                    index = index - len(dec_str)

    def dec_to_image(
        self, dec_str: list[int], cmyk_format: bool, size: int
    ) -> Image.Image:
        img: Image.Image = self.create_image(cmyk_format, size)
        self.set_pixels(img, dec_str, cmyk_format, size)
        return img


class VideoGenerator:
    def __init__(self, hash_converter: HashConverter, image_generator: ImageGenerator):
        self.hash_converter = hash_converter
        self.image_generator = image_generator

    def create_hash_video(
        self,
        text: str,
        hash_type: str,
        frames: int,
        size: int,
        fps: int,
        vh: int,
        vw: int,
        palette_string: str,
    ) -> None:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        filename: str = text[:32] + palette_string + ".mp4"
        out = cv2.VideoWriter(filename, fourcc, fps, (vw, vh))

        with Halo(text="Generating video frames...", color="white"):
            for i in range(frames):
                hash_result = self.hash_converter.text_to_hash(text, hash_type, str(i))
                data = self.hash_converter.hash_to_dec(hash_result)
                image = self.image_generator.dec_to_image(data, False, size)
                resized_image = image.resize((vw, vh), resample=1)
                opencv_image = cv2.cvtColor(np.array(resized_image), cv2.COLOR_RGB2BGR)
                out.write(opencv_image)

        out.release()
        print(f"Video saved as {filename}")


def main(
    text: str,
    cmyk_format: bool,
    random_sentence: bool,
    size: int,
    hash_type: str,
    salt: str,
    video: bool,
    frames: int,
    image_size: int,
    fps: int,
    vh: int,
    vw: int,
    palette_path: str | None,
) -> None:
    palette = None
    palette_string = ""
    if palette_path:
        palette = PaletteLoader.load_gpl_palette(palette_path)
        palette_name: str = os.path.splitext(os.path.basename(palette_path))[0]
        palette_string = f"-{palette_name}"
    hash_converter = HashConverter()
    image_generator = ImageGenerator(palette=palette)

    if video:
        video_generator = VideoGenerator(hash_converter, image_generator)
        video_generator.create_hash_video(
            text=text,
            hash_type=hash_type,
            frames=frames,
            size=image_size,
            fps=fps,
            vh=vh,
            vw=vw,
            palette_string=palette_string,
        )
    else:
        with Halo(text="Generating image...", color="white"):
            hash_result = hash_converter.text_to_hash(text, hash_type, salt)
            data = hash_converter.hash_to_dec(hash_result)
            image = image_generator.dec_to_image(data, cmyk_format, size)
            resized = image.resize((1500, 1500), resample=1)

            text = text[:-1] if random_sentence and text[-1] == "." else text
            filename: str = (
                text[:32] + "-" + str(resized.mode) + palette_string + ".jpg"
            )

            resized.save(filename)
            print(f"\nUsed random text '{text}'") if random_sentence else None
            print(f"\nImage saved as {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "text", type=str, help="The input string", nargs="?", default="test string"
    )
    parser.add_argument(
        "-c",
        "--cmyk_format",
        help="Add to export CMYK instead of RGB",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--random_sentence",
        help="Generate a random sentence to use as text",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--image_size",
        help="Set the square size of the base image",
        type=int,
        default=8,
    )
    parser.add_argument(
        "--salt", help="Add a salt key to make the hash unique", type=str, default=""
    )
    parser.add_argument(
        "--hash-type",
        choices=HashConverter().hash_functions.keys(),
        default="sha512",
        help=f"Choose the hash algorithm to use. Available options: {', '.join(HashConverter().hash_functions.keys())}",
    )
    parser.add_argument(
        "--video", action="store_true", help="Create a video instead of a single image"
    )
    parser.add_argument(
        "--frames", type=int, default=60, help="Number of frames for video output"
    )
    parser.add_argument(
        "--fps", type=int, default=30, help="Frames per second for video output"
    )
    parser.add_argument("--vh", type=int, default=480, help="Video height dimension")
    parser.add_argument("--vw", type=int, default=640, help="Video width dimension")

    parser.add_argument(
        "--palette",
        type=str,
        help="Path to a .gpl palette file to remap image colors",
        default=None,
    )

    args = parser.parse_args()
    args.text = (
        RandomSentence().simple_sentence() if args.random_sentence else args.text
    )
    main(
        text=args.text,
        cmyk_format=args.cmyk_format,
        random_sentence=args.random_sentence,
        size=args.image_size,
        salt=args.salt,
        hash_type=args.hash_type,
        video=args.video,
        frames=args.frames,
        fps=args.fps,
        image_size=args.image_size,
        vh=args.vh,
        vw=args.vw,
        palette_path=args.palette,
    )
