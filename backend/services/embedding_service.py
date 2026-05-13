import torch
import open_clip
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "ViT-B-32", pretrained: str = "laion2b_s34b_b79k"):
        """
        Initializes the CLIP model and preprocessing pipeline.
        Defaulting to ViT-B-32 which is balanced for CPU performance.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading CLIP model {model_name} on {self.device}...")
        
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, 
            pretrained=pretrained, 
            device=self.device
        )
        self.tokenizer = open_clip.get_tokenizer(model_name)
        logger.info("CLIP model loaded successfully.")

    def embed_image(self, image_path: str):
        """Generates an embedding for a single image."""
        image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)
        with torch.no_grad(), torch.cuda.amp.autocast(enabled=(self.device == "cuda")):
            image_features = self.model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy().flatten().tolist()

    def embed_text(self, text: str):
        """Generates an embedding for a text query."""
        text_input = self.tokenizer([text]).to(self.device)
        with torch.no_grad(), torch.cuda.amp.autocast(enabled=(self.device == "cuda")):
            text_features = self.model.encode_text(text_input)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy().flatten().tolist()
