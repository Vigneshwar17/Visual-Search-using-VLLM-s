import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
PEXELS_API_KEY = "FznlLOW4fKsNvLc6ZJFnmf6au4unyMAyFTIuXO0Op7SvDoI04WX0zHkM"
PIXABAY_API_KEY = "49642350-1d71ee313dfb1b26c0a8c09bf"

def search_pexels_images(query, limit=6, category="healthcare"):
    """Search for images on Pexels API"""
    # Add healthcare to the query if not already present
    if "healthcare" not in query.lower() and "medical" not in query.lower():
        search_query = f"{query} medical healthcare"
    else:
        search_query = query
    
    url = f"https://api.pexels.com/v1/search?query={search_query}&per_page={limit}"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    try:
        print(f"Searching Pexels for: {search_query}")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error from Pexels API: {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        
        results = []
        for item in data.get('photos', []):
            results.append({
                "id": str(item['id']),
                "url": item['src']['large'],
                "title": item.get('alt', query),
                # "description": item.get('alt', query),
                "category": category,
                "similarity": 0.9,  # Mock similarity score
                # "source": "pexels"
            })
        
        print(f"Found {len(results)} images from Pexels")
        return results
    except Exception as e:
        print(f"Error searching Pexels: {e}")
        return []

def search_pixabay_images(query, limit=6, category="healthcare"):
    """Search for images on Pixabay API"""
    # Add healthcare to the query if not already present
    if "healthcare" not in query.lower() and "medical" not in query.lower():
        search_query = f"{query} medical healthcare"
    else:
        search_query = query
    
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={search_query}&per_page={limit}&image_type=photo&category=science"
    
    try:
        print(f"Searching Pixabay for: {search_query}")
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error from Pixabay API: {response.status_code} - {response.text}")
            return []
            
        data = response.json()
        
        results = []
        for item in data.get('hits', []):
            results.append({
                "id": str(item['id']),
                "url": item['largeImageURL'],
                "title": item.get('tags', '').split(',')[0],
                # "description": item.get('tags', ''),
                "category": category,
                "similarity": 0.9,  # Mock similarity score
                # "source": "pixabay"
            })
        
        print(f"Found {len(results)} images from Pixabay")
        return results
    except Exception as e:
        print(f"Error searching Pixabay: {e}")
        return []

def search_similar_images_by_text(query, limit=6):
    """Search for images similar to text query using both Pexels and Pixabay"""
    # Get results from both APIs
    pexels_results = search_pexels_images(query, limit // 2)
    pixabay_results = search_pixabay_images(query, limit // 2)
    
    # Combine and shuffle results
    import random
    combined_results = pexels_results + pixabay_results
    random.shuffle(combined_results)
    
    return combined_results[:limit]

def search_similar_images_by_image(image_url, limit=6):
    """
    Search for images similar to an image
    Note: Since direct image search isn't supported, we use medical keywords
    """
    medical_keywords = [
        "xray","mri", "ct scan", "ultrasound", "medical scan",
        "healthcare", "medical imaging", "radiology"
    ]
    
    # Use a random medical keyword as fallback
    import random
    query = random.choice(medical_keywords)
    
    return search_similar_images_by_text(query, limit)