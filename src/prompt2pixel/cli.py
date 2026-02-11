import argparse
import os

from halo import Halo
from wonderwords import RandomSentence

from .hashing import HashConverter
from .imagegen import ImageGenerator
from .palette import PaletteLoader
from .videogen import VideoGenerator


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

    # Load palette if provided
    palette = None
    palette_string = ""
    if palette_path:
        palette = PaletteLoader.load_gpl_palette(palette_path)
        palette_name = os.path.splitext(os.path.basename(palette_path))[0]
        palette_string = f"-{palette_name}"

    # Initialize core components
    hash_converter = HashConverter()
    image_generator = ImageGenerator(palette=palette)

    # Video mode
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
        return

    # Image mode
    with Halo(text="Generating image...", color="white"):
        hash_result = hash_converter.text_to_hash(text, hash_type, salt)
        data = hash_converter.hash_to_dec(hash_result)
        image = image_generator.dec_to_image(data, cmyk_format, size)
        resized = image.resize((vw, vh))
        clean_text = text[:-1] if random_sentence and text.endswith(".") else text
        filename = f"{clean_text[:32]}-{resized.mode}{palette_string}.jpg"
        resized.save(filename)
        print(f"\nUsed random text '{text}'") if random_sentence else None
        print(f"\nImage saved as {filename}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", default="test string")
    parser.add_argument("-c", "--cmyk_format", action="store_true")
    parser.add_argument("-r", "--random_sentence", action="store_true")
    parser.add_argument("-s", "--image_size", type=int, default=8)
    parser.add_argument("--salt", type=str, default="")
    parser.add_argument(
        "--hash-type",
        choices=HashConverter().hash_functions.keys(),
        default="sha512",
    )
    parser.add_argument("--video", action="store_true")
    parser.add_argument("--frames", type=int, default=60)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--vh", type=int, default=480)
    parser.add_argument("--vw", type=int, default=640)
    parser.add_argument("--palette", type=str, default=None)
    return parser


def run() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Handle random sentence generation
    if args.random_sentence:
        args.text = RandomSentence().simple_sentence()

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


if __name__ == "__main__":
    run()
