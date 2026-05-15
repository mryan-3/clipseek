import os
import torch
import open_clip
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "ViT-B-32", pretrained: str = "laion2b_s34b_b79k"):
        """
        Initializes OpenCLIP using the locally cached LAION model.
        Bypasses CUDA issues by using the modern Safetensors format on CPU.
        """
        self.device = "cpu"
        # Point to the existing HuggingFace hub cache
        os.environ["HF_HOME"] = "/home/ryanm/.cache/huggingface"
        
        logger.info(f"Loading OpenCLIP {model_name} ({pretrained}) on {self.device}...")
        
        try:
            # OpenCLIP handles loading from HF_HOME/hub automatically
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                model_name, 
                pretrained=pretrained, 
                device=self.device
            )
            self.tokenizer = open_clip.get_tokenizer(model_name)
            self.model.eval()
            logger.info("OpenCLIP model loaded successfully from cache.")
        except Exception as e:
            logger.error(f"Failed to load OpenCLIP model: {e}")
            raise

    def embed_image(self, image_path: str):
        """Generates a semantic embedding for a single image."""
        image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy().flatten().tolist()

    def embed_text(self, text: str):
        """Generates a semantic embedding for a text query."""
        text_input = self.tokenizer([text]).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_input)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy().flatten().tolist()
