import argparse
import hashlib
import math

from PIL import Image
from halo import Halo
from wonderwords import RandomSentence


def text_to_sha512(text: str, salt: str) -> str:
    return hashlib.sha512((text + salt).encode()).hexdigest()


def hash_to_dec(hash_string: str) -> list[int]:
    integer_list: list[int] = []
    for i in range(0, len(hash_string) - 1, 2):
        a: str = hash_string[i]
        b: str = hash_string[i + 1]
        c: str = a + b
        dec: int = int(c, 16)
        integer_list.append(dec)
    return integer_list


def rgb_to_cmyk(rgb: list[int]) -> tuple[int, int, int] | tuple[int, int, int, int]:
    r, g, b = [x / 255.0 for x in rgb]

    k = 1 - max(r, g, b)
    if k == 255:
        return 0, 0, 0, 255

    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)

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


def dec_to_image(dec_str: list[int], cmyk_format: bool, size: int) -> Image.Image:
    img: Image.Image = create_image(cmyk_format, size)
    set_pixels(img, dec_str, cmyk_format, size)
    return img


def main(text: str, cmyk_format: bool, random_sentence: bool, size: int, salt: str) -> None:
    print("SIZE", size)
    with Halo(text="Converting data…", color="white"):
        hash_result: str = text_to_sha512(text, salt)
        data: list[int] = hash_to_dec(hash_result)
        image: Image.Image = dec_to_image(data, cmyk_format, size)
        resized: Image.Image = image.resize((1500, 1500), resample=1)
        text = text[:-1] if random_sentence and text[-1] == "." else text
        filename: str = text[:32] + "-" + str(resized.mode) + ".jpg"
        resized.save(filename)
        print(f"\nUsed random text '{text}'") if random_sentence else None
        print(f"\nImage saved as {filename}")


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
    default=16,
)
parser.add_argument(
    "--salt",
    help="Add a salt key to make the hash unique",
    type=str,
    default=""
)

args = parser.parse_args()
args.text = RandomSentence().simple_sentence() if args.random_sentence else args.text
main(
    text=args.text,
    cmyk_format=args.cmyk_format,
    random_sentence=args.random_sentence,
    size=args.image_size,
    salt=args.salt
)
