
# 🖼️ LSB Steganography Tool (GUI + CLI)

This Python script allows embedding and extraction of secret messages in images using **Least Significant Bit (LSB) steganography**. It supports both **graphical user interface (GUI)** and **command-line interface (CLI)** modes.

---

## 📦 Requirements

- Python 3.x
- `tkinter` (usually included with Python)
- `Pillow` library (`pip install pillow`)

---

## 🛠️ Features

- **Embed messages** in image files using LSB encoding.
- **Extract messages** hidden within images.
- **User-friendly GUI** for both embedding and extraction.
- **CLI mode** for automation and scripting.

---

## 🧪 Functions Overview

### 🔣 `text_to_bits(text)`
Converts a text string into its binary representation.

### 🧾 `bits_to_text(bits)`
Reconstructs the original text from a binary string.

---

### 🖊️ `embed_text_on_image(image_path, message)`
Embeds a message into an image using the least significant bits of each color channel.
- Adds a special delimiter (`#####END#####`) to signify the message's end.
- Creates a new image file prefixed with `Embedded-`.
- Returns the new image's filename.

**Raises**:
- `ValueError`: If the message is too large for the image.
- `FileNotFoundError`: If the specified image is missing.

---

### 🕵️ `extract_text_from_image(image_path)`
Reads the LSBs of the image and reconstructs the embedded message until it finds the `#####END#####` delimiter.

Returns the decoded message string.

---

### 🖼️ `run_embedding_gui()`
Opens a GUI that allows:
- Selecting an image
- Typing a message
- Embedding the message into the image

---

### 🔍 `run_extraction_gui()`
GUI interface to:
- Load an image with an embedded message
- Extract and display the hidden message

---

## 💻 Command-Line Usage

### Embed Message
```bash
python lsb.py -e -i <image.png> -m "your secret message"
```

### Extract Message
```bash
python lsb.py -x -i <Embedded-image.png>
```

### Run Embedding GUI
```bash
python lsb.py -gui_e
```

### Run Extraction GUI
```bash
python lsb.py -gui_x
```

---

## 📁 Output

When embedding, the tool generates a new PNG file in the same directory:
```
Embedded-<original_filename>.png
```

---

## ⚠️ Notes

- The message capacity is limited by the image size: each pixel can store up to 3 bits (1 bit per RGB channel).
- Only PNG or lossless image formats are recommended to avoid corruption during saving/compression.

---

## 📌 Example

```bash
python lsb.py -e -i image.png -m "The treasure is buried under the oak tree."
```

Result: An image named `Embedded-image.png` containing the hidden message.
