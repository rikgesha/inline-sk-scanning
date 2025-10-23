"""
Servizio principale per l'analisi dei video di slalom
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
import time
from datetime import datetime

from ..models.schemas import (
    AnalysisReport, TrickDetection, Penalty, ConeInfo,
    LineUsageStats, EvaluationScore
)
from .cone_detector import ConeDetector
from .skater_tracker import SkaterTracker

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """
    Analizzatore principale per video di slalom freestyle.
    Combina cone detection, skater tracking e analisi dei passi.
    """

    def __init__(self, config: Dict):
        self.config = config
        self.cone_detector = ConeDetector(config)
        self.skater_tracker = SkaterTracker(config)

        self.field_setup = config.get('field_setup', {})
        self.rules = config.get('rules', {})
        self.tricks_config = config.get('tricks', {})

    def analyze_video(self, video_path: str, skater_name: Optional[str] = None) -> AnalysisReport:
        """
        Analizza un video completo e genera un report.

        Args:
            video_path: Path al file video
            skater_name: Nome del pattinatore (opzionale)

        Returns:
            AnalysisReport con tutti i dati dell'analisi
        """
        start_time = time.time()
        logger.info(f"Starting analysis of video: {video_path}")

        # Apri video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        logger.info(f"Video info: {total_frames} frames at {fps} fps, duration: {duration:.2f}s")

        # Inizializza cone detector
        logger.info("Initializing cone positions...")
        cone_positions = self.cone_detector.initialize_cone_positions(video_path)

        # Crea struttura report
        report = AnalysisReport(
            video_filename=video_path.split('/')[-1],
            skater_name=skater_name,
            video_duration=duration,
            field_setup=self._create_field_setup_info(cone_positions),
            final_score=0.0  # Verrà calcolato dopo
        )

        # Reset tracker
        self.skater_tracker.reset()

        # Analizza frame per frame
        frame_idx = 0
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning

        initialized_tracking = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_idx / fps

            # Inizializza tracking al primo frame
            if not initialized_tracking:
                if self.skater_tracker.initialize_tracking(frame):
                    initialized_tracking = True
                    logger.info("Skater tracking initialized")

            # Aggiorna posizione pattinatore
            skater_pos = self.skater_tracker.update(frame, timestamp)

            # Rileva coni (periodicamente, non ogni frame per performance)
            if frame_idx % 10 == 0:
                current_cone_positions = self.cone_detector.detect_cones_in_frame(frame)

                # Controlla spostamenti coni
                displaced = self.cone_detector.detect_cone_displacement(current_cone_positions)
                for line_id, cone_idx in displaced:
                    penalty = Penalty(
                        type="cone_displaced",
                        timestamp=timestamp,
                        description=f"Cono spostato: Fila {line_id}, Cono {cone_idx}",
                        points_deducted=self.rules.get('cone_displacement_penalty', -0.2),
                        cone_line=line_id,
                        cone_index=cone_idx
                    )
                    report.penalties.append(penalty)

            frame_idx += 1

        cap.release()

        # Analizza traiettoria per rilevare attraversamenti e passi
        logger.info("Analyzing trajectory for trick detection...")
        tricks, line_usage = self._analyze_trajectory_for_tricks(
            self.skater_tracker.position_history,
            cone_positions
        )

        report.tricks_detail = tricks
        report.total_tricks_detected = len(tricks)
        report.valid_tricks = sum(1 for t in tricks if t.is_valid)
        report.invalid_tricks = len(tricks) - report.valid_tricks

        report.line_usage = line_usage
        report.total_crossings = sum(lu.crossings for lu in line_usage)

        # Calcola penalità totali
        report.total_penalty_points = sum(p.points_deducted for p in report.penalties)

        # Calcola valutazione e punteggio finale
        report.evaluation_scores = self._calculate_evaluation(report)
        report.final_score = self._calculate_final_score(report)

        processing_time = time.time() - start_time
        report.processing_time_seconds = processing_time

        logger.info(f"Analysis completed in {processing_time:.2f}s")
        logger.info(f"Final score: {report.final_score:.2f}/10.0")

        return report

    def _create_field_setup_info(self, cone_positions: Dict[int, List[Tuple[int, int]]]) -> List[ConeInfo]:
        """Crea le informazioni sul setup del campo"""
        field_info = []

        for line_num, line_config in self.field_setup.items():
            line_id = int(line_num.split('_')[1])
            detected = len(cone_positions.get(line_id, []))

            field_info.append(ConeInfo(
                line_number=line_id,
                num_cones=line_config['cones'],
                distance_cm=line_config['distance_cm'],
                color=line_config['color'],
                detected_cones=detected
            ))

        return field_info

    def _analyze_trajectory_for_tricks(
        self,
        trajectory: List[Tuple[int, int, float]],
        cone_positions: Dict[int, List[Tuple[int, int]]]
    ) -> Tuple[List[TrickDetection], List[LineUsageStats]]:
        """
        Analizza la traiettoria per rilevare attraversamenti e passi.

        Per MVP: rileva semplicemente gli attraversamenti delle file di coni.
        In fasi successive: riconoscimento pattern per passi specifici.
        """
        tricks = []
        line_crossings = {1: 0, 2: 0, 3: 0}

        if not trajectory:
            return tricks, self._create_line_usage_stats(line_crossings)

        # Per ogni segmento della traiettoria
        min_cones = self.rules.get('min_cones_valid_trick', 4)

        # Algoritmo semplificato: rileva quando il pattinatore attraversa una fila
        # TODO: Implementare riconoscimento pattern più sofisticato

        for i in range(1, len(trajectory)):
            prev_pos = trajectory[i-1]
            curr_pos = trajectory[i]

            # Controlla attraversamento di ogni fila
            for line_id, cones in cone_positions.items():
                if not cones:
                    continue

                crossed, num_cones = self._check_line_crossing(
                    prev_pos[:2], curr_pos[:2], cones
                )

                if crossed and num_cones > 0:
                    line_crossings[line_id] += 1

                    # Crea trick detection (generico per MVP)
                    trick = TrickDetection(
                        trick_name="Passo Generico",  # TODO: Riconoscimento specifico
                        start_time=prev_pos[2],
                        end_time=curr_pos[2],
                        cones_crossed=num_cones,
                        line_number=line_id,
                        is_valid=num_cones >= min_cones,
                        confidence=0.8,  # TODO: Calcolare confidence reale
                        points=1.0 if num_cones >= min_cones else 0.0
                    )
                    tricks.append(trick)

        line_usage = self._create_line_usage_stats(line_crossings)

        return tricks, line_usage

    def _check_line_crossing(
        self,
        prev_pos: Tuple[int, int],
        curr_pos: Tuple[int, int],
        cones: List[Tuple[int, int]]
    ) -> Tuple[bool, int]:
        """
        Verifica se c'è stato un attraversamento di una fila di coni.

        Returns:
            (crossed, num_cones_crossed)
        """
        # TODO: Implementare logica più sofisticata
        # Per ora: verifica semplice se la traiettoria passa vicino ai coni

        # Calcola distanza minima dalla linea dei coni
        # Questo è un placeholder - serve algoritmo più robusto

        return False, 0  # Placeholder

    def _create_line_usage_stats(self, crossings: Dict[int, int]) -> List[LineUsageStats]:
        """Crea statistiche di utilizzo delle file"""
        total = sum(crossings.values())
        stats = []

        for line_id in [1, 2, 3]:
            line_config = self.field_setup.get(f'line_{line_id}', {})
            count = crossings.get(line_id, 0)
            percentage = (count / total * 100) if total > 0 else 0

            stats.append(LineUsageStats(
                line_number=line_id,
                distance_cm=line_config.get('distance_cm', 0),
                crossings=count,
                percentage=percentage
            ))

        return stats

    def _calculate_evaluation(self, report: AnalysisReport) -> List[EvaluationScore]:
        """Calcola i punteggi per i vari criteri di valutazione"""
        criteria = self.config.get('evaluation_criteria', {})
        scores = []

        # 1. Difficoltà tecnica (basata sui passi eseguiti)
        tech_difficulty_score = self._evaluate_technical_difficulty(report)
        scores.append(EvaluationScore(
            criterion="Difficoltà Tecnica",
            score=tech_difficulty_score,
            weight=criteria.get('technical_difficulty', {}).get('weight', 0.3),
            weighted_score=tech_difficulty_score * criteria.get('technical_difficulty', {}).get('weight', 0.3)
        ))

        # 2. Varietà dei passi
        variety_score = self._evaluate_trick_variety(report)
        scores.append(EvaluationScore(
            criterion="Varietà Passi",
            score=variety_score,
            weight=criteria.get('trick_variety', {}).get('weight', 0.25),
            weighted_score=variety_score * criteria.get('trick_variety', {}).get('weight', 0.25)
        ))

        # 3. Pulizia esecuzione
        cleanliness_score = self._evaluate_execution_cleanliness(report)
        scores.append(EvaluationScore(
            criterion="Pulizia Esecuzione",
            score=cleanliness_score,
            weight=criteria.get('execution_cleanliness', {}).get('weight', 0.25),
            weighted_score=cleanliness_score * criteria.get('execution_cleanliness', {}).get('weight', 0.25)
        ))

        # 4. Utilizzo campo
        field_usage_score = self._evaluate_field_usage(report)
        scores.append(EvaluationScore(
            criterion="Utilizzo Campo",
            score=field_usage_score,
            weight=criteria.get('field_usage', {}).get('weight', 0.2),
            weighted_score=field_usage_score * criteria.get('field_usage', {}).get('weight', 0.2)
        ))

        return scores

    def _evaluate_technical_difficulty(self, report: AnalysisReport) -> float:
        """Valuta difficoltà tecnica basata sui passi"""
        # TODO: Implementare con riconoscimento passi reali
        if report.valid_tricks == 0:
            return 0.0

        # Per ora: score base su numero di passi validi
        return min(10.0, report.valid_tricks * 0.2)

    def _evaluate_trick_variety(self, report: AnalysisReport) -> float:
        """Valuta varietà dei passi"""
        # TODO: Implementare conteggio passi diversi
        unique_tricks = len(set(t.trick_name for t in report.tricks_detail))
        return min(10.0, unique_tricks * 1.5)

    def _evaluate_execution_cleanliness(self, report: AnalysisReport) -> float:
        """Valuta pulizia dell'esecuzione"""
        base_score = 10.0

        # Penalità per coni spostati
        cone_penalties = sum(1 for p in report.penalties if p.type == "cone_displaced")
        score = base_score - (cone_penalties * 0.5)

        # Penalità per passi non validi
        invalid_ratio = report.invalid_tricks / max(1, report.total_tricks_detected)
        score -= invalid_ratio * 3.0

        return max(0.0, min(10.0, score))

    def _evaluate_field_usage(self, report: AnalysisReport) -> float:
        """Valuta utilizzo bilanciato del campo"""
        if not report.line_usage:
            return 0.0

        # Ideale: utilizzo bilanciato tra le tre file
        # Calcola deviazione standard delle percentuali
        percentages = [lu.percentage for lu in report.line_usage]
        ideal = 100 / 3  # 33.33% per fila

        deviations = [abs(p - ideal) for p in percentages]
        avg_deviation = sum(deviations) / len(deviations)

        # Score: 10 se perfettamente bilanciato, decresce con la deviazione
        score = 10.0 - (avg_deviation / 10.0)
        return max(0.0, min(10.0, score))

    def _calculate_final_score(self, report: AnalysisReport) -> float:
        """Calcola il punteggio finale"""
        # Somma dei punteggi pesati
        base_score = sum(es.weighted_score for es in report.evaluation_scores)

        # Applica penalità
        final_score = base_score + report.total_penalty_points

        # Normalizza tra 0 e 10
        return max(0.0, min(10.0, final_score))
