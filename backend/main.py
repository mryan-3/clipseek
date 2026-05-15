import os, uuid, logging, mimetypes
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.video_service import VideoService
from services.embedding_service import EmbeddingService
from services.vectordb_service import VectorDBService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ClipSeek API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

FRAME_DIR, DB_DIR = "data/frames", "data/db"
os.makedirs(FRAME_DIR, exist_ok=True); os.makedirs(DB_DIR, exist_ok=True)

video_service = VideoService(FRAME_DIR)
embedding_service = EmbeddingService()
vectordb_service = VectorDBService(DB_DIR)

app.mount("/frames", StaticFiles(directory=FRAME_DIR), name="frames")
videos_db = {}

class VideoLinkRequest(BaseModel): file_path: str

async def background_process_video(v_id: str, path: str):
    try:
        videos_db[v_id]["status"] = "extracting"
        frames = video_service.extract_frames(v_id, path)
        videos_db[v_id]["status"] = "embedding"
        embs = [embedding_service.embed_image(f["path"]) for f in frames]
        vectordb_service.add_frames(v_id, frames, embs)
        videos_db[v_id]["status"] = "completed"
    except Exception as e:
        logger.error(e); videos_db[v_id]["status"] = f"error: {e}"

@app.post("/link")
async def link_video(req: VideoLinkRequest):
    if not os.path.exists(req.file_path): raise HTTPException(404)
    v_id = str(uuid.uuid4())
    videos_db[v_id] = {"id": v_id, "path": req.file_path, "filename": os.path.basename(req.file_path), "status": "linked"}
    return {"video_id": v_id, "filename": videos_db[v_id]["filename"]}

@app.post("/process/{v_id}")
async def process_video(v_id: str, bt: BackgroundTasks):
    if v_id not in videos_db: raise HTTPException(404)
    bt.add_task(background_process_video, v_id, videos_db[v_id]["path"])
    return {"status": "started", "video_id": v_id}

@app.get("/status/{v_id}")
async def get_status(v_id: str):
    if v_id not in videos_db: raise HTTPException(404)
    return {"video_id": v_id, "status": videos_db[v_id]["status"]}

@app.get("/video-stream/{v_id}")
async def stream_video(v_id: str):
    video = videos_db.get(v_id)
    if not video or not os.path.exists(video["path"]): raise HTTPException(404)
    return FileResponse(video["path"])

@app.get("/search")
async def search(q: str, limit: int = 10):
    embs = embedding_service.embed_text(q)
    results = vectordb_service.search(embs, n_results=limit)
    for res in results:
        res["frame_url"] = f"/frames/{res['metadata']['video_id']}/{res['metadata']['filename']}"
    return {"query": q, "results": results}

@app.get("/")
async def root(): return {"message": "ClipSeek API Active"}
