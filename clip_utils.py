import torch
import clip
import numpy as np
from PIL import Image

def get_clip_model(device=None):
    """Load the CLIP model and return model and preprocessing function"""
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"Loading CLIP model on {device}...")
    model, preprocess = clip.load("ViT-B/32", device=device)
    model.eval()  # Set to evaluation mode
    print("CLIP model loaded successfully!")
    return model, preprocess, device

def encode_image(model, preprocess, image, device):
    """Encode an image using CLIP model"""
    image_input = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        # Normalize the features
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    return image_features.cpu().numpy().flatten()

def encode_text(model, text, device):
    """Encode text using CLIP model"""
    text_input = clip.tokenize([text]).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_input)
        # Normalize the features
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    return text_features.cpu().numpy().flatten()