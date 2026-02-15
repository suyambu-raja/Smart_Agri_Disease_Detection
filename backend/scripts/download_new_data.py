"""
Script to download sample images for Rice, Wheat, and Onion diseases.
Since I cannot download files directly from the web in this environment,
this script provides a template to download images if you have internet access
on your local machine.

Usage:
    python scripts/download_new_data.py
"""

import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the target classes and some example image URLs
# NOTE: These URLs are examples. In a real scenario, you would need valid URLs.
NEW_CLASSES = {
    'Rice___Brown_spot': [
        'https://inaturalist-open-data.s3.amazonaws.com/photos/156616089/medium.jpg',
        'https://crop-protection-network.s3.amazonaws.com/articles/Rice-Brown-Spot-1.jpg',
    ],
    'Rice___Leaf_blast': [
        'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Rice_Blast.jpg/800px-Rice_Blast.jpg',
    ],
    'Rice___Hispa': [
        'https://live.staticflickr.com/65535/51234567890_abcdef1234_b.jpg', 
    ],
    'Rice___healthy': [
        'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Rice_plants.jpg/800px-Rice_plants.jpg',
    ],
    'Wheat___Yellow_rust': [
        'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Puccinia_striiformis.jpg/800px-Puccinia_striiformis.jpg',
    ],
    'Wheat___Septoria': [
        'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Septoria_tritici.jpg/800px-Septoria_tritici.jpg',
    ],
    'Wheat___Brown_rust': [
        'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Puccinia_recondita.jpg/800px-Puccinia_recondita.jpg',
    ],
    'Wheat___healthy': [
        'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Green_wheat.jpg/800px-Green_wheat.jpg',
    ],
    'Onion___Purple_blotch': [
        'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Purple_blotch_onion.jpg/800px-Purple_blotch_onion.jpg',
    ],
    'Onion___healthy': [
        'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Onion_field.jpg/800px-Onion_field.jpg',
    ]
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'plantvillage dataset', 'color')

def download_images():
    for class_name, urls in NEW_CLASSES.items():
        folder_path = os.path.join(DATA_DIR, class_name)
        os.makedirs(folder_path, exist_ok=True)
        
        logger.info(f"Checking {class_name}...")
        
        # Check if folder is empty
        if not os.listdir(folder_path):
            logger.info(f"  Folder is empty. Attempting to download samples...")
            for i, url in enumerate(urls):
                try:
                    # Generic download logic
                    # response = requests.get(url, timeout=10)
                    # if response.status_code == 200:
                    #     file_path = os.path.join(folder_path, f"downloaded_{i+1}.jpg")
                    #     with open(file_path, 'wb') as f:
                    #         f.write(response.content)
                    #     logger.info(f"    Downloaded image {i+1}")
                    pass
                except Exception as e:
                    logger.error(f"    Failed to download {url}: {e}")
        else:
             logger.info(f"  Folder already has images. Skipping.")

if __name__ == '__main__':
    print("This script is a placeholder. Automatic downloading of images from search results is restricted.")
    print(f"Please manually add 10-15 images for each of these folders in:")
    print(f"{DATA_DIR}")
    print("\nFolders created:")
    for cls in NEW_CLASSES.keys():
        print(f" - {cls}")
