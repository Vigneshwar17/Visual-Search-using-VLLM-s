import os
import psycopg2
import psycopg2.extras
import numpy as np
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    try:
        # Get connection parameters from environment variables
        host = os.getenv("DB_HOST", "localhost")
        database = os.getenv("DB_NAME", "visual")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD")
        port = os.getenv("DB_PORT", "5432")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        conn.autocommit = True
        
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_vector_db():
    """Initialize the vector database"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        # Create a cursor
        cur = conn.cursor()
        
        # Check if pgvector extension is installed
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if cur.fetchone() is None:
            print("Installing pgvector extension...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create table for image vectors if it doesn't exist
        cur.execute("""
        CREATE TABLE IF NOT EXISTS image_vectors (
            id UUID PRIMARY KEY,
            embedding vector(512),
            image_path TEXT,
            description TEXT,
            category TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create index for similarity search if it doesn't exist
        cur.execute("""
        CREATE INDEX IF NOT EXISTS image_vectors_embedding_idx 
        ON image_vectors 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """)
        
        print("Vector database initialized successfully!")
        cur.close()
        
        return conn
    except Exception as e:
        print(f"Error initializing vector database: {e}")
        if conn:
            conn.close()
        return None

def add_image_to_db(conn, embedding, image_path, description="", category="healthcare"):
    """Add an image embedding to the vector database"""
    if not conn:
        return None
    
    try:
        # Generate a unique ID for the image
        image_id = str(uuid.uuid4())
        
        # Add the embedding to the database
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO image_vectors (id, embedding, image_path, description, category) VALUES (%s, %s, %s, %s, %s)",
            (image_id, embedding.tolist(), image_path, description, category)
        )
        cur.close()
        
        return image_id
    except Exception as e:
        print(f"Error adding image to database: {e}")
        return None

def search_similar_images(conn, query_embedding, limit=6, threshold=0.6, category=None):
    """Search for similar images in the vector database"""
    if not conn:
        return []
    
    try:
        # Convert numpy array to list for PostgreSQL compatibility
        embedding_list = query_embedding.tolist()
        
        # Query the database for similar images
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        if category:
            cur.execute(
                """
                SELECT id, image_path, description, category, 
                       1 - (embedding <=> %s::vector) AS similarity
                FROM image_vectors
                WHERE 1 - (embedding <=> %s::vector) > %s AND category = %s
                ORDER BY similarity DESC
                LIMIT %s;
                """,
                (embedding_list, embedding_list, threshold, category, limit)
            )
        else:
            cur.execute(
                """
                SELECT id, image_path, description, category, 
                       1 - (embedding <=> %s::vector) AS similarity
                FROM image_vectors
                WHERE 1 - (embedding <=> %s::vector) > %s
                ORDER BY similarity DESC
                LIMIT %s;
                """,
                (embedding_list, embedding_list, threshold, limit)
            )
        
        # Format the results
        results = []
        for row in cur.fetchall():
            results.append({
                "id": row["id"],
                "image_url": row["image_path"],
                "description": row["description"],
                "category": row["category"],
                "similarity": float(row["similarity"])
            })
        
        cur.close()
        return results
    except Exception as e:
        print(f"Error searching for similar images: {e}")
        return []

def get_image_count(conn, category=None):
    """Get the count of images in the database"""
    if not conn:
        return 0
    
    try:
        cur = conn.cursor()
        
        if category:
            cur.execute("SELECT COUNT(*) FROM image_vectors WHERE category = %s", (category,))
        else:
            cur.execute("SELECT COUNT(*) FROM image_vectors")
            
        count = cur.fetchone()[0]
        cur.close()
        
        return count
    except Exception as e:
        print(f"Error getting image count: {e}")
        return 0