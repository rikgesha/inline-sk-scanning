import React from 'react';
import './AnalysisReport.css';

function AnalysisReport({ report, onReset }) {
  if (!report) return null;

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="analysis-report-container">
      <div className="report-header">
        <h2>📊 Report Analisi Esibizione</h2>
        <button onClick={onReset} className="new-analysis-button">
          Nuova Analisi
        </button>
      </div>

      <div className="report-grid">
        {/* Metadata */}
        <div className="report-card">
          <h3>📝 Informazioni</h3>
          <div className="info-row">
            <span className="label">Video:</span>
            <span className="value">{report.video_filename}</span>
          </div>
          {report.skater_name && (
            <div className="info-row">
              <span className="label">Pattinatore:</span>
              <span className="value">{report.skater_name}</span>
            </div>
          )}
          <div className="info-row">
            <span className="label">Durata:</span>
            <span className="value">{formatTime(report.video_duration)}</span>
          </div>
          <div className="info-row">
            <span className="label">Data analisi:</span>
            <span className="value">
              {new Date(report.analysis_timestamp).toLocaleString('it-IT')}
            </span>
          </div>
        </div>

        {/* Final Score */}
        <div className="report-card score-card">
          <h3>⭐ Voto Finale</h3>
          <div className="final-score">
            {report.final_score.toFixed(2)}<span className="score-max">/10.0</span>
          </div>
          <div className="score-bar">
            <div
              className="score-bar-fill"
              style={{ width: `${(report.final_score / 10) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Tricks Statistics */}
        <div className="report-card">
          <h3>📌 Statistiche Passi</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{report.total_tricks_detected}</div>
              <div className="stat-label">Passi Totali</div>
            </div>
            <div className="stat-item success">
              <div className="stat-value">{report.valid_tricks}</div>
              <div className="stat-label">Passi Validi</div>
            </div>
            <div className="stat-item warning">
              <div className="stat-value">{report.invalid_tricks}</div>
              <div className="stat-label">Passi Non Validi</div>
            </div>
          </div>
        </div>

        {/* Field Usage */}
        <div className="report-card">
          <h3>📏 Utilizzo Campo</h3>
          {report.line_usage.map((line) => (
            <div key={line.line_number} className="line-usage">
              <div className="line-info">
                <span className="line-label">
                  Fila {line.distance_cm}cm
                </span>
                <span className="line-value">
                  {line.crossings} attraversamenti ({line.percentage.toFixed(1)}%)
                </span>
              </div>
              <div className="usage-bar">
                <div
                  className="usage-bar-fill"
                  style={{ width: `${line.percentage}%` }}
                ></div>
              </div>
            </div>
          ))}
          <div className="info-row">
            <span className="label">Totale attraversamenti:</span>
            <span className="value">{report.total_crossings}</span>
          </div>
        </div>

        {/* Penalties */}
        <div className="report-card">
          <h3>⚠️ Penalità</h3>
          {report.penalties.length > 0 ? (
            <>
              <div className="penalties-list">
                {report.penalties.map((penalty, idx) => (
                  <div key={idx} className="penalty-item">
                    <span className="penalty-time">{formatTime(penalty.timestamp)}</span>
                    <span className="penalty-desc">{penalty.description}</span>
                    <span className="penalty-points">
                      {penalty.points_deducted.toFixed(2)} pt
                    </span>
                  </div>
                ))}
              </div>
              <div className="penalty-total">
                Penalità totale: <strong>{report.total_penalty_points.toFixed(2)} punti</strong>
              </div>
            </>
          ) : (
            <p className="no-penalties">Nessuna penalità rilevata! 🎉</p>
          )}
        </div>

        {/* Evaluation Scores */}
        <div className="report-card">
          <h3>🎯 Valutazione Dettagliata</h3>
          {report.evaluation_scores.map((eval_score) => (
            <div key={eval_score.criterion} className="eval-score">
              <div className="eval-header">
                <span className="eval-criterion">{eval_score.criterion}</span>
                <span className="eval-value">
                  {eval_score.score.toFixed(1)}/10
                  <span className="eval-weight"> (peso: {(eval_score.weight * 100).toFixed(0)}%)</span>
                </span>
              </div>
              <div className="eval-bar">
                <div
                  className="eval-bar-fill"
                  style={{ width: `${(eval_score.score / 10) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>

        {/* Field Setup Info */}
        <div className="report-card">
          <h3>🎯 Setup Campo</h3>
          {report.field_setup.map((field) => (
            <div key={field.line_number} className="field-info">
              <span className="field-label">
                Fila {field.line_number} ({field.distance_cm}cm)
              </span>
              <span className="field-value">
                {field.detected_cones}/{field.num_cones} coni rilevati
              </span>
            </div>
          ))}
        </div>

        {/* Processing Info */}
        <div className="report-card">
          <h3>⚙️ Informazioni Elaborazione</h3>
          <div className="info-row">
            <span className="label">Tempo di elaborazione:</span>
            <span className="value">{report.processing_time_seconds.toFixed(2)}s</span>
          </div>
          {report.warnings && report.warnings.length > 0 && (
            <div className="warnings">
              <h4>⚠️ Avvisi:</h4>
              <ul>
                {report.warnings.map((warning, idx) => (
                  <li key={idx}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalysisReport;
