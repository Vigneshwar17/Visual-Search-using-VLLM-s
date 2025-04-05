import os
import argparse
from PIL import Image
import torch
from tqdm import tqdm
from clip_utils import get_clip_model, encode_image
from db_utils import init_vector_db, add_image_to_db, get_image_count, get_db_connection
from backend.healthcare_images import fetch_healthcare_images

def is_valid_image(image_path):
    """Check if an image file is valid"""
    try:
        with Image.open(image_path) as img:
            img.verify()  # Verify it's a valid image
        return True
    except Exception:
        return False

def index_images(image_dir, category="general"):
    """Index all images in a directory into the vector database"""
    # Initialize CLIP model
    model, preprocess, device = get_clip_model()
    
    # Initialize vector database
    conn = init_vector_db()
    if not conn:
        print("❌ Failed to initialize vector database")
        return
    
    # Get all image files from the directory
    if not os.path.exists(image_dir):
        print(f"❌ Image directory '{image_dir}' not found")
        return
        
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    if not image_files:
        print("❌ No images found in the directory")
        return
    
    print(f"Found {len(image_files)} images to index")
    
    # Process each image
    for filename in tqdm(image_files, desc="Indexing images"):
        try:
            # Load and process the image
            image_path = os.path.join(image_dir, filename)
            image = Image.open(image_path).convert('RGB')
            
            # Generate embedding
            embedding = encode_image(model, preprocess, image, device)
            
            # Generate description from filename
            description = filename.split('.')[0].replace('_', ' ').replace('-', ' ')
            
            # Add to database
            image_id = add_image_to_db(conn, embedding, image_path, description, category)
            
            if not image_id:
                print(f"❌ Failed to add image {filename} to database")
            
        except Exception as e:
            print(f"Error processing image {filename}: {e}")
    
    print(f"✅ Indexed {len(image_files)} images successfully")
    
    # Close the database connection
    conn.close()

def index_healthcare_images(fetch_new=True, num_images=10):
    """Index healthcare images into the vector database"""
    # Initialize CLIP model
    model, preprocess, device = get_clip_model()
    
    # Initialize vector database
    conn = init_vector_db()
    if not conn:
        print("❌ Failed to initialize vector database")
        return
    
    # Check if we already have images
    existing_count = get_image_count(conn, category="healthcare")
    print(f"Found {existing_count} existing healthcare images in the database")
    
    # If we need to fetch new images
    if fetch_new or existing_count == 0:
        image_dir = "healthcare_images"
            
        # Fetch healthcare images if needed
        if not os.path.exists(image_dir) or len(os.listdir(image_dir)) == 0:
            print("Fetching healthcare images...")
            images = fetch_healthcare_images(num_images=num_images, save_dir=image_dir)
            
            # Process each image
            for image_info in images:
                try:
                    # Load and process the image
                    image_path = image_info['path']
                    
                    # Validate the image
                    if not is_valid_image(image_path):
                        print(f"❌ Invalid image file: {image_path}")
                        continue
                    
                    image = Image.open(image_path).convert('RGB')
                    
                    # Generate embedding
                    embedding = encode_image(model, preprocess, image, device)
                    
                    # Add to database
                    image_id = add_image_to_db(conn, embedding, image_path, image_info['description'], category="healthcare")
                    
                    if not image_id:
                        print(f"❌ Failed to add image {image_path} to database")
                    else:
                        print(f"✅ Added image {image_path} to database")
                    
                except Exception as e:
                    print(f"Error processing image {image_info['path']}: {e}")
        else:
            # Index existing images
            index_images(image_dir, category="healthcare")
    
    # Close the database connection
    conn.close()
    print("✅ Healthcare image indexing complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index images for visual search")
    parser.add_argument("--image_dir", type=str, help="Directory containing images to index")
    parser.add_argument("--category", type=str, default="general", help="Category for the images")
    parser.add_argument("--healthcare", action="store_true", help="Index healthcare images")
    parser.add_argument("--fetch", action="store_true", help="Fetch new healthcare images")
    parser.add_argument("--num_images", type=int, default=10, help="Number of healthcare images to fetch")
    args = parser.parse_args()
    
    if args.healthcare:
        index_healthcare_images(args.fetch, args.num_images)
    elif args.image_dir:
        index_images(args.image_dir, args.category)
    else:
        print("Please specify either --image_dir or --healthcare")