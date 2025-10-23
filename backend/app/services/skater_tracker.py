"""
Servizio per il tracking del pattinatore nel video
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SkaterTracker:
    """
    Traccia la posizione del pattinatore attraverso il video.
    Usa algoritmi di background subtraction e tracking per seguire il movimento.
    """

    def __init__(self, config: Dict):
        self.config = config

        # Background subtractor per rilevare movimento
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )

        # Tracker OpenCV (CSRT è buono per precisione)
        self.tracker = None
        self.tracking_active = False

        # Storia delle posizioni
        self.position_history: List[Tuple[int, int, float]] = []  # (x, y, timestamp)

    def initialize_tracking(self, frame: np.ndarray, bbox: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Inizializza il tracking del pattinatore.

        Args:
            frame: Primo frame del video
            bbox: Bounding box iniziale (x, y, w, h). Se None, viene rilevato automaticamente.

        Returns:
            True se l'inizializzazione ha successo
        """
        if bbox is None:
            # Rileva automaticamente il pattinatore
            bbox = self._detect_skater(frame)
            if bbox is None:
                logger.error("Failed to detect skater in initial frame")
                return False

        # Inizializza tracker
        self.tracker = cv2.TrackerCSRT_create()
        self.tracker.init(frame, bbox)
        self.tracking_active = True

        logger.info(f"Tracking initialized with bbox: {bbox}")
        return True

    def update(self, frame: np.ndarray, timestamp: float) -> Optional[Tuple[int, int]]:
        """
        Aggiorna la posizione del pattinatore nel frame corrente.

        Args:
            frame: Frame corrente
            timestamp: Timestamp in secondi

        Returns:
            Coordinate (x, y) del centro del pattinatore, o None se tracking fallisce
        """
        if not self.tracking_active or self.tracker is None:
            return None

        success, bbox = self.tracker.update(frame)

        if success:
            x, y, w, h = [int(v) for v in bbox]
            center_x = x + w // 2
            center_y = y + h // 2

            self.position_history.append((center_x, center_y, timestamp))
            return (center_x, center_y)
        else:
            logger.warning(f"Tracking lost at timestamp {timestamp}")
            # Prova a re-inizializzare
            new_bbox = self._detect_skater(frame)
            if new_bbox:
                self.tracker = cv2.TrackerCSRT_create()
                self.tracker.init(frame, new_bbox)
                return self.update(frame, timestamp)

            return None

    def _detect_skater(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Rileva automaticamente il pattinatore nel frame usando background subtraction.

        Returns:
            Bounding box (x, y, w, h) o None
        """
        # Applica background subtraction
        fg_mask = self.bg_subtractor.apply(frame)

        # Rimuovi ombre
        fg_mask[fg_mask == 127] = 0

        # Operazioni morfologiche per pulire
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

        # Trova contorni
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Prendi il contorno più grande (dovrebbe essere il pattinatore)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        # Verifica che sia abbastanza grande da essere un pattinatore
        if area < 500:  # TODO: Calibrare
            return None

        # Ottieni bounding box
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)

    def get_position_at_time(self, timestamp: float) -> Optional[Tuple[int, int]]:
        """
        Ottieni la posizione del pattinatore a un determinato timestamp.

        Args:
            timestamp: Timestamp in secondi

        Returns:
            Coordinate (x, y) o None
        """
        if not self.position_history:
            return None

        # Trova la posizione più vicina al timestamp richiesto
        closest = min(self.position_history, key=lambda p: abs(p[2] - timestamp))
        return (closest[0], closest[1])

    def get_trajectory(self, start_time: float, end_time: float) -> List[Tuple[int, int, float]]:
        """
        Ottieni la traiettoria del pattinatore in un intervallo di tempo.

        Args:
            start_time: Tempo di inizio (secondi)
            end_time: Tempo di fine (secondi)

        Returns:
            Lista di (x, y, timestamp)
        """
        return [
            pos for pos in self.position_history
            if start_time <= pos[2] <= end_time
        ]

    def get_velocity(self, timestamp: float, window: float = 0.1) -> float:
        """
        Calcola la velocità del pattinatore in un dato momento.

        Args:
            timestamp: Timestamp in secondi
            window: Finestra temporale per calcolare la velocità (secondi)

        Returns:
            Velocità in pixel/secondo
        """
        trajectory = self.get_trajectory(timestamp - window, timestamp + window)

        if len(trajectory) < 2:
            return 0.0

        # Calcola distanza totale percorsa
        total_distance = 0.0
        for i in range(1, len(trajectory)):
            dx = trajectory[i][0] - trajectory[i-1][0]
            dy = trajectory[i][1] - trajectory[i-1][1]
            total_distance += np.sqrt(dx**2 + dy**2)

        # Dividi per tempo
        time_span = trajectory[-1][2] - trajectory[0][2]
        if time_span > 0:
            return total_distance / time_span

        return 0.0

    def reset(self):
        """Reset del tracker"""
        self.tracker = None
        self.tracking_active = False
        self.position_history.clear()
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )
