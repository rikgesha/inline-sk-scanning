# Configurazione Passi (Tricks)

Questo documento spiega come configurare il sistema per riconoscere i passi specifici del freestyle slalom.

## Stato Attuale

L'MVP attuale rileva **attraversamenti generici** delle file di coni, ma non riconosce ancora passi specifici come:
- Crazy
- Nelson
- Special
- Mabrouk
- Sun
- Coffin
- etc.

## Come Configurare i Passi

### 1. Definire le Caratteristiche del Passo

Per ogni passo, dobbiamo definire:

```yaml
trick_name:
  name: "Nome Visualizzato"
  difficulty: 1-10  # Difficoltà del passo
  min_cones: 4      # Minimo coni richiesti
  base_points: 1.5  # Punti base assegnati
  description: "Descrizione del passo"

  # Caratteristiche per il riconoscimento (DA DEFINIRE)
  recognition:
    pattern: "tipo di movimento"
    direction: "avanti/indietro"
    foot_position: "parallelo/incrociato"
    speed_range: [min, max]  # Velocità tipica
    body_movement: "descrizione movimento corpo"
```

### 2. Pattern di Riconoscimento

Per implementare il riconoscimento automatico, avremo bisogno di:

#### Dati Necessari per Ogni Passo:

1. **Movimento dei piedi**
   - Paralleli vs incrociati
   - Alterni vs simultanei
   - Direzione (avanti, indietro, laterale)

2. **Traiettoria**
   - Linea retta vs curva
   - Serpentina vs zigzag
   - Angolo di attraversamento

3. **Velocità**
   - Range di velocità tipica
   - Accelerazione/decelerazione

4. **Posizione del corpo**
   - Inclinazione
   - Rotazione
   - Altezza (squat vs in piedi)

5. **Sequenza**
   - Numero di movimenti per cono
   - Ritmo/cadenza
   - Simmetria

### 3. Esempio di Configurazione Completa

```yaml
crazy:
  name: "Crazy"
  difficulty: 3
  min_cones: 4
  base_points: 1.5
  description: "Passo base con piedi paralleli"

  recognition:
    pattern: "serpentina"
    direction: "avanti"
    foot_position: "parallelo"
    crossings_per_cone: 1
    speed_range: [0.5, 2.0]  # m/s
    trajectory_angle: [30, 60]  # gradi rispetto alla fila
    body_movement: "inclinazione laterale alternata"

nelson:
  name: "Nelson"
  difficulty: 4
  min_cones: 4
  base_points: 2.0
  description: "Passo con piedi incrociati"

  recognition:
    pattern: "serpentina"
    direction: "avanti"
    foot_position: "incrociato"
    crossings_per_cone: 1
    speed_range: [0.3, 1.5]
    trajectory_angle: [40, 70]
    body_movement: "rotazione bacino"
```

## Approccio Graduale per l'Implementazione

### Fase 1: Riconoscimento Base (ATTUALE)
- ✅ Rileva attraversamenti delle file
- ✅ Conta coni attraversati
- ✅ Valida passi (>= 4 coni)

### Fase 2: Classificazione per Caratteristiche Base
- Distinguere avanti vs indietro
- Riconoscere quale fila viene usata
- Calcolare velocità media

### Fase 3: Pattern Recognition con Computer Vision
- Analisi traiettoria dettagliata
- Rilevamento posizione piedi (se visibili)
- Classificazione con algoritmi ML

### Fase 4: Machine Learning
- Training su dataset di video etichettati
- Classificazione automatica passi complessi
- Confidence score per ogni detection

## Come Procedere

### Step 1: Raccolta Informazioni
**Tu dovrai fornire per ogni passo:**

1. Nome del passo
2. Difficoltà (1-10)
3. Punti che dovrebbe valere
4. Descrizione del movimento
5. Come distinguerlo dagli altri passi
6. Numero minimo di coni richiesti

### Step 2: Video di Riferimento
Sarebbe utile avere:
- Video di esempio per ogni passo
- Esecuzioni sia corrette che scorrette
- Diverse velocità di esecuzione

### Step 3: Implementazione Progressiva
1. Aggiungeremo i passi nella configurazione
2. Implementeremo riconoscimento base (direzione, fila usata)
3. Raffineremo con pattern recognition avanzato
4. Testeremo e calibreremo

## Template da Compilare

Per ogni passo che vuoi aggiungere, compila questo template:

```
NOME PASSO: _______________

DIFFICOLTÀ (1-10): ___

PUNTI BASE: ___

DESCRIZIONE:
_______________________________________________
_______________________________________________

CARATTERISTICHE DISTINTIVE:
- Direzione: (avanti/indietro/laterale)
- Piedi: (paralleli/incrociati)
- Movimento: ______________________________
- Fila preferita: (50cm/80cm/120cm/qualsiasi)
- Velocità: (lento/medio/veloce)
- Minimo coni: ___

NOTE AGGIUNTIVE:
_______________________________________________
_______________________________________________
```

## Esempi di Passi Comuni

Questi sono placeholder - dovrai fornire le informazioni reali:

1. **Crazy**: Base, avanti, paralleli
2. **Nelson**: Incrociati, rotazione bacino
3. **Special**: Criss-cross, piedi alternati
4. **Mabrouk**: One foot, equilibrio
5. **Sun**: Rotazione completa
6. **Coffin**: Squat basso
7. **Eagle**: Apertura laterale
8. **X**: Pattern incrociato
9. **Wheeling**: Su una ruota
10. **Chapchap**: Veloce, doppio passaggio

## Domande per Te

Prima di implementare il riconoscimento specifico, ho bisogno di sapere:

1. Quali sono i 10-15 passi più comuni nelle competizioni?
2. Quali caratteristiche sono più importanti per distinguerli?
3. C'è una "gerarchia" di difficoltà ufficiale?
4. Come vengono valutati nelle gare reali?
5. Ci sono combinazioni di passi che valgono bonus?

## Prossimi Passi

Una volta che mi avrai fornito le informazioni sui passi:

1. Aggiorneremo `config/scoring_config.yaml`
2. Implementeremo la logica di riconoscimento in `video_analyzer.py`
3. Creeremo un sistema di pattern matching
4. Testeremo con i tuoi video
5. Raffineremo in base ai risultati
