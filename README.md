# README — Kodland · Python Game (PgZero)

Questo repository contiene il progetto **Python base**: un piccolo roguelike top‑down su griglia realizzato con **PgZero**.  
In futuro sarà aggiunta anche una cartella **Python pro** con estensioni avanzate.

---

## Struttura

```
kodland/
├─ pythonBase/
│  ├─ main.py
│  ├─ images/
│  ├─ sounds/
│  └─ music/
├─ requirements.txt
└─ README.md
```

---

## Requisiti

- **Python 3.9+**
- Librerie consentite dal compito:
  - **PgZero**
  - `math`, `random` (standard library)
  - Eccezione: import della **classe `Rect`** da `pygame` (permesso)
- Installa i pacchetti con `requirements.txt` oppure manualmente `pgzero`.

---

## Setup rapido (venv)

Esegui dalla **root** del progetto `kodland/`.

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt    # oppure: pip install pgzero
```

### Windows (PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt    # oppure: pip install pgzero
```

---

## Avvio del gioco

```bash
cd "python base"
pgzrun main.py
# Se pgzrun non fosse nel PATH del venv:
# python -m pygamezero main.py
```

---

## Asset

Usiamo asset **Kenney** (vedi `License.txt` del pack — generalmente CC0).

**Immagini attese** (`python base/images/`)
- Player (idle + walk): `hero_idle_0..3.png`, `hero_walk_0..3.png`
- Nemico (idle + walk): `slime_idle_0..*.png`, `slime_walk_0..*.png`

> Puoi scegliere i frame da `Players/Tiles` e `Enemies/Tiles` dei pacchetti Kenney e **rinominarli** con questi nomi.

**Suoni** (`python base/sounds/`)
- `step.ogg`  → es. `move-a.ogg` rinominato
- `hit.ogg`   → es. `hurt-a.ogg` rinominato
- `click.ogg` → es. `select-a.ogg` rinominato

**Musica** (`python base/music/`)
- `theme.ogg` (loop di sottofondo; va bene anche un Music Loops Kenney)

---

## Come si gioca

- **Menu principale**
  - **Avvia partita**: crea il livello, il player e 4 nemici.
  - **Attiva/Disattiva musica e suoni**: toggle immediato.
  - **Slider volume**: trascina il knob (0–100%). Influenza musica e SFX.
  - **Esci**: chiude l’applicazione.
- **Controlli in gioco**
  - **WASD / Frecce**: muovi il personaggio di 1 cella con animazione fluida.
  - **ESC**: torna al menu.
- **Meccaniche**
  - I nemici si muovono e tendono a inseguirti.
  - Contatto con un nemico → perdi 1 cuore (SFX).
  - A 0 cuori → **Game Over**; click per tornare al menu.

---

## Consegna / Condivisione

- Consigliato **non includere** la cartella `.venv/` nell’archivio; basta `requirements.txt`.
- ZIP di esempio (da `~/Desktop`):
```bash
zip -r kodland_project.zip kodland -x "kodland/.venv/*"
```
- Carica lo ZIP o la cartella su Google Drive/Dropbox e condividi il link.

---

## Conformità ai requisiti del compito

- Librerie: **PgZero**, `math`, `random`, `Rect` da `pygame` → ✅  
- Genere: roguelike top‑down a **griglia** con movimento **fluido** → ✅  
- Menu con 3 pulsanti richiesti → ✅  
- **Musica + SFX** (toggle + slider volume) → ✅  
- **Nemici** che si muovono e **minacciano** (danni a contatto) → ✅  
- **Classi** con funzioni di **movimento** e **animazione**; sprite **idle** e **walk** → ✅  
- Nomi chiari in inglese (PEP8-ish) → ✅

---

## Roadmap

- **Python base** (completo): gioco funzionante come sopra.
- **Python pro** (in arrivo):
  - Tileset grafico per la mappa (blit texture Kenney)
  - Tipi di nemici/pattern aggiuntivi
  - Pickup, punteggio, livelli multipli
  - Salvataggi, pausa, opzioni separate Musica/SFX

---

## Licenze

- Codice © 2024 _[Il tuo nome]_.
- Asset grafici/audio: **Kenney** — consulta `License.txt` del pack (di norma CC0 / pubblico dominio).