"""
FastAPI application for inline slalom video analysis
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

from .models.schemas import (
    VideoUploadResponse,
    AnalysisRequest,
    AnalysisStatus,
    AnalysisReport
)
from .services.video_analyzer import VideoAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Inline Slalom Scoring API",
    description="API per l'analisi automatica di video di pattinaggio inline freestyle slalom",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configurare in produzione
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
CONFIG_DIR = Path("../config")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# In-memory storage for analysis status
# TODO: Usare Redis o database per produzione
analysis_storage: Dict[str, AnalysisStatus] = {}

# Load configuration
def load_config() -> Dict:
    """Load scoring configuration from YAML"""
    config_path = CONFIG_DIR / "scoring_config.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        # Return default config
        return {
            'field_setup': {
                'line_1': {'cones': 20, 'distance_cm': 50, 'color': 'orange'},
                'line_2': {'cones': 20, 'distance_cm': 80, 'color': 'blue'},
                'line_3': {'cones': 14, 'distance_cm': 120, 'color': 'yellow'}
            },
            'rules': {
                'classic_duration_seconds': 120,
                'min_cones_valid_trick': 4,
                'cone_displacement_penalty': -0.2
            }
        }

config = load_config()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Inline Slalom Scoring API",
        "version": "0.1.0"
    }


@app.post("/api/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file for analysis
    """
    # Validate file type
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {allowed_extensions}"
        )

    # Generate unique ID
    upload_id = str(uuid.uuid4())

    # Save file
    file_path = UPLOAD_DIR / f"{upload_id}{file_ext}"

    try:
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size

        logger.info(f"Video uploaded: {upload_id}, size: {file_size} bytes")

        # Initialize analysis status
        analysis_storage[upload_id] = AnalysisStatus(
            upload_id=upload_id,
            status="uploaded",
            progress_percentage=0.0,
            message="Video caricato con successo"
        )

        return VideoUploadResponse(
            status="success",
            filename=file.filename,
            file_size=file_size,
            upload_id=upload_id
        )

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/analyze")
async def analyze_video(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start video analysis in background
    """
    upload_id = request.upload_id

    if upload_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Upload ID not found")

    # Find video file
    video_files = list(UPLOAD_DIR.glob(f"{upload_id}.*"))
    if not video_files:
        raise HTTPException(status_code=404, detail="Video file not found")

    video_path = video_files[0]

    # Update status
    analysis_storage[upload_id].status = "processing"
    analysis_storage[upload_id].message = "Analisi in corso..."

    # Start analysis in background
    background_tasks.add_task(
        process_video_analysis,
        upload_id,
        str(video_path),
        request.skater_name,
        request.custom_config
    )

    return JSONResponse({
        "status": "processing",
        "upload_id": upload_id,
        "message": "Analisi avviata in background"
    })


async def process_video_analysis(
    upload_id: str,
    video_path: str,
    skater_name: Optional[str] = None,
    custom_config: Optional[Dict] = None
):
    """
    Process video analysis (runs in background)
    """
    try:
        # Use custom config if provided, otherwise use default
        analysis_config = custom_config if custom_config else config

        # Create analyzer
        analyzer = VideoAnalyzer(analysis_config)

        # Update progress
        analysis_storage[upload_id].progress_percentage = 10.0
        analysis_storage[upload_id].message = "Inizializzazione analisi..."

        # Run analysis
        logger.info(f"Starting analysis for {upload_id}")
        report = analyzer.analyze_video(video_path, skater_name)

        # Update status with results
        analysis_storage[upload_id].status = "completed"
        analysis_storage[upload_id].progress_percentage = 100.0
        analysis_storage[upload_id].message = "Analisi completata"
        analysis_storage[upload_id].report = report

        logger.info(f"Analysis completed for {upload_id}, score: {report.final_score}")

    except Exception as e:
        logger.error(f"Analysis failed for {upload_id}: {e}", exc_info=True)
        analysis_storage[upload_id].status = "failed"
        analysis_storage[upload_id].message = f"Errore: {str(e)}"


@app.get("/api/status/{upload_id}", response_model=AnalysisStatus)
async def get_analysis_status(upload_id: str):
    """
    Get analysis status and results
    """
    if upload_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Upload ID not found")

    return analysis_storage[upload_id]


@app.get("/api/config")
async def get_config():
    """
    Get current scoring configuration
    """
    return config


@app.post("/api/config")
async def update_config(new_config: Dict):
    """
    Update scoring configuration
    """
    global config
    config = new_config

    # Save to file
    config_path = CONFIG_DIR / "scoring_config.yaml"
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, allow_unicode=True)
        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")


@app.delete("/api/analysis/{upload_id}")
async def delete_analysis(upload_id: str):
    """
    Delete analysis data and video file
    """
    if upload_id in analysis_storage:
        del analysis_storage[upload_id]

    # Delete video file
    video_files = list(UPLOAD_DIR.glob(f"{upload_id}.*"))
    for vf in video_files:
        vf.unlink()

    return {"status": "success", "message": "Analysis deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
