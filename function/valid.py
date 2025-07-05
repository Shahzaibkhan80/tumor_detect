# import cv2
# import numpy as np


# def is_valid_biopsy(image_path):
#     """
#     Validate whether the input image is likely to be a biopsy image.
#     """
#     try:
#         img = cv2.imread(image_path)
#         if img is None:
            
#             return False
#         h, w, _ = img.shape
#         if h < 100 or w < 100:
           
#             return False
#         aspect_ratio = w / h
#         if aspect_ratio < 0.8 or aspect_ratio > 1.2:
          
#             return False
#         hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#         color_variance = np.var(hsv_img[:, :, 1])
#         if color_variance < 50:
        
#             return False
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
#         if laplacian_var < 100:
            
#             return False
#         sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
#         if sharpness < 100:
           
#             return False
#         hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
#         if np.sum(hist[hist > 0]) < 1000:
#             return False
#         edges = cv2.Canny(gray, 100, 200)
#         if np.sum(edges) < 5000:
#             return False
#         return True
#     except Exception as e:
#         print(f"Validation error (biopsy): {e}")
#         return False
    

# def is_valid_xray(image_path):
#     """
#     Validate whether the input image is likely to be an X-ray image.
#     """
#     try:
#         img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#         if img is None:
#             return False
#         h, w = img.shape
#         if h < 100 or w < 100:
#             return False
#         sharpness = cv2.Laplacian(img, cv2.CV_64F).var()
#         if sharpness < 50:
#             return False
#         return True
#     except Exception as e:
#         print(f"Validation error (X-ray): {e}")
#         return False
    

# def validate_xray_image(filepath):
#     """
#     Validates if the uploaded image is likely an X-ray.
#     :param filepath: Path to the uploaded image file.
#     :return: True if it passes validation, False otherwise.
#     """
#     try:
#         # Read the image using OpenCV
#         image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)  # X-ray images are usually grayscale
#         if image is None:
#             return False  # Invalid image

#         # Check the dimensions and properties
#         height, width = image.shape
#         if height < 100 or width < 100:  # Ensure image isn't too small
#             return False

#         # Optional: Analyze pixel intensity (X-rays have specific intensity distributions)
#         mean_intensity = np.mean(image)
#         if mean_intensity < 50 or mean_intensity > 200:  # X-rays tend to have medium intensity
#             return False

#         return True
#     except Exception as e:
#         print(f"Error validating X-ray image: {e}")
#         return False


import cv2
import numpy as np

def is_valid_biopsy(image_path):
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            print("Invalid image or path!")
            return False  # Invalid image
        
        # Check image dimensions (avoid too small images)
        h, w, _ = img.shape
        if h < 100 or w < 100:
            print(f"Image too small! Dimensions: {h}x{w}")
            return False  # Too small image
        
        # Check aspect ratio
        aspect_ratio = w / h
        if aspect_ratio < 0.8 or aspect_ratio > 1.2:
            print(f"Aspect ratio out of range: {aspect_ratio}")
            return False  # Aspect ratio out of expected range
        
        # Convert to HSV for color analysis
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        color_variance = np.var(hsv_img[:, :, 1])  # Saturation variance
        if color_variance < 50:
            print("Too little color variation in image.")
            return False  # Too little color variation
        
        # Convert to grayscale for sharpness and edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Sharpness check using Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 100:
            print("Image too blurry!")
            return False  # Too blurry image
        
        # Edge detection
        edges = cv2.Canny(gray, 100, 200)
        if np.sum(edges) < 5000:
            print("Not enough edges detected!")
            return False  # Not enough edges detected
        
        print("Image passed validation.")
        return True  # Biopsy image validated
    
    except Exception as e:
        print(f"Validation error (biopsy): {e}")
        return False  # Return false if any error occurs


    

def is_valid_xray(image_path, debug=False):
    """
    Validate whether the input image is likely to be an X-ray image.
    :param image_path: File path of the image
    :param debug: Whether to print debug info
    :return: True if valid, else False
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False

        h, w = img.shape
        if debug: print(f"📏 Image dimensions: {h}x{w}")
        if h < 100 or w < 100:
            return False

        sharpness = cv2.Laplacian(img, cv2.CV_64F).var()
        if sharpness < 50:
            return False

        mean_intensity = np.mean(img)
        if mean_intensity < 50 or mean_intensity > 200:
            return False

        return True
    except Exception as e:
        return False
    

# def validate_xray_image(filepath):
#     """
#     Validates if the uploaded image is likely an X-ray.
#     :param filepath: Path to the uploaded image file.
#     :return: True if it passes validation, False otherwise.
#     """
#     try:
#         # Read the image in grayscale
#         image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
#         if image is None:
#             return False  # Invalid image

#         # Check dimensions
#         height, width = image.shape
#         if height < 100 or width < 100:
#             return False  # Image too small

#         # Check for appropriate sharpness
#         sharpness = cv2.Laplacian(image, cv2.CV_64F).var()
#         if sharpness < 50:
#             return False  # Image too blurry

#         # Optional: Check intensity range (X-ray images tend to have a certain intensity range)
#         mean_intensity = np.mean(image)
#         if mean_intensity < 50 or mean_intensity > 200:
#             return False  # Intensity out of expected range

#         return True  # Image passed all validation checks
#     except Exception as e:
#         print(f"Error validating X-ray image: {e}")
#         return False  # Return false if any error occurs
def validate_xray_image(filepath):
    """
    Validates if the uploaded image is likely an X-ray.
    :param filepath: Path to the uploaded image file.
    :return: True if it passes validation, False otherwise.
    """
    try:
        print(f"Checking file: {filepath}")  # ✅ Debugging Step 1

        # Read the image in grayscale
        image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print("❌ Error: Unable to read the image. It may not be a valid image file.")
            return False  # Invalid image
        
        print("✅ Image successfully read in grayscale.")

        # Check dimensions
        height, width = image.shape
        print(f"📏 Image dimensions: {height}x{width}")  # ✅ Debugging Step 2
        if height < 100 or width < 100:
            print("❌ Error: Image too small.")
            return False  # Image too small

        # Check for appropriate sharpness
        sharpness = cv2.Laplacian(image, cv2.CV_64F).var()
        print(f"📌 Sharpness Level: {sharpness}")  # ✅ Debugging Step 3
        if sharpness < 50:
            print("❌ Error: Image is too blurry.")
            return False  # Image too blurry

        # Optional: Check intensity range (X-ray images tend to have a certain intensity range)
        mean_intensity = np.mean(image)
        print(f"💡 Mean Intensity: {mean_intensity}")  # ✅ Debugging Step 4
        if mean_intensity < 50 or mean_intensity > 200:
            print("❌ Error: Intensity out of expected X-ray range.")
            return False  # Intensity out of expected range

        print("✅ Image passed all validation checks.")
        return True  # Image passed all validation checks

    except Exception as e:
        print(f"⚠️ Error validating X-ray image: {e}")
        return False  # Return false if any error occurs