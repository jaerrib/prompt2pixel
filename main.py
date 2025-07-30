import argparse
import hashlib
import math

from PIL import Image
from halo import Halo
from wonderwords import RandomSentence

SIZE: tuple[int, int] = (8, 8)


def text_to_sha512(text: str) -> str:
    return hashlib.sha512(text.encode()).hexdigest()


def hash_to_dec(hash_string: str) -> list[int]:
    integer_list = []
    for i in range(0, len(hash_string) - 1, 2):
        a = hash_string[i]
        b = hash_string[i + 1]
        c = a + b
        dec = int(c, 16)
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


def create_image(cmyk_format: bool) -> Image.Image:
    if cmyk_format:
        img = Image.new("CMYK", SIZE)
    else:
        img = Image.new("RGB", SIZE)
    return img


def set_pixels(img: Image.Image, dec_str: list[int], cmyk_format: bool) -> None:
    pixels = img.load()
    index = 0
    for y_pos in range(SIZE[0]):
        for x_pos in range(SIZE[1]):
            r = dec_str[index]
            g = dec_str[index + 1]
            b = dec_str[index + 2]
            if cmyk_format:
                c, m, y, k = rgb_to_cmyk([r, g, b])
                pixels[x_pos, y_pos] = (c, m, y, k)
            else:
                pixels[x_pos, y_pos] = (r, g, b)
            index += 1
            if index > (len(dec_str)) / 3:
                index = index - len(dec_str)


def dec_to_image(dec_str: list[int], cmyk_format: bool) -> Image.Image:
    img = create_image(cmyk_format)
    set_pixels(img, dec_str, cmyk_format)
    return img


def main(text: str, cmyk_format: bool, random_sentence: bool) -> None:
    with Halo(text="Converting data…", color="white"):
        hash_result = text_to_sha512(text)
        data = hash_to_dec(hash_result)
        image = dec_to_image(data, cmyk_format)
        resized = image.resize((1500, 1500), resample=1)
        filename = text[:32] + "-" + str(resized.mode) + ".jpg"
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

args = parser.parse_args()
args.text = RandomSentence().simple_sentence() if args.random_sentence else args.text
main(text=args.text, cmyk_format=args.cmyk_format, random_sentence=args.random_sentence)
