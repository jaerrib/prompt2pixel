from PIL import Image

from .palette import PaletteLoader


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
        if k == 1:
            return 0, 0, 0, 255
        c: float = (1 - r - k) / (1 - k)
        m: float = (1 - g - k) / (1 - k)
        y: float = (1 - b - k) / (1 - k)
        return (
            round(c * 255),
            round(m * 255),
            round(y * 255),
            round(k * 255),
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
                if index + 2 >= len(dec_str):
                    index = 0

    def dec_to_image(
        self, dec_str: list[int], cmyk_format: bool, size: int
    ) -> Image.Image:
        img: Image.Image = self.create_image(cmyk_format, size)
        self.set_pixels(img, dec_str, cmyk_format, size)
        return img
