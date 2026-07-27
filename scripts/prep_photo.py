import sys
import os
import cv2
import numpy as np
from PIL import Image

def prep_photo(input_path="source-photo.jpg", output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} does not exist.")
        sys.exit(1)

    print(f"Processing photo: {input_path}...")
    img_pil = Image.open(input_path).convert("RGB")
    
    # Attempt background removal with rembg
    has_alpha = False
    try:
        from rembg import remove
        print("Removing background with rembg...")
        img_no_bg = remove(img_pil)
        img_np = np.array(img_no_bg)
        if img_np.shape[2] == 4:
            has_alpha = True
            alpha = img_np[:, :, 3]
            rgb = img_np[:, :, :3]
    except Exception as e:
        print(f"rembg notice ({e}). Falling back to OpenCV image processing...")

    if not has_alpha:
        rgb = np.array(img_pil)
        alpha = np.full((rgb.shape[0], rgb.shape[1]), 255, dtype=np.uint8)

    # Convert to grayscale
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # Composite onto pure white background using alpha mask
    alpha_float = alpha.astype(float) / 255.0
    composite = (enhanced_gray * alpha_float + 255 * (1.0 - alpha_float)).astype(np.uint8)

    output_pil = Image.fromarray(composite)
    output_pil.save(output_path)
    print(f"Prepped photo saved to {output_path}")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    prep_photo(inp)
