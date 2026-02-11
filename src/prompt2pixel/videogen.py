import cv2
import numpy as np
from halo import Halo


class VideoGenerator:
    def __init__(self, hash_converter, image_generator):
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
