# Prompt2pixel

 A small utility that converts user-provided text into abstract images (JPG) or videos (MP4) by hashing the text and
 mapping the resulting bytes into pixel data. The project is now organized into modules (`hashing.py`, `palette.py`,
 `imagegen.py`, etc.) for easier maintenance and extension.

> These examples assume you're using a virtual environment and calling python directly. Adjust as needed for your setup.

---

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

## Installation in editable (development) mode

If you want to work on the codebase or make changes locally, install the package in editable mode:

```bash
pip install -e .
```

This links the package to your working directory so changes take effect immediately. After installing (editable or
normal), you can run `python -m prompt2pixel` from any directory.

---

## Running the tool

```bash
python -m prompt2pixel
```

To generate an image using your own text:

```bash
python -m prompt2pixel "hello world"
```

To generate a random sentence:

```bash
python -m prompt2pixel -r
```

---

## Generating an image

### Basic usage

Running the CLI with no flags generates an RGB image using default settings:

```bash
python -m prompt2pixel "foo"
```

Or let the tool generate a random sentence:

```bash
python -m prompt2pixel -r
```

![Example](/example_output/test_string-RGB.jpg "Sample image using the default settings")

### Advanced options

You can customize the output using flags:

- `-c`  
  Export CMYK instead of RGB.

- `--hash-type <algorithm>`  
  Choose from:  
  `sha256`, `sha384`, `sha512`, `sha3_256`, `sha3_384`, `sha3_512`, `blake2b`, `blake2s`

- `--salt <value>`  
  Add a salt to the hash.

- `-s <int>`  
  Set the base square size of the generated image.

- `--palette <path>`  
  Remap colors using a `.gpl` palette file.

Example:

```bash
python -m prompt2pixel "foo" -c --hash-type blake2b --salt bar -s 42 --palette spam.gpl
```

---

## Generating a video

Add the `--video` flag to switch from image mode to video mode:

```bash
python -m prompt2pixel "foo" --video
```

You can customize video output:

- `--frames <int>`  
  Number of frames to generate.

- `--fps <int>`  
  Frames per second.

- `--vh <int>`  
  Video height.

- `--vw <int>`  
  Video width.

Example:

```bash
python -m prompt2pixel "foo" --video --frames 90 --fps 30 --palette spam.gpl
```


> For reference: 90 frames at 30 fps produces a 3-second video.

---

## Image and video sizing

Both images and videos can be resized using:

- `--vh` (video height)
- `--vw` (video width)

Default output size is **640x480**, but you can set any dimensions your system can handle.

---

## Project structure

The project is now organized into modules:

```bash
prompt2pixel/
    cli.py
    hashing.py
    palette.py
    imagegen.py
    videogen.py
```

This modular layout makes it easier to extend the tool. For example, adding new hash algorithms, color spaces, or output formats.

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

See the [LICENSE](LICENSE) file for the full text.
