"""
Pydantic models for API requests and responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ConeInfo(BaseModel):
    """Informazioni su una singola fila di coni"""
    line_number: int = Field(..., description="Numero fila (1, 2, o 3)")
    num_cones: int = Field(..., description="Numero di coni")
    distance_cm: int = Field(..., description="Distanza tra coni in cm")
    color: str = Field(..., description="Colore dei coni")
    detected_cones: int = Field(0, description="Coni effettivamente rilevati")


class TrickDetection(BaseModel):
    """Passo rilevato durante l'esibizione"""
    trick_name: str = Field(..., description="Nome del passo")
    start_time: float = Field(..., description="Tempo inizio (secondi)")
    end_time: float = Field(..., description="Tempo fine (secondi)")
    cones_crossed: int = Field(..., description="Numero coni attraversati")
    line_number: int = Field(..., description="Fila utilizzata")
    is_valid: bool = Field(..., description="Se il passo è valido (>= 4 coni)")
    confidence: float = Field(1.0, description="Confidence del rilevamento (0-1)")
    points: float = Field(0.0, description="Punti assegnati")


class Penalty(BaseModel):
    """Penalità rilevata"""
    type: str = Field(..., description="Tipo di penalità")
    timestamp: float = Field(..., description="Momento della penalità (secondi)")
    description: str = Field(..., description="Descrizione")
    points_deducted: float = Field(..., description="Punti detratti")
    cone_line: Optional[int] = Field(None, description="Fila del cono (se applicabile)")
    cone_index: Optional[int] = Field(None, description="Indice del cono (se applicabile)")


class LineUsageStats(BaseModel):
    """Statistiche utilizzo di una fila"""
    line_number: int
    distance_cm: int
    crossings: int = 0
    percentage: float = 0.0


class EvaluationScore(BaseModel):
    """Punteggio per un criterio di valutazione"""
    criterion: str
    score: float = Field(..., ge=0, le=10)
    weight: float = Field(..., ge=0, le=1)
    weighted_score: float


class AnalysisReport(BaseModel):
    """Report completo dell'analisi di un'esibizione"""

    # Metadata
    video_filename: str
    skater_name: Optional[str] = None
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    video_duration: float

    # Setup campo
    field_setup: List[ConeInfo]

    # Statistiche passi
    total_tricks_detected: int = 0
    valid_tricks: int = 0
    invalid_tricks: int = 0
    tricks_detail: List[TrickDetection] = []

    # Utilizzo campo
    line_usage: List[LineUsageStats] = []
    total_crossings: int = 0

    # Penalità
    penalties: List[Penalty] = []
    total_penalty_points: float = 0.0

    # Valutazione
    evaluation_scores: List[EvaluationScore] = []
    final_score: float = Field(..., ge=0, le=10)

    # Dati aggiuntivi
    processing_time_seconds: float = 0.0
    warnings: List[str] = []


class VideoUploadResponse(BaseModel):
    """Risposta dopo upload video"""
    status: str
    filename: str
    file_size: int
    upload_id: str


class AnalysisRequest(BaseModel):
    """Richiesta di analisi"""
    upload_id: str
    skater_name: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


class AnalysisStatus(BaseModel):
    """Status dell'analisi in corso"""
    upload_id: str
    status: str  # "processing", "completed", "failed"
    progress_percentage: float = 0.0
    message: Optional[str] = None
    report: Optional[AnalysisReport] = None
