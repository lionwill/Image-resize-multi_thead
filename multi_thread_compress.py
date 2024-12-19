# Multi-threaded compression suitable for multi-core systems and machines with fast SSDs. It is recommended to place the compressed path on an SSD.
#lionwill 20241219
from PIL import Image
import os
import time
import concurrent.futures

# Define global variables
IMAGE_DIR = 'xxximgage folder'  #image folder for resize
RESIZED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resized')  #resized image folder name

# Initialize counters
total_images = 0
compressed_images = 0
unchanged_images = 0

def resize_image(image_path, target_width=768, target_height=768):
    """
    Resize images proportionally based on width and height.
    
    :param image_path: Path of the image to be resized
    :param target_width: Target width, default is 768
    :param target_height: Target height, default is 768
    """
    global compressed_images, unchanged_images
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Check if the image dimensions need resizing
        if width > 512 or height > 768:
            if width > height:
                # Width is greater than height, resize proportionally by width
                ratio = target_width / width
                new_height = int(height * ratio)
                resized_img = img.resize((target_width, new_height), resample=Image.Resampling.LANCZOS)
            else:
                # Height is greater than width, resize proportionally by height
                ratio = target_height / height
                new_width = int(width * ratio)
                resized_img = img.resize((new_width, target_height), resample=Image.Resampling.LANCZOS)
            
            # Save the resized image
            base_name, ext = os.path.splitext(os.path.basename(image_path))
            new_image_path = get_unique_filename(base_name, ext)
            resized_img.save(new_image_path)
            print(f"Resized and saved image: {new_image_path}")
            compressed_images += 1
        else:
            print(f"Image size is appropriate, no resizing needed: {image_path}")
            unchanged_images += 1
        
        global total_images
        total_images += 1
    except Exception as e:
        print(f"Error occurred while processing image {image_path}: {e}")

def get_unique_filename(base_name, ext):
    """
    Generate a unique filename.
    
    :param base_name: Base name of the file
    :param ext: File extension
    :return: Unique file path
    """
    index = 1
    while True:
        filename = f"{base_name}_{index}{ext}"
        new_image_path = os.path.join(RESIZED_DIR, filename)
        if not os.path.exists(new_image_path):
            return new_image_path
        index += 1

def collect_image_paths(directory):
    """
    Collect all image paths within a specified directory.
    
    :param directory: Directory path
    :return: List of image paths
    """
    image_paths = []
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    image_paths.append(os.path.join(root, file))
    except Exception as e:
        print(f"Error occurred while traversing directory {directory}: {e}")
    return image_paths

def compress_images(directory):
    """
    Compress all images in a specified directory.
    
    :param directory: Directory containing images
    """
    # Create the directory for compressed images
    if not os.path.exists(RESIZED_DIR):
        os.makedirs(RESIZED_DIR)
    
    # Collect all image paths
    image_paths = collect_image_paths(directory)
    
    # Use multi-threading to process images
    start_time = time.time()
    max_workers = os.cpu_count()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(resize_image, image_paths))
    end_time = time.time()
    
    # Calculate processing time
    processing_time = end_time - start_time
    print(f"Processing time: {processing_time:.2f} seconds")

def summarize_results():
    """ Output the results of the processing. """
    print(f"Processed a total of {total_images} images")
    print(f"Compressed a total of {compressed_images} images")
    print(f"{unchanged_images} images did not require compression")

if __name__ == "__main__":
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Join the image folder path
    IMAGE_DIR = os.path.join(current_directory, IMAGE_DIR)
    
    if not os.path.exists(IMAGE_DIR):
        print(f"The directory '{IMAGE_DIR}' does not exist. Please check the path.")
    else:
        compress_images(IMAGE_DIR)
        summarize_results()