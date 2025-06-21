import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
from math import log10, sqrt
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

def calculate_psnr(original_image_path, stego_image_path):
    """Calculates the PSNR between the original and stego images."""
    try:
        original_img = Image.open(original_image_path).convert("RGB")
        stego_img = Image.open(stego_image_path).convert("RGB")
        original_data = list(original_img.getdata()) # type: ignore
        stego_data = list(stego_img.getdata()) #type: ignore

        if len(original_data) != len(stego_data):
            print("Original and stego images have different dimensions.")
            return None

        mse_sum = 0
        for i in range(len(original_data)):
            r1, g1, b1 = original_data[i]
            r2, g2, b2 = stego_data[i]
            mse_sum += (r1 - r2) ** 2
            mse_sum += (g1 - g2) ** 2
            mse_sum += (b1 - b2) ** 2

        mse = mse_sum / (len(original_data) * 3)

        if mse == 0:
            return float('inf')  # Perfect match
        psnr = 10 * log10((255 ** 2) / mse)
        return psnr
    except Exception as e:
        print(f"Error calculating PSNR: {e}")
        return None

def embed_text_on_image(image_path, message):
    """Embeds text into the least significant bits of an image."""
    try:
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        data = list(img.getdata()) # type: ignore
        binary_message = text_to_bits(message + "#####END#####") # Add a delimiter
        message_index = 0

        if len(binary_message) > width * height * 3:
            raise ValueError("Text is too long to hide in this image.")

        modified_data = []
        bit_changes = 0  # Track the number of bits changed
        for pixel in data:
            r, g, b = pixel
            if message_index < len(binary_message):
                new_r = (r & ~1) | int(binary_message[message_index])
                bit_changes += (new_r != r)
                r = new_r
                message_index += 1
            if message_index < len(binary_message):
                new_g = (g & ~1) | int(binary_message[message_index])
                bit_changes += (new_g != g)
                g = new_g
                message_index += 1
            if message_index < len(binary_message):
                new_b = (b & ~1) | int(binary_message[message_index])
                bit_changes += (new_b != b)
                b = new_b
                message_index += 1
            modified_data.append((r, g, b))

        filename = os.path.basename(image_path)  # Extract the filename
        new_filename = "Stego" + filename # Use only the filename

        modified_img = Image.new("RGB", (width, height))
        modified_img.putdata(modified_data)
        modified_img.save(new_filename, "PNG")
        psnr = calculate_psnr(image_path, new_filename)
        if psnr is not None:
            messagebox.showinfo("Embedding Successful", f"Text successfully encoded into '{new_filename}'\nPSNR: {psnr:.2f} dB\nBits changed: {bit_changes}")
            print(f"Text successfully encoded into '{new_filename}'")
            print(f"PSNR: {psnr:.2f} dB")
            print(f"Bits changed: {bit_changes}")
        else:
            messagebox.showinfo("Embedding Successful", f"Text successfully encoded into '{new_filename}'\nPSNR calculation failed.\nBits changed: {bit_changes}")
            print(f"Text successfully encoded into '{new_filename}'")
            print("PSNR calculation failed.")
            print(f"Bits changed: {bit_changes}")
        print(f"Text successfully encoded into '{new_filename}'")
        print(f"Bits changed: {bit_changes}")
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
        data = list(img.getdata()) # type: ignore
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

        original_image_path = filedialog.askopenfilename(title="Select Original Image for PSNR Calculation", filetypes=[("Image files", "*.png")])
        if original_image_path:
            psnr = calculate_psnr(original_image_path, image_path)
            if psnr is not None:
                messagebox.showinfo("Extraction Successful", f"Extracted Message: '{decoded_text}'\nPSNR: {psnr:.2f} dB")
                print(f"PSNR: {psnr:.2f} dB")
            else:
                messagebox.showinfo("Extraction Successful", f"Extracted Message: '{decoded_text}'\nPSNR calculation failed.")
        else:
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
            left_square.image = photo # type: ignore
            root.image_path = filepath  # type: ignore # Store the image path

    def get_message():
        message = simpledialog.askstring("Embed Message", "Enter the message to embed:")
        if message:
            root.message_to_embed = message # type: ignore

    def embed_interactive():
        if hasattr(root, 'image_path') and hasattr(root, 'message_to_embed'):
            embed_text_on_image(root.image_path, root.message_to_embed) # type: ignore
        else:
            messagebox.showerror("Error", "Please select an image and enter a message.")

    root = tk.Tk()
    root.title("Interactive Embedding Tool (LSB)")
    root.configure(bg="gray")
    root.image_path = None # type: ignore
    root.message_to_embed = None # type: ignore

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
            left_square.image = photo # type: ignore
            root.image_path = filepath # type: ignore

    def extract_interactive():
        if hasattr(root, 'image_path'):
            extract_text_from_image(root.image_path) # type: ignore
        else:
            messagebox.showerror("Error", "Please select an image.")

    root = tk.Tk()
    root.title("Interactive Extraction Tool (LSB)")
    root.configure(bg="gray")
    root.image_path = None # type: ignore

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
            if len(sys.argv) >= 5 and sys.argv[2].lower() == "-i":
                image_file = sys.argv[3]
                if sys.argv[4].lower() == "-m":
                    message_to_embed = sys.argv[5].strip('"')
                    embed_text_on_image(image_file, message_to_embed)
                elif sys.argv[4].lower() == "-f":
                    file_path = sys.argv[5]
                    try:
                        with open(file_path, 'r') as file:
                            message_to_embed = file.read()
                        embed_text_on_image(image_file, message_to_embed)
                    except FileNotFoundError:
                        print(f"Error: File '{file_path}' not found.")
                    except Exception as e:
                        print(f"Error reading file: {e}")
                else:
                    print("Usage for embedding: python lsb.py -e -i <image.png> -m \"your message\" or -f <file.txt>")
            else:
                print("Usage for embedding: python lsb.py -e -i <image.png> -m \"your message\" or -f <file.txt>")
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
