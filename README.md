# Inline Slalom Scoring App

Applicazione web per l'analisi automatica di esibizioni di pattinaggio inline freestyle slalom.

## Caratteristiche

- 📹 Upload video di esibizioni
- 🎯 Rilevamento automatico coni (3 file con colori diversi)
- 👤 Tracking del pattinatore
- 📊 Analisi passi e attraversamenti
- ⚠️ Rilevamento penalità (coni spostati)
- 🏆 Sistema di scoring configurabile

## Setup Campo Gara

- **Fila 1**: 20 coni distanti 50cm (colore specifico)
- **Fila 2**: 20 coni distanti 80cm (colore specifico)
- **Fila 3**: 14 coni distanti 120cm (colore specifico)

## Struttura Progetto

```
/backend         - API FastAPI + analisi video OpenCV
/frontend        - Interfaccia web React
/config          - Configurazione passi e punteggi
/docs            - Documentazione
```

## Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Tecnologie

- **Backend**: Python, FastAPI, OpenCV, NumPy
- **Frontend**: React, TailwindCSS
- **Computer Vision**: OpenCV, scikit-image

## Roadmap

### MVP (Fase 1)
- [x] Setup progetto
- [ ] Detection coni per colore
- [ ] Tracking base pattinatore
- [ ] Conta attraversamenti per fila
- [ ] Report base con statistiche

### Fase 2
- [ ] Riconoscimento passi specifici
- [ ] Sistema di scoring avanzato
- [ ] Rilevamento coni spostati
- [ ] Dashboard con replay video

### Fase 3
- [ ] ML per riconoscimento pattern
- [ ] Multi-camera support
- [ ] Database esibizioni
- [ ] Comparazione performance
