from PIL import Image
import numpy as np
import argparse

def calculate_psnr(original_image_path, stego_image_path):
    """Calculates the PSNR between the original image and the stego image."""
    try:
        original = Image.open(original_image_path).convert("RGB")
        stego = Image.open(stego_image_path).convert("RGB")

        original_data = np.array(original)
        stego_data = np.array(stego)

        if original_data.shape != stego_data.shape:
            raise ValueError("Images must have the same dimensions.")

        mse = np.mean((original_data - stego_data) ** 2)
        if mse == 0:
            return float('inf')  # Perfect match

        max_pixel_value = 255.0
        psnr = 20 * np.log10(max_pixel_value / np.sqrt(mse))
        return psnr

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate PSNR between two images.")
    parser.add_argument("original_image_path", type=str, help="Path to the original image.")
    parser.add_argument("stego_image_path", type=str, help="Path to the stego image.")
    args = parser.parse_args()

    psnr_value = calculate_psnr(args.original_image_path, args.stego_image_path)
    if psnr_value is not None:
        print(f"PSNR: {psnr_value} dB")
