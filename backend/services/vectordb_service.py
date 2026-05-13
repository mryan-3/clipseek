import chromadb
from chromadb.config import Settings
import os
import logging

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self, db_path: str):
        """Initializes the ChromaDB client and collection."""
        self.client = chromadb.PersistentClient(path=db_path)
        # Collection for all video frames
        self.collection = self.client.get_or_create_collection(
            name="video_frames",
            metadata={"hnsw:space": "cosine"} # Use cosine similarity for CLIP embeddings
        )
        logger.info(f"ChromaDB initialized at {db_path}")

    def add_frames(self, video_id: str, frames: list, embeddings: list):
        """Adds a batch of frame embeddings to the collection."""
        ids = [f"{video_id}_{f['timestamp']}" for f in frames]
        metadatas = [
            {
                "video_id": video_id, 
                "timestamp": f["timestamp"], 
                "frame_path": f["path"],
                "filename": f["filename"]
            } 
            for f in frames
        ]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"Added {len(frames)} embeddings to ChromaDB for video {video_id}")

    def search(self, query_embedding: list, n_results: int = 5):
        """Searches for the most similar frames in the collection."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results for the API
        formatted_results = []
        if results["ids"]:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "score": 1 - results["distances"][0][i], # Convert distance to similarity score
                    "metadata": results["metadatas"][0][i]
                })
        
        return formatted_results
