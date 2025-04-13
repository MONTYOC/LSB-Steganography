import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import sys
import os  # Import the os module

def text_to_bits(text):
    """Converts a string of text into a string of bits."""
    bits = ''.join(format(ord(char), '08b') for char in text)
    return bits

def bits_to_text(bits):
    """Converts a string of bits back into a string of text."""
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def embed_text_on_image(image_path, message):
    """Embeds text into the least significant bits of an image."""
    try:
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        data = list(img.getdata())
        binary_message = text_to_bits(message + "#####END#####") # Add a delimiter
        message_index = 0

        if len(binary_message) > width * height * 3:
            raise ValueError("Text is too long to hide in this image.")

        modified_data = []
        for pixel in data:
            r, g, b = pixel
            if message_index < len(binary_message):
                r = (r & ~1) | int(binary_message[message_index])
                message_index += 1
            if message_index < len(binary_message):
                g = (g & ~1) | int(binary_message[message_index])
                message_index += 1
            if message_index < len(binary_message):
                b = (b & ~1) | int(binary_message[message_index])
                message_index += 1
            modified_data.append((r, g, b))

        filename = os.path.basename(image_path)  # Extract the filename
        new_filename = "Embedded-" + filename # Use only the filename

        modified_img = Image.new("RGB", (width, height))
        modified_img.putdata(modified_data)
        modified_img.save(new_filename, "PNG")
        messagebox.showinfo("Embedding Successful", f"Message embedded. Saved as '{new_filename}'")
        print(f"Text successfully encoded into '{new_filename}'")
        return new_filename

    except FileNotFoundError:
        messagebox.showerror("Error", f"Image file '{image_path}' not found.")
        return None
    except ValueError as e:
        messagebox.showerror("Error", f"An error occurred during embedding: {e}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred during embedding: {e}")
        return None

def extract_text_from_image(image_path):
    """Extracts hidden text from the least significant bits of an image."""
    try:
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        data = list(img.getdata())
        binary_message = ""

        for pixel in data:
            r, g, b = pixel
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

        decoded_text = ""
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i+8]
            if len(byte) == 8:
                char = chr(int(byte, 2))
                decoded_text += char
                if decoded_text.endswith("#####END#####"):
                    decoded_text = decoded_text[:-11] # Remove the delimiter
                    break
            else:
                break

        messagebox.showinfo("Extraction Successful", f"Extracted Message: '{decoded_text}'")
        print(f"Decoded text: '{decoded_text}'")
        return decoded_text

    except FileNotFoundError:
        messagebox.showerror("Error", f"Image file '{image_path}' not found.")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during extraction: {e}")
        return None

def run_embedding_gui():
    """Runs the embedding GUI (interactive) with LSB embedding."""
    def select_image():
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if filepath:
            img = Image.open(filepath)
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            left_square.create_image(100, 100, image=photo)
            left_square.image = photo
            root.image_path = filepath  # Store the image path

    def get_message():
        message = simpledialog.askstring("Embed Message", "Enter the message to embed:")
        if message:
            root.message_to_embed = message

    def embed_interactive():
        if hasattr(root, 'image_path') and hasattr(root, 'message_to_embed'):
            embed_text_on_image(root.image_path, root.message_to_embed)
        else:
            messagebox.showerror("Error", "Please select an image and enter a message.")

    root = tk.Tk()
    root.title("Interactive Embedding Tool (LSB)")
    root.configure(bg="gray")
    root.image_path = None
    root.message_to_embed = None

    left_square = tk.Canvas(root, width=200, height=200, bg="white")
    left_square.grid(row=0, column=0, padx=10, pady=10)

    arrow_canvas = tk.Canvas(root, width=50, height=200, bg="gray", highlightthickness=0)
    arrow_canvas.grid(row=0, column=1)
    arrow_canvas.create_line(10, 100, 40, 100, arrow=tk.LAST, width=3)

    output_label = tk.Label(root, text="Ready to Embed (LSB)", bg="gray", fg="white")
    output_label.grid(row=0, column=2, padx=10, pady=10)

    select_image_button = tk.Button(root, text="Select Image", command=select_image)
    select_image_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    enter_message_button = tk.Button(root, text="Enter Message", command=get_message)
    enter_message_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    embed_button = tk.Button(root, text="Embed", command=embed_interactive)
    embed_button.grid(row=1, column=1, padx=10, pady=5)

    root.mainloop()

def run_extraction_gui():
    """Runs the extraction GUI (interactive) with LSB extraction."""
    def select_image():
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if filepath:
            img = Image.open(filepath)
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            left_square.create_image(100, 100, image=photo)
            left_square.image = photo
            root.image_path = filepath

    def extract_interactive():
        if hasattr(root, 'image_path'):
            extract_text_from_image(root.image_path)
        else:
            messagebox.showerror("Error", "Please select an image.")

    root = tk.Tk()
    root.title("Interactive Extraction Tool (LSB)")
    root.configure(bg="gray")
    root.image_path = None

    left_square = tk.Canvas(root, width=200, height=200, bg="white")
    left_square.grid(row=0, column=0, padx=10, pady=10)

    arrow_canvas = tk.Canvas(root, width=50, height=200, bg="gray", highlightthickness=0)
    arrow_canvas.grid(row=0, column=1)
    arrow_canvas.create_line(10, 100, 40, 100, arrow=tk.LAST, width=3)

    right_label = tk.Label(root, text="Decoded Text", bg="gray", fg="white")
    right_label.grid(row=0, column=2, padx=10, pady=10)

    select_image_button = tk.Button(root, text="Select Stego Image", command=select_image)
    select_image_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    extract_button = tk.Button(root, text="Extract", command=extract_interactive)
    extract_button.grid(row=1, column=1, padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "-e":
            if len(sys.argv) >= 5 and sys.argv[2].lower() == "-i" and sys.argv[4].lower() == "-m":
                image_file = sys.argv[3]
                message_to_embed = sys.argv[5].strip('"')
                embed_text_on_image(image_file, message_to_embed)
            else:
                print("Usage for embedding: python lsb.py -e -i <image.png> -m \"your message\"")
        elif sys.argv[1].lower() == "-x":
            if len(sys.argv) >= 3 and sys.argv[2].lower() == "-i":
                image_file = sys.argv[3]
                extract_text_from_image(image_file)
            else:
                print("Usage for extraction: python lsb.py -x -i <Stego-image.png>")
        elif sys.argv[1].lower() == "-gui_e":
            run_embedding_gui()
        elif sys.argv[1].lower() == "-gui_x":
            run_extraction_gui()
        else:
            print("""Usage: python lsb.py [-e -i <image.png> -m \"message\"] 
            or [-x -i <stego.png>] or [-gui_e] or [-gui_x]""")
    else:
        print("""Usage: python lsb.py [-e -i <image.png> -m \"message\"] 
            or [-x -i <stego.png>] or [-gui_e] or [-gui_x]""")