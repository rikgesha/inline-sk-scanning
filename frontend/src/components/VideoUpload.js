import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './VideoUpload.css';

function VideoUpload({ onUploadComplete, onAnalysisComplete, uploadId }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [skaterName, setSkaterName] = useState('');
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (uploadId && !analyzing) {
      startAnalysis();
    }
  }, [uploadId]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setStatus('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Seleziona un video prima di caricare');
      return;
    }

    setUploading(true);
    setStatus('Caricamento video...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setStatus('Video caricato con successo!');
      onUploadComplete(response.data.upload_id);
    } catch (error) {
      console.error('Upload error:', error);
      setStatus(`Errore durante il caricamento: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const startAnalysis = async () => {
    setAnalyzing(true);
    setStatus('Avvio analisi...');

    try {
      // Start analysis
      await axios.post('/api/analyze', {
        upload_id: uploadId,
        skater_name: skaterName || null,
      });

      // Poll for status
      pollAnalysisStatus();
    } catch (error) {
      console.error('Analysis error:', error);
      setStatus(`Errore durante l'analisi: ${error.message}`);
      setAnalyzing(false);
    }
  };

  const pollAnalysisStatus = async () => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/status/${uploadId}`);
        const data = response.data;

        setProgress(data.progress_percentage);
        setStatus(data.message);

        if (data.status === 'completed') {
          clearInterval(interval);
          setAnalyzing(false);
          onAnalysisComplete(data.report);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setAnalyzing(false);
          setStatus(`Analisi fallita: ${data.message}`);
        }
      } catch (error) {
        console.error('Status poll error:', error);
        clearInterval(interval);
        setAnalyzing(false);
      }
    }, 2000); // Poll every 2 seconds
  };

  return (
    <div className="video-upload-container">
      <div className="upload-box">
        <h2>Carica Video Esibizione</h2>

        <div className="form-group">
          <label htmlFor="skater-name">Nome Pattinatore (opzionale)</label>
          <input
            id="skater-name"
            type="text"
            value={skaterName}
            onChange={(e) => setSkaterName(e.target.value)}
            placeholder="Es: Mario Rossi"
            disabled={uploading || analyzing}
          />
        </div>

        <div className="form-group">
          <label htmlFor="video-file">File Video</label>
          <input
            id="video-file"
            type="file"
            accept="video/mp4,video/avi,video/mov,video/mkv"
            onChange={handleFileChange}
            disabled={uploading || analyzing}
          />
        </div>

        {file && (
          <div className="file-info">
            <p>File selezionato: <strong>{file.name}</strong></p>
            <p>Dimensione: {(file.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || uploading || analyzing}
          className="upload-button"
        >
          {uploading ? 'Caricamento...' : analyzing ? 'Analisi in corso...' : 'Carica e Analizza'}
        </button>

        {status && (
          <div className={`status-message ${status.includes('Errore') ? 'error' : 'info'}`}>
            {status}
          </div>
        )}

        {analyzing && (
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
            <span className="progress-text">{progress.toFixed(0)}%</span>
          </div>
        )}

        <div className="info-box">
          <h3>ℹ️ Informazioni</h3>
          <ul>
            <li>Formati supportati: MP4, AVI, MOV, MKV</li>
            <li>Durata tipica: 2 minuti (Classic)</li>
            <li>Assicurati che i coni siano ben visibili</li>
            <li>Angolazione consigliata: laterale o dall'alto</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default VideoUpload;
