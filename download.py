import time
import cv2
import pandas as pd
import requests
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

def crop_to_product_area(image_path):
    """Crop image to remove top portion containing human head and focus on product/clothing"""
    try:
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"Warning: Could not load image {image_path}")
            return False
        
        height, width = img.shape[:2]
        crop_start = int(height * 0.3)
        cropped_img = img[crop_start:, :]
        
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            if face_cascade.empty():
                print("Warning: Could not load face cascade classifier")
            else:
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    lowest_face_bottom = 0
                    for (x, y, w, h) in faces:
                        face_bottom = y + h
                        if face_bottom > lowest_face_bottom:
                            lowest_face_bottom = face_bottom
                    
                    crop_start = min(lowest_face_bottom + 50, int(height * 0.4))
                    cropped_img = img[crop_start:, :]
                    print(f"Smart crop based on face detection: {image_path}")
                else:
                    print(f"No face detected, using default crop: {image_path}")
                
        except Exception as face_error:
            print(f"Face detection failed, using default crop: {face_error}")
        
        # Ensure we don't crop too much
        if cropped_img.shape[0] < height * 0.6:
            crop_start = int(height * 0.4)
            cropped_img = img[crop_start:, :]
        
        # Save the cropped image
        success = cv2.imwrite(str(image_path), cropped_img)
        if success:
            print(f"Cropped image: {image_path} (Original: {height}x{width}, New: {cropped_img.shape[0]}x{cropped_img.shape[1]})")
        else:
            print(f"Failed to save cropped image: {image_path}")
        return success
        
    except Exception as e:
        print(f"Error cropping image {image_path}: {e}")
        return False

def download_images():
    """Download images from CSV file"""
    csv_path = './csv/zando_images.csv'
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Please ensure your CSV file is mounted correctly in the container")
        return
    
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded CSV with {len(df)} rows")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Create base directory for images
    base_dir = Path('./images')
    base_dir.mkdir(exist_ok=True)
    
    # Track download timing for rate limiting
    download_count = 0
    start_time = time.time()
    
    for index, row in df.iterrows():
        try:
            sku = str(row['sku'])
            image_url = row['image']
            image_name = row['names']
            
            # Create SKU folder
            sku_folder = base_dir / sku
            sku_folder.mkdir(exist_ok=True)
            
            # Fix URL construction
            if image_url.startswith('http'):
                full_url = image_url
            else:
                clean_path = image_url.lstrip('/')
                full_url = f"https://zandokh.com/image/{clean_path}"
            
            # Get file extension from URL
            parsed_url = urlparse(full_url)
            file_ext = os.path.splitext(parsed_url.path)[1]
            if not file_ext:
                file_ext = '.jpg'
            
            # Create safe filename
            safe_name = "".join(c for c in str(image_name) if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_name:
                safe_name = f"image_{index}"
            
            file_path = sku_folder / f"{safe_name}{file_ext}"
            
            # Skip if file already exists
            if file_path.exists():
                print(f"Skipping {file_path} - already exists")
                continue
            
            print(f"Downloading from: {full_url}")
            
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(full_url, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"Warning: {full_url} doesn't appear to be an image")
                continue
            
            # Save image
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {file_path}")
            
            # Crop the image
            crop_to_product_area(file_path)
            
            download_count += 1
            
            # Rate limiting
            if download_count % 3 == 0:
                elapsed = time.time() - start_time
                if elapsed < 1:
                    time.sleep(1 - elapsed)
                start_time = time.time()
                
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            continue
        
        # Add delay between downloads
        time.sleep(0.3)
    
    print(f"Download complete. Processed {download_count} images.")

if __name__ == "__main__":
    print("Starting image download and processing...")
    download_images()
    print("Process completed.")