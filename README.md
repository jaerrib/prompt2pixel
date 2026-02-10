# Prompt2pixel

A small utility that uses cryptographic hashes to convert user text to an abstract image (jpg) or video (mp4)

> Please note that I use venv for my virtual environment and an alias, so I don't have to type python3. The sample
> commands below are written with that in consideration.

## How to generate an image

### Basic usage

You can generate a sample image with default settings by running `python -m main`. However, that's neither fun nor
creative. By adding one flag to the command, the utility will generate image using a random sentence:
`python -m main -r`. Alternatively, you can use your own text as input. For example, `python -m main foo`.

### Advanced usage

While the above is functional, there are also several ways to customize your output. Just add the flags as shown in the
examples.

- Export CMYK images instead of RGB by adding `-c`
- sha512 is used as the default hashing method, but you can select a specific hash by adding `--hash-type` followed by
  any of the following: sha256, sha384, sha512, sha3_256, sha3_384, sha3_512, blake2b, blake2s
- Want to add a salt key to the hash? Just add `--salt` followed by a value.
- You can also generate different types of patterns by adding `-s` with an integer.
- **prompt2pixel** can also remap the generic color palette to any valid .gpl palette with `--palette` followed by a
  path to a file

Here's an example of a more complex command to generate an image:

```python
python -m main foo -c --hash-type blake2b --salt bar -s 42 --palette spam.gpl
```

## How to generate a video

Generating a video can be as simple as adding the `--video` flag, and **prompt2pixel** will use the default settings. If
those are not sufficient, you have a bit more control over the output:

- Add `--frames` followed by an integer to set the total number of frames
- Add `--fps` followed by an integer to set the frames per second

> When these values are combined, you can influence the total length of the video. For example, 90 frames at 30 fps will
> result in 3 seconds of video.

Video generation can use the same flags as images. A much more complete and complicated command could be:

```python
python -m main foo -c --hash-type blake2b --salt bar -s 42 --palette spam.gpl --video --frames 90 --fps 30
```

## Image and video sizing

You can also determine the dimensions of both images and videos by adding `--vh` and `--vw` (video height and video width)
with integer values. **Prompt2pixel** defaults to using 640x480, but feel free to use whatever you want. Image generation
is relatively fast. However, your system specs can be a factor when making very large images or long videos.
