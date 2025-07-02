from faiss import read_index
from PIL import Image

import clip
import json
import torch


class App:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)  # Keep preprocess
        self.model.eval()

        self.index = read_index("static/index.faiss")
        with open("static/image_paths.json") as f:
            self.image_paths = json.load(f)

    def search_by_text(self, search_text, results=1):
        text_tokens = clip.tokenize([search_text]).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens).float()
        text_features /= text_features.norm(dim=-1, keepdim=True)
        text_features = text_features.cpu().numpy()

        _, indices = self.index.search(text_features, results)
        return [self.image_paths[indices[0][i]] for i in range(results)]

    def search_by_image(self, image_path, results=5):
        # Load and preprocess the uploaded image
        image = Image.open(image_path).convert("RGB")
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        
        # Get image features
        with torch.no_grad():
            image_features = self.model.encode_image(image_input).float()
        image_features /= image_features.norm(dim=-1, keepdim=True)
        image_features = image_features.cpu().numpy()

        # Search for similar images
        _, indices = self.index.search(image_features, results)
        return [self.image_paths[indices[0][i]] for i in range(results)]

    def search(self, search_text, results=1):
        return self.search_by_text(search_text, results)