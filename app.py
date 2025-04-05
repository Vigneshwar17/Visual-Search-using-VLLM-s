from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import numpy as np
from PIL import Image
import io
import base64
import torch
from clip_utils import get_clip_model, encode_image, encode_text
from db_utils import get_db_connection, search_similar_images, get_image_count
from external_search import search_similar_images_by_text, search_similar_images_by_image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize CLIP model
model, preprocess, device = get_clip_model()

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.json
        query = data.get('query')
        search_type = data.get('type')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        results = []
        
        # First try database search if available
        try:
            conn = get_db_connection()
            if conn:
                if search_type == 'text':
                    # Text-based search
                    logger.info(f"Processing text search in database: {query}")
                    text_embedding = encode_text(model, query, device)
                    results = search_similar_images(conn, text_embedding)
                    
                elif search_type == 'image':
                    # Image-based search
                    logger.info("Processing image search in database")
                    # Handle base64 encoded image
                    if query.startswith('data:image'):
                        image_data = query.split(',')[1]
                        image_bytes = base64.b64decode(image_data)
                        image = Image.open(io.BytesIO(image_bytes))
                        image_embedding = encode_image(model, preprocess, image, device)
                        results = search_similar_images(conn, image_embedding)
                
                conn.close()
        except Exception as e:
            logger.error(f"Database search error: {str(e)}")
            results = []
        
        # If no results from database, use Pexels API
        if not results:
            logger.info(f"No database results, using Pexels API for: {query}")
            
            if search_type == 'text':
                # Text-based search with Pexels
                results = search_similar_images_by_text(query)
                
            elif search_type == 'image':
                # Image-based search (using text extraction as fallback)
                if query.startswith('data:image'):
                    # For image search, we'll use a simplified approach
                    results = search_similar_images_by_image(query)
        
        return jsonify({"results": results})
        
    except Exception as e:
        logger.error(f"Error processing search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/fetch-healthcare-images', methods=['POST'])
def fetch_images_api():
    try:
        data = request.json
        query = data.get('query', 'healthcare medical')
        num_images = data.get('num_images', 10)
        
        # Use Pexels API to fetch images
        results = search_similar_images_by_text(query, num_images)
        
        return jsonify({
            "success": True,
            "message": f"Fetched {len(results)} healthcare images from Pexels",
            "images": results
        })
        
    except Exception as e:
        logger.error(f"Error fetching healthcare images: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    try:
        # Check database connection
        conn = get_db_connection()
        db_status = "connected" if conn else "disconnected"
        
        # Get image count if connected
        image_count = get_image_count(conn) if conn else 0
        
        # Close connection if open
        if conn:
            conn.close()
        
        return jsonify({
            "status": "ok",
            "message": "Server is running",
            "database": db_status,
            "model": "loaded",
            "images": image_count,
            "pexels_api": "enabled"
        })
        
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)