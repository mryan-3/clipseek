import os
import uuid
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from services.video_service import VideoService
from services.embedding_service import EmbeddingService
from services.vectordb_service import VectorDBService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ClipSeek API")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
DATA_DIR = "data"
FRAME_DIR = os.path.join(DATA_DIR, "frames")
DB_DIR = os.path.join(DATA_DIR, "db")

# Create directories if they don't exist
os.makedirs(FRAME_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# Initialize Services
video_service = VideoService(FRAME_DIR)
embedding_service = EmbeddingService() # This loads the CLIP model
vectordb_service = VectorDBService(DB_DIR)

# Mount static files for frame previews
app.mount("/frames", StaticFiles(directory=FRAME_DIR), name="frames")

# Processing status and metadata store (in-memory for prototype)
videos_db = {}

class VideoLinkRequest(BaseModel):
    file_path: str

async def background_process_video(video_id: str, video_path: str):
    """
    Background task to extract frames, embed them, and store in vector DB.
    """
    try:
        videos_db[video_id]["status"] = "extracting_frames"
        frames = video_service.extract_frames(video_id, video_path)
        
        videos_db[video_id]["status"] = "generating_embeddings"
        embeddings = []
        for frame in frames:
            emb = embedding_service.embed_image(frame["path"])
            embeddings.append(emb)
            
        videos_db[video_id]["status"] = "storing_vectors"
        vectordb_service.add_frames(video_id, frames, embeddings)
        
        videos_db[video_id]["status"] = "completed"
        logger.info(f"Successfully processed video {video_id}")
        
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")
        videos_db[video_id]["status"] = f"error: {str(e)}"

@app.post("/link")
async def link_video(request: VideoLinkRequest):
    file_path = request.file_path
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found at the provided path")
    
    if not file_path.lower().endswith((".mp4", ".mov", ".mkv")):
        raise HTTPException(status_code=400, detail="Unsupported video format")
    
    video_id = str(uuid.uuid4())
    videos_db[video_id] = {
        "id": video_id,
        "path": file_path,
        "filename": os.path.basename(file_path),
        "status": "linked"
    }
    
    return {"video_id": video_id, "filename": os.path.basename(file_path)}

@app.post("/process/{video_id}")
async def process_video(video_id: str, background_tasks: BackgroundTasks):
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video ID not found")
    
    video_path = videos_db[video_id]["path"]
    background_tasks.add_task(background_process_video, video_id, video_path)
    
    return {"status": "processing initiated", "video_id": video_id}

@app.get("/status/{video_id}")
async def get_status(video_id: str):
    video = videos_db.get(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video ID not found")
    return {"video_id": video_id, "status": video["status"]}

@app.get("/videos")
async def list_videos():
    return {"videos": list(videos_db.values())}

@app.get("/search")
async def search(q: str, limit: int = 10):
    if not q:
        raise HTTPException(status_code=400, detail="Query string 'q' is required")
    
    try:
        # 1. Embed the text query
        query_embedding = embedding_service.embed_text(q)
        
        # 2. Search ChromaDB
        results = vectordb_service.search(query_embedding, n_results=limit)
        
        # 3. Augment results with local frame URLs
        for res in results:
            video_id = res["metadata"]["video_id"]
            filename = res["metadata"]["filename"]
            # Construct URL for the frontend to fetch the image
            res["frame_url"] = f"/frames/{video_id}/{filename}"
            
        return {"query": q, "results": results}
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "ClipSeek API is running locally (Path Linking Mode)"}
