import argparse
import hashlib

from PIL import Image
from halo import Halo


def text_to_sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def hash_to_dec(hash_string: str) -> list[int]:
    integer_list = []
    for i in range(0, len(hash_string) - 1, 2):
        a = hash_string[i]
        b = hash_string[i + 1]
        c = a + b
        dec = int(c, 16)
        integer_list.append(dec)
    return integer_list


def dec_to_image(dec_str: list[int]) -> Image.Image:
    size = (8, 8)
    img = Image.new("RGB", size)
    pixels = img.load()
    index = 0
    for y in range(size[0]):
        for x in range(size[1]):
            r = dec_str[index]
            g = dec_str[index + 1]
            b = dec_str[index + 2]
            pixels[y, x] = (r, g, b)
            index += 1
            if index > len(dec_str) / 3:
                index = index - len(dec_str)
    return img


def main(text: str, cmyk_format: bool) -> None:
    with Halo(text="Converting data…", color="white"):
        hash_result = text_to_sha256(text)
        data = hash_to_dec(hash_result)
        image = dec_to_image(data)
        resized = image.resize((1500, 1500), resample=1)
        if cmyk_format:
            resized = resized.convert("CMYK")
        filename = text + "-" + str(resized.mode) + ".jpg"
        resized.show()
        resized.save(filename)


parser = argparse.ArgumentParser()
parser.add_argument("text", type=str, help="The input string")
parser.add_argument(
    "-c",
    "--cmyk_format",
    help="Add to export CMYK instead of RGB",
    action="store_true",
)
args = parser.parse_args()
main(text=args.text, cmyk_format=args.cmyk_format)
