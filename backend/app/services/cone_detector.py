"""
Servizio per il rilevamento dei coni nel video
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConeDetector:
    """
    Rileva i coni nel video in base al loro colore.
    Utilizza color segmentation per identificare i coni delle tre file.
    """

    def __init__(self, config: Dict):
        """
        Args:
            config: Configurazione con le informazioni sui coni (colori, distanze, etc.)
        """
        self.config = config
        self.field_setup = config.get('field_setup', {})

        # Color ranges in HSV - da calibrare in base ai colori reali
        # Questi sono valori di default, dovranno essere tarati
        self.color_ranges = {
            'orange': {
                'lower': np.array([5, 100, 100]),
                'upper': np.array([15, 255, 255])
            },
            'blue': {
                'lower': np.array([100, 100, 100]),
                'upper': np.array([130, 255, 255])
            },
            'yellow': {
                'lower': np.array([20, 100, 100]),
                'upper': np.array([30, 255, 255])
            }
        }

        # Cache delle posizioni dei coni (assumiamo siano fissi)
        self.cone_positions: Optional[Dict[int, List[Tuple[int, int]]]] = None

    def calibrate_colors(self, frame: np.ndarray) -> None:
        """
        Calibra i range di colore basandosi su un frame del video.
        Da implementare con UI per permettere la selezione interattiva.
        """
        # TODO: Implementare calibrazione interattiva colori
        pass

    def detect_cones_in_frame(self, frame: np.ndarray) -> Dict[int, List[Tuple[int, int]]]:
        """
        Rileva tutti i coni in un singolo frame.

        Args:
            frame: Frame del video in formato BGR

        Returns:
            Dict con chiave = numero linea, valore = lista di coordinate (x, y) dei coni
        """
        # Converti in HSV per color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        detected_cones = {}

        for line_num, line_config in self.field_setup.items():
            color = line_config.get('color', '')
            if color not in self.color_ranges:
                logger.warning(f"Color {color} not configured for line {line_num}")
                continue

            # Crea maschera per questo colore
            mask = self._create_color_mask(hsv, color)

            # Trova contorni
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filtra contorni validi (dimensione appropriata per coni)
            cones = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if self._is_valid_cone_size(area):
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        cones.append((cx, cy))

            # Ordina coni per posizione (assumiamo disposizione lineare)
            cones = self._sort_cones_by_position(cones, line_num)

            line_id = int(line_num.split('_')[1])
            detected_cones[line_id] = cones

        return detected_cones

    def _create_color_mask(self, hsv_frame: np.ndarray, color: str) -> np.ndarray:
        """Crea maschera binaria per un colore specifico"""
        color_range = self.color_ranges.get(color, {})
        lower = color_range.get('lower')
        upper = color_range.get('upper')

        if lower is None or upper is None:
            return np.zeros(hsv_frame.shape[:2], dtype=np.uint8)

        mask = cv2.inRange(hsv_frame, lower, upper)

        # Applica operazioni morfologiche per ridurre il rumore
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        return mask

    def _is_valid_cone_size(self, area: float) -> bool:
        """Verifica se l'area del contorno corrisponde a un cono"""
        # TODO: Calibrare questi valori in base alla distanza della camera
        min_area = 50  # pixel quadrati
        max_area = 5000
        return min_area <= area <= max_area

    def _sort_cones_by_position(self, cones: List[Tuple[int, int]], line_num: str) -> List[Tuple[int, int]]:
        """
        Ordina i coni in base alla loro posizione nella fila.
        Assumiamo che le file siano disposte orizzontalmente o verticalmente.
        """
        if not cones:
            return []

        # TODO: Determinare orientamento automaticamente
        # Per ora assumiamo disposizione orizzontale (ordina per x)
        return sorted(cones, key=lambda c: c[0])

    def initialize_cone_positions(self, video_path: str, num_frames: int = 30) -> Dict[int, List[Tuple[int, int]]]:
        """
        Inizializza le posizioni dei coni analizzando i primi frame del video.
        I coni sono fissi, quindi possiamo fare un'analisi iniziale e poi tracciare.

        Args:
            video_path: Path del video
            num_frames: Numero di frame da analizzare per l'inizializzazione

        Returns:
            Dict con le posizioni medie dei coni per ogni fila
        """
        cap = cv2.VideoCapture(video_path)

        all_detections = {1: [], 2: [], 3: []}

        for i in range(num_frames):
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.detect_cones_in_frame(frame)
            for line_id, cones in detections.items():
                if cones:
                    all_detections[line_id].append(cones)

        cap.release()

        # Calcola posizioni medie
        averaged_positions = {}
        for line_id, detections_list in all_detections.items():
            if detections_list:
                # Media delle posizioni su tutti i frame
                averaged_positions[line_id] = self._average_cone_positions(detections_list)
            else:
                averaged_positions[line_id] = []

        self.cone_positions = averaged_positions
        return averaged_positions

    def _average_cone_positions(self, detections_list: List[List[Tuple[int, int]]]) -> List[Tuple[int, int]]:
        """Calcola la posizione media dei coni da multiple rilevazioni"""
        if not detections_list:
            return []

        # Trova il numero più comune di coni rilevati
        max_cones = max(len(d) for d in detections_list)

        averaged = []
        for i in range(max_cones):
            positions = [d[i] for d in detections_list if i < len(d)]
            if positions:
                avg_x = int(np.mean([p[0] for p in positions]))
                avg_y = int(np.mean([p[1] for p in positions]))
                averaged.append((avg_x, avg_y))

        return averaged

    def detect_cone_displacement(self, current_positions: Dict[int, List[Tuple[int, int]]],
                                  threshold: float = 30.0) -> List[Tuple[int, int]]:
        """
        Rileva se qualche cono è stato spostato rispetto alla posizione iniziale.

        Args:
            current_positions: Posizioni correnti dei coni
            threshold: Distanza in pixel oltre la quale si considera spostamento

        Returns:
            Lista di (line_id, cone_index) dei coni spostati
        """
        if self.cone_positions is None:
            logger.warning("Cone positions not initialized")
            return []

        displaced = []

        for line_id, current_cones in current_positions.items():
            if line_id not in self.cone_positions:
                continue

            reference_cones = self.cone_positions[line_id]

            for i, (curr_pos, ref_pos) in enumerate(zip(current_cones, reference_cones)):
                distance = np.sqrt((curr_pos[0] - ref_pos[0])**2 + (curr_pos[1] - ref_pos[1])**2)
                if distance > threshold:
                    displaced.append((line_id, i))

        return displaced
