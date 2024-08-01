import hashlib

from PIL import Image


def text_to_sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def hash_to_dec(s):
    d = []
    for i in range(0, len(s) - 1, 2):
        a = s[i]
        b = s[i + 1]
        c = a + b
        dec = int(c, 16)
        d.append(dec)
    return d


def dec_to_image(dec_str):
    size = (8, 8)
    img = Image.new("RGB", size)
    pixels = img.load()
    index = 0
    for i in range(size[0]):
        for j in range(size[1]):
            r = dec_str[index]
            g = dec_str[index + 1]
            b = dec_str[index + 2]
            pixels[i, j] = (r, g, b)
            index += 1
            if index > len(dec_str) / 3:
                index = index - len(dec_str)
    return img


def main():
    print("Enter a string: ")
    text = input()
    hash_result = text_to_sha256(text)
    data = hash_to_dec(hash_result)
    image = dec_to_image(data)
    resized = image.resize((1500, 1500), resample=1)
    resized.show()
    resized.save("output.png")


main()
