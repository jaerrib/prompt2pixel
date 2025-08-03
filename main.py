import argparse
import hashlib
import math

import cv2
import numpy as np
from PIL import Image
from halo import Halo
from wonderwords import RandomSentence

hash_functions = {
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "sha3_256": hashlib.sha3_256,
    "sha3_384": hashlib.sha3_384,
    "sha3_512": hashlib.sha3_512,
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
}


def text_to_hash(text: str, hash_type: str, salt: str) -> str:
    if hash_type not in hash_functions:
        raise ValueError(
            f"Unsupported hash type. Supported types: {', '.join(hash_functions.keys())}"
        )
    return hash_functions[hash_type]((text + salt).encode()).hexdigest()


def hash_to_dec(hash_string: str) -> list[int]:
    integer_list: list[int] = []
    for i in range(0, len(hash_string) - 1, 2):
        a: str = hash_string[i]
        b: str = hash_string[i + 1]
        c: str = a + b
        dec: int = int(c, 16)
        integer_list.append(dec)
    return integer_list


def dec_to_image(dec_str: list[int], cmyk_format: bool, size: int) -> Image.Image:
    img: Image.Image = create_image(cmyk_format, size)
    set_pixels(img, dec_str, cmyk_format, size)
    return img


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


def create_image(cmyk_format: bool, size: int) -> Image.Image:
    if cmyk_format:
        img: Image.Image = Image.new(mode="CMYK", size=(size, size))
    else:
        img: Image.Image = Image.new(mode="RGB", size=(size, size))
    return img


def set_pixels(
    img: Image.Image, dec_str: list[int], cmyk_format: bool, size: int
) -> None:
    pixels: Image = img.load()
    index: int = 0
    for y_pos in range(0, size):
        for x_pos in range(0, size):
            r: int = dec_str[index]
            g: int = dec_str[index + 1]
            b: int = dec_str[index + 2]
            if cmyk_format:
                c, m, y, k = rgb_to_cmyk([r, g, b])
                pixels[x_pos, y_pos] = (c, m, y, k)
            else:
                pixels[x_pos, y_pos] = (r, g, b)
            index += 1
            if index > (len(dec_str)) / 3:
                index = index - len(dec_str)


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
) -> None:
    with Halo(text="Converting data…", color="white"):
        if video:
            create_hash_video(
                text=text,
                hash_type=hash_type,
                frames=frames,
                size=image_size,
                fps=fps,
                vh=vh,
                vw=vw,
            )
        else:
            hash_result: str = text_to_hash(text=text, hash_type=hash_type, salt=salt)
            data: list[int] = hash_to_dec(hash_string=hash_result)
            image: Image.Image = dec_to_image(
                dec_str=data, cmyk_format=cmyk_format, size=size
            )
            resized: Image.Image = image.resize((1500, 1500), resample=1)
            text = text[:-1] if random_sentence and text[-1] == "." else text
            filename: str = text[:32] + "-" + str(resized.mode) + ".jpg"
            resized.save(filename)
            print(f"\nUsed random text '{text}'") if random_sentence else None
            print(f"\nImage saved as {filename}")


def create_hash_video(
    text: str,
    hash_type: str,
    frames: int,
    size: int,
    fps: int,
    vh: int,
    vw: int,
    output_file: str = "hash_animation.mp4",
) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, fps, (vw, vh))
    with Halo(text="Generating video frames...", color="white"):
        for i in range(frames):
            hash_result = text_to_hash(text, hash_type=hash_type, salt=str(i))
            data = hash_to_dec(hash_result)
            pil_image = dec_to_image(data, cmyk_format=False, size=size)
            resized_image = pil_image.resize((vw, vh), resample=1)
            opencv_image = cv2.cvtColor(np.array(resized_image), cv2.COLOR_RGB2BGR)
            out.write(opencv_image)
    out.release()
    print(f"Video saved as {output_file}")


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
    choices=list(hash_functions.keys()),
    default="sha512",
    help=f"Choose the hash algorithm to use. Available options: {', '.join(hash_functions.keys())}",
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


args = parser.parse_args()
args.text = RandomSentence().simple_sentence() if args.random_sentence else args.text
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
)
