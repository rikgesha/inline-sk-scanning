import React, { useState } from 'react';
import './App.css';
import VideoUpload from './components/VideoUpload';
import AnalysisReport from './components/AnalysisReport';

function App() {
  const [uploadId, setUploadId] = useState(null);
  const [report, setReport] = useState(null);

  const handleUploadComplete = (id) => {
    setUploadId(id);
  };

  const handleAnalysisComplete = (analysisReport) => {
    setReport(analysisReport);
  };

  const handleReset = () => {
    setUploadId(null);
    setReport(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🛼 Inline Slalom Scoring App</h1>
        <p>Analisi automatica di esibizioni freestyle slalom</p>
      </header>

      <main className="App-main">
        {!report ? (
          <VideoUpload
            onUploadComplete={handleUploadComplete}
            onAnalysisComplete={handleAnalysisComplete}
            uploadId={uploadId}
          />
        ) : (
          <AnalysisReport report={report} onReset={handleReset} />
        )}
      </main>

      <footer className="App-footer">
        <p>Inline Slalom Scoring v0.1.0 - MVP</p>
      </footer>
    </div>
  );
}

export default App;
