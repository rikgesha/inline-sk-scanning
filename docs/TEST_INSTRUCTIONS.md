# Istruzioni per Testare l'Applicazione

Questa guida ti spiega come testare l'applicazione di analisi slalom con il tuo video.

## Prerequisiti

### 1. Scarica il Video da Mega

Il video è disponibile qui: https://mega.nz/file/4RIU2DyB#otuNNuMFLghD0G1lxD2zJnXRP-2voOhcasEOnwOrn18

Scaricalo e salvalo nella cartella `backend/test_videos/` con nome `test_slalom.mp4`

### 2. Installa Python

Assicurati di avere Python 3.8 o superiore installato:
```bash
python --version
```

### 3. Installa le Dipendenze

```bash
cd backend
pip install -r requirements.txt
```

**Nota:** Se `moviepy` dà errore durante l'installazione, puoi ignorarlo - non è essenziale per l'MVP.

Se hai problemi, installa solo le dipendenze essenziali:
```bash
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-multipart==0.0.6 \
  opencv-python==4.8.1.78 opencv-contrib-python==4.8.1.78 \
  numpy==1.26.2 scikit-image==0.22.0 scipy==1.11.4 \
  scikit-learn==1.3.2 pydantic==2.5.0 python-dotenv==1.0.0 pyyaml==6.0.1
```

## Opzione 1: Test Diretto con Script

### Esegui il Test

```bash
cd backend
python test_video_analysis.py test_videos/test_slalom.mp4 "Rebe"
```

Sostituisci `"Rebe"` con il nome del pattinatore (opzionale).

### Output

Lo script stamperà:
- Informazioni sul video
- Setup campo e coni rilevati
- Statistiche passi
- Utilizzo delle file di coni
- Penalità (se rilevate)
- Valutazione dettagliata
- **Voto finale (0-10)**

Il report sarà anche salvato in formato JSON nella cartella `backend/output/`.

## Opzione 2: Test con API (Full Stack)

### 1. Avvia il Backend

Terminal 1:
```bash
cd backend
python -m app.main
```

Il backend sarà disponibile su http://localhost:8000

### 2. Avvia il Frontend

Terminal 2:
```bash
cd frontend
npm install
npm start
```

Il browser si aprirà automaticamente su http://localhost:3000

### 3. Usa l'Interfaccia Web

1. Clicca su "Seleziona file" e carica il video
2. Inserisci il nome del pattinatore (opzionale)
3. Clicca "Carica e Analizza"
4. Attendi l'elaborazione
5. Visualizza il report dettagliato

## Cosa Aspettarsi (MVP Attuale)

### ✅ Funzionalità Implementate:
- Upload e processing video
- Rilevamento posizioni coni (basato su colore)
- Tracking del pattinatore
- Conteggio attraversamenti base
- Report con punteggio finale

### ⚠️ Limitazioni Attuali:

1. **Riconoscimento Passi Generico**
   - Attualmente non distingue passi specifici (crazy, nelson, etc.)
   - Rileva solo "attraversamenti generici"
   - Servirà configurare i pattern di ogni passo

2. **Calibrazione Colori Coni**
   - I colori nel config (`config/scoring_config.yaml`) sono placeholder
   - Potrebbero non corrispondere ai colori reali del video
   - Potrebbe non rilevare correttamente i coni

3. **Algoritmo di Attraversamento**
   - L'algoritmo di rilevamento attraversamenti è molto base
   - Potrebbe non contare correttamente tutti i passaggi

4. **Rilevamento Coni Spostati**
   - Implementato in modo base
   - Potrebbe non essere molto preciso

## Problemi Comuni e Soluzioni

### Problema: "Cannot open video"
**Soluzione:** Verifica che il path del video sia corretto e che il file esista.

### Problema: "Tracking failed"
**Soluzione:** Il video potrebbe avere sfondo troppo complesso o illuminazione difficile.
- Prova con un video con sfondo più uniforme
- Assicurati che il pattinatore sia ben visibile

### Problema: "Nessun cono rilevato"
**Soluzione:** I colori configurati non corrispondono a quelli reali.
1. Apri `config/scoring_config.yaml`
2. Modifica i valori in `color_ranges` in `cone_detector.py`
3. Potrebbe servire una calibrazione manuale

### Problema: Punteggi strani o irrealistici
**Soluzione:** È normale nel MVP! Gli algoritmi sono base e necessitano:
- Calibrazione dei colori
- Definizione dei passi specifici
- Raffinamento della logica di scoring

## Debug e Logging

Per vedere i log dettagliati durante l'analisi:

```bash
export LOG_LEVEL=DEBUG
python test_video_analysis.py test_videos/test_slalom.mp4
```

## Prossimi Passi Dopo il Test

Dopo aver testato, sarà utile:

1. **Feedback sui Risultati**
   - Il video viene processato?
   - I coni vengono rilevati?
   - Il tracking funziona?
   - I risultati hanno senso?

2. **Calibrazione Colori**
   - Quali sono i colori reali dei coni nel video?
   - Serve modificare i range HSV in `cone_detector.py`

3. **Definizione Passi**
   - Iniziare a configurare i passi specifici
   - Vedere `docs/TRICKS_CONFIGURATION.md`

4. **Raffinamento Algoritmi**
   - Migliorare detection e tracking
   - Implementare riconoscimento pattern

## Supporto

Se hai problemi o domande durante il test:

1. Controlla i log per errori dettagliati
2. Verifica che tutte le dipendenze siano installate
3. Prova prima con lo script di test (più semplice)
4. Condividi eventuali errori per ricevere aiuto

## File di Output

Dopo l'analisi troverai:
- `backend/output/report_*.json` - Report in formato JSON
- Log nella console durante l'esecuzione

Il report JSON contiene tutti i dati strutturati e può essere usato per analisi successive o integrazione con altri tool.

---

Buon test! 🛼
