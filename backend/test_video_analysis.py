#!/usr/bin/env python3
"""
Script di test per l'analisi di video di slalom inline freestyle.
Esegui questo script per testare l'applicazione con un video reale.

Usage:
    python test_video_analysis.py <path_to_video.mp4> [skater_name]

Example:
    python test_video_analysis.py test_slalom.mp4 "Rebe"
"""

import sys
import os
import yaml
import json
from pathlib import Path
from datetime import datetime

# Aggiungi il path corrente per importare i moduli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.video_analyzer import VideoAnalyzer


def load_config():
    """Carica la configurazione dal file YAML"""
    config_path = Path(__file__).parent.parent / "config" / "scoring_config.yaml"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️  File di configurazione non trovato: {config_path}")
        print("Uso configurazione di default...")
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
            },
            'evaluation_criteria': {
                'technical_difficulty': {'weight': 0.30},
                'trick_variety': {'weight': 0.25},
                'execution_cleanliness': {'weight': 0.25},
                'field_usage': {'weight': 0.20}
            }
        }


def print_report(report):
    """Stampa il report in formato leggibile"""
    print("\n" + "="*80)
    print("📊 REPORT ANALISI ESIBIZIONE - Inline Slalom Classic")
    print("="*80)

    # Metadata
    print(f"\n📝 INFORMAZIONI")
    print(f"   Video: {report.video_filename}")
    if report.skater_name:
        print(f"   Pattinatore: {report.skater_name}")
    print(f"   Durata: {report.video_duration:.2f} secondi ({report.video_duration/60:.2f} minuti)")
    print(f"   Data analisi: {report.analysis_timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   Tempo elaborazione: {report.processing_time_seconds:.2f} secondi")

    # Setup campo
    print(f"\n🎯 SETUP CAMPO")
    for field in report.field_setup:
        detected_status = "✓" if field.detected_cones > 0 else "✗"
        print(f"   {detected_status} Fila {field.line_number} ({field.distance_cm}cm, {field.color}): "
              f"{field.detected_cones}/{field.num_cones} coni rilevati")

    # Statistiche passi
    print(f"\n📌 STATISTICHE PASSI")
    print(f"   Passi totali rilevati: {report.total_tricks_detected}")
    print(f"   ✓ Passi validi (≥4 coni): {report.valid_tricks}")
    print(f"   ✗ Passi non validi: {report.invalid_tricks}")

    if report.tricks_detail:
        print(f"\n   Dettaglio passi:")
        for i, trick in enumerate(report.tricks_detail[:10], 1):  # Mostra solo i primi 10
            status = "✓" if trick.is_valid else "✗"
            print(f"      {status} {trick.trick_name} - Fila {trick.line_number} - "
                  f"{trick.cones_crossed} coni - {trick.start_time:.1f}s")
        if len(report.tricks_detail) > 10:
            print(f"      ... e altri {len(report.tricks_detail) - 10} passi")

    # Utilizzo campo
    print(f"\n📏 UTILIZZO CAMPO")
    for line in report.line_usage:
        bar_length = int(line.percentage / 2)  # 50 = 100%
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"   Fila {line.distance_cm}cm: {bar} {line.crossings} ({line.percentage:.1f}%)")
    print(f"   Totale attraversamenti: {report.total_crossings}")

    # Penalità
    print(f"\n⚠️  PENALITÀ")
    if report.penalties:
        for penalty in report.penalties:
            print(f"   • {penalty.description} @ {penalty.timestamp:.1f}s → {penalty.points_deducted:.2f} punti")
        print(f"   Penalità totale: {report.total_penalty_points:.2f} punti")
    else:
        print("   Nessuna penalità rilevata! 🎉")

    # Valutazione
    print(f"\n🎯 VALUTAZIONE DETTAGLIATA")
    for eval_score in report.evaluation_scores:
        bar_length = int(eval_score.score)
        bar = "★" * bar_length + "☆" * (10 - bar_length)
        print(f"   {eval_score.criterion:30s} {bar} {eval_score.score:.1f}/10 "
              f"(peso {eval_score.weight*100:.0f}% → {eval_score.weighted_score:.2f})")

    # Voto finale
    print(f"\n⭐ VOTO FINALE")
    final_bar_length = int(report.final_score)
    final_bar = "★" * final_bar_length + "☆" * (10 - final_bar_length)
    print(f"   {final_bar} {report.final_score:.2f}/10.0")

    # Avvisi
    if report.warnings:
        print(f"\n⚠️  AVVISI")
        for warning in report.warnings:
            print(f"   • {warning}")

    print("\n" + "="*80 + "\n")


def save_report_json(report, output_path):
    """Salva il report in formato JSON"""
    report_dict = report.model_dump(mode='json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False, default=str)

    print(f"✓ Report salvato in: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_video_analysis.py <path_to_video> [skater_name]")
        print("\nExample:")
        print("  python test_video_analysis.py test_slalom.mp4")
        print("  python test_video_analysis.py test_slalom.mp4 'Mario Rossi'")
        sys.exit(1)

    video_path = sys.argv[1]
    skater_name = sys.argv[2] if len(sys.argv) > 2 else None

    # Verifica che il video esista
    if not os.path.exists(video_path):
        print(f"❌ Errore: File video non trovato: {video_path}")
        sys.exit(1)

    print(f"\n🎬 Caricamento video: {video_path}")
    if skater_name:
        print(f"👤 Pattinatore: {skater_name}")

    # Carica configurazione
    print("\n⚙️  Caricamento configurazione...")
    config = load_config()

    # Crea analyzer
    print("🔧 Inizializzazione analizzatore...")
    analyzer = VideoAnalyzer(config)

    # Analizza video
    print("🎯 Avvio analisi video...")
    print("   (Questo potrebbe richiedere alcuni minuti...)\n")

    try:
        report = analyzer.analyze_video(video_path, skater_name)

        # Stampa report
        print_report(report)

        # Salva report JSON
        video_name = Path(video_path).stem
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"report_{video_name}_{timestamp}.json"
        save_report_json(report, output_path)

        print("✅ Analisi completata con successo!")

    except Exception as e:
        print(f"\n❌ Errore durante l'analisi:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        print("\nTraceback completo:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
