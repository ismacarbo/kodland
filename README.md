
README - Kodland – Python Game (PgZero)

Questo repository contiene il progetto **Python base** (un piccolo roguelike top-down su griglia fatto con PgZero).
A breve verrà aggiunta anche la cartella **Python pro** con estensioni avanzate.

──────────────────────────────────────────────────────────────────────────────

STRUTTURA

kodland/
├─ python base/
│  ├─ main.py
│  ├─ images/
│  ├─ sounds/
│  └─ music/
├─ requirements.txt
└─ README.md

Nota: la cartella si chiama "python base" (con uno spazio). Nei comandi del terminale usa le virgolette: cd "python base".

──────────────────────────────────────────────────────────────────────────────

REQUISITI

- Python 3.9+
- Solo librerie consentite dal compito:
  • PgZero (usa Pygame internamente)
  • math, random (standard library)
  • Eccezione: import della classe Rect da pygame (permesso)
- Installa i pacchetti da requirements.txt oppure manualmente pgzero.

──────────────────────────────────────────────────────────────────────────────

SETUP RAPIDO (venv)

Dalla root del progetto (kodland/):

macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt    # oppure: pip install pgzero

Windows (PowerShell)
    py -3 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt    # oppure: pip install pgzero

──────────────────────────────────────────────────────────────────────────────

AVVIO DEL GIOCO

    cd "python base"
    pgzrun main.py
    # Se pgzrun non fosse nel PATH del venv:
    # python -m pygamezero main.py

──────────────────────────────────────────────────────────────────────────────

CONTENUTI / ASSET

Usiamo asset Kenney (https://kenney.nl/) – vedi License.txt del pacchetto (generalmente CC0).

Immagini attese (python base/images/)
- Player (idle + walk):
  - hero_idle_0.png ... hero_idle_3.png
  - hero_walk_0.png ... hero_walk_3.png
- Nemico (idle + walk):
  - slime_idle_0.png ...
  - slime_walk_0.png ...

Suggerimento: scegli i frame dal pack Kenney (Players/Tiles e Enemies/Tiles) e rinominali con questi nomi.

Suoni (python base/sounds/)
- step.ogg  → es. move-a.ogg rinominato
- hit.ogg   → es. hurt-a.ogg rinominato
- click.ogg → es. select-a.ogg rinominato

Musica (python base/music/)
- theme.ogg (loop; puoi usare un “Music Loops” Kenney)

──────────────────────────────────────────────────────────────────────────────

COME SI GIOCA

Menu principale
- Avvia partita: crea il livello, il player e 4 nemici.
- Attiva/Disattiva musica e suoni: toggle immediato.
- Slider volume: trascina il knob (0–100%). Influenza musica e SFX.
- Esci: chiude l’app.

Controlli in gioco
- WASD / Frecce: muovi il personaggio di 1 cella con animazione fluida.
- ESC: torna al menu.

Meccaniche
- I nemici si muovono e tendono a inseguirti.
- Contatto con un nemico → perdi 1 cuore (SFX).
- A 0 cuori → Game Over; click per rientrare nel menu.

──────────────────────────────────────────────────────────────────────────────

CONSEGNA / CONDIVISIONE

Consigliato: non includere .venv/ nell’archivio; basta requirements.txt.
Per creare uno ZIP minimale:

    cd ~/Desktop
    zip -r kodland_project.zip kodland -x "kodland/.venv/*"

Carica lo ZIP o la cartella su Google Drive/Dropbox e condividi il link.

──────────────────────────────────────────────────────────────────────────────

CONFORMITÀ AI REQUISITI DEL COMPITO

- Librerie: PgZero, math, random, Rect da pygame → OK
- Genere: roguelike top-down a griglia con movimento fluido → OK
- Menu con 3 pulsanti richiesti → OK
- Musica + SFX (toggle + slider volume) → OK
- Nemici che si muovono e minacciano (danni) → OK
- Classi con funzioni di movimento e animazione; sprite animati idle e walk → OK
- Nomi chiari in inglese (PEP8-ish) → OK

──────────────────────────────────────────────────────────────────────────────

ROADMAP

- Python base (completo): gioco funzionante come sopra.
- Python pro (in arrivo): idee
  • Tileset grafico per la mappa (blit texture Kenney)
  • Nuovi tipi di nemici / pattern
  • Pickup, punteggio, livelli multipli
  • Salvataggi, pausa, opzioni separate Musica/SFX

──────────────────────────────────────────────────────────────────────────────

LICENZE

- Codice © 2024 [Il tuo nome].
- Asset grafici/audio: Kenney – vedi License.txt del pack (di norma CC0 / pubblico dominio).