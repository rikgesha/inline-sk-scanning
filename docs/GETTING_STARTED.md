# Getting Started - Inline Slalom Scoring App

## Prerequisiti

### Backend
- Python 3.8 o superiore
- pip (package manager Python)

### Frontend
- Node.js 16 o superiore
- npm (incluso con Node.js)

## Installazione

### 1. Clona il repository
```bash
git clone <repository-url>
cd inline-sk-scanning
```

### 2. Setup Backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Setup Frontend

```bash
cd ../frontend
npm install
```

## Avvio dell'Applicazione

### Backend (Terminal 1)
```bash
cd backend
python -m app.main
```

Il backend sarà disponibile su: `http://localhost:8000`

### Frontend (Terminal 2)
```bash
cd frontend
npm start
```

Il frontend aprirà automaticamente il browser su: `http://localhost:3000`

## Utilizzo

1. **Carica Video**: Seleziona un video di un'esibizione di slalom freestyle
2. **Inserisci Nome** (opzionale): Nome del pattinatore
3. **Avvia Analisi**: Clicca su "Carica e Analizza"
4. **Attendi**: L'analisi richiederà alcuni minuti a seconda della durata del video
5. **Visualizza Report**: Al termine vedrai un report dettagliato con:
   - Voto finale
   - Statistiche passi
   - Utilizzo del campo
   - Penalità
   - Valutazione per criteri

## Configurazione

Il file `config/scoring_config.yaml` contiene:
- Setup del campo (colori coni, distanze)
- Regole di validazione
- Sistema di punteggio
- Criteri di valutazione

**IMPORTANTE**: Prima dell'uso in produzione, dovrai configurare i colori reali dei coni usati nelle gare.

## Stato Attuale (MVP)

Questo è un **Minimum Viable Product** con funzionalità base:

✅ **Implementato:**
- Upload video
- Detection coni per colore
- Tracking pattinatore
- Sistema di scoring configurabile
- Report dettagliato

⚠️ **Da Migliorare:**
- Riconoscimento passi specifici (attualmente generico)
- Calibrazione colori coni (richiede setup)
- Algoritmo di attraversamento coni (da raffinare)
- Rilevamento coni spostati (base implementato)

## Prossimi Passi

1. **Testare con video reali** delle tue gare
2. **Calibrare i colori** dei coni nel file config
3. **Definire i passi specifici** (crazy, nelson, ecc.) con le caratteristiche per riconoscerli
4. **Raffinare gli algoritmi** in base ai risultati dei test

## Troubleshooting

### Il backend non si avvia
- Verifica di aver installato tutte le dipendenze: `pip install -r requirements.txt`
- Controlla che Python sia 3.8+: `python --version`

### Il frontend non si connette al backend
- Verifica che il backend sia avviato su porta 8000
- Controlla la configurazione proxy in `frontend/package.json`

### L'analisi fallisce
- Verifica che il formato video sia supportato (MP4, AVI, MOV, MKV)
- Controlla i log del backend per errori dettagliati
- Assicurati che OpenCV sia installato correttamente

## Supporto

Per problemi o domande, apri un issue nel repository.
