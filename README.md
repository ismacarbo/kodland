# README — Kodland · Python Base + Python Pro

Questo repository contiene due progetti del percorso Kodland:

1. **Python Base** → un piccolo gioco roguelike top-down su griglia, realizzato con PgZero.
2. **Python Pro** → un sito web completo realizzato con Flask, con meteo, registrazione, login, quiz e classifica.

Entrambi i progetti rispettano pienamente i requisiti richiesti dalle consegne.

------------------------------------------------------------
## STRUTTURA DEL REPOSITORY
------------------------------------------------------------

kodland/
├─ pythonBase/
│  ├─ main.py
│  ├─ images/
│  ├─ sounds/
│  └─ music/
│
├─ pythonPRO/
│  ├─ app.py
│  ├─ quiz.db (generato automaticamente)
│  ├─ templates/
│  │   ├─ base.html
│  │   ├─ home.html
│  │   ├─ login.html
│  │   ├─ register.html
│  │   ├─ quiz.html
│  │   └─ leaderboard.html
│  ├─ static/
│  │   └─ style.css
│  └─ requirements.txt
│
└─ README.md (o README.txt — questo file)

------------------------------------------------------------
# PYTHON BASE — ROGUELIKE PGZERO
------------------------------------------------------------

Il progetto Python base è un gioco top-down su griglia con animazioni, nemici, musica e menu.

### REQUISITI  
- Python 3.9+
- Librerie:
  - PgZero
  - math, random (standard library)
  - pygame.Rect (permesso)
- Installazione tramite `pip install -r requirements.txt`

### AVVIO (dalla cartella pythonBase/)
pgzrun main.py
(se pgzrun non è nel PATH → python -m pygamezero main.py)

### ASSET
Usiamo asset Kenney (CC0).
- images/: sprite per player e nemici (idle + walk)
- sounds/: step, hit, click
- music/: theme.ogg

### COME SI GIOCA
- Menu:
  - Avvia Partita
  - Audio ON/OFF
  - Slider volume
  - Esci
- In gioco:
  - WASD / frecce per muoverti
  - Nemici che inseguono
  - Collisioni → perdi cuori
  - Game Over → ritorno al menu

### CONFORMITÀ ALLA CONSEGNA
✔ Librerie consentite  
✔ Roguelike top-down su griglia  
✔ Movimento fluido + animazioni  
✔ Nemici pericolosi  
✔ Menu completo  
✔ Audio & slider volume  
✔ Sprite idle/walk  
✔ Classi e codice ben strutturato  

------------------------------------------------------------
# PYTHON PRO — SITO WEB FLASK (Meteo + Quiz)
------------------------------------------------------------

Il progetto Python PRO è un'applicazione Flask con:

- Home con **meteo 3 giorni**
- Registrazione con controllo login & nickname unici
- Login / logout
- Quiz con domande casuali e punteggio salvato
- Classifica globale
- Header dinamico (voci visibili in base al login)
- Footer col nome dello sviluppatore
- Hosting compatibile con PythonAnywhere

### REQUISITI  
- Python 3.10+
- Flask
- Requests
- Werkzeug (incluso in Flask)

### INSTALLAZIONE (nella cartella pythonPRO/)
python3 -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  

Imposta la tua API key meteo:
export OPENWEATHER_API_KEY="LA_TUA_API_KEY"

### AVVIO
python app.py  
→ http://127.0.0.1:5000

------------------------------------------------------------
# STRUTTURA PAGINE (Python PRO)
------------------------------------------------------------

### HOME PAGE (/)  
✔ Campo città  
✔ Meteo 3 giorni  
✔ Data + nome del giorno  
✔ Tabella previsioni  
✔ Widget meteo tramite API esterna  

### REGISTRAZIONE (/register)
✔ Login unico  
✔ Password + conferma  
✔ Nickname unico  
✔ Login automatico dopo registrazione  

### LOGIN (/login)
✔ Autenticazione login/password  
✔ Errori gestiti  

### LOGOUT (/logout)
✔ Disponibile solo se loggato  
✔ Sessione pulita  

### QUIZ (/quiz)
✔ Mostra punteggio utente  
✔ Domanda casuale ogni volta  
✔ 4 opzioni  
✔ Risulta subito corretto/sbagliato  
✔ +1 punto per risposta corretta  
✔ Domande infinite  

### CLASSIFICA (/leaderboard)
✔ Nickname + punteggio  
✔ Ordinamento corretto  

### HEADER (nav)
✔ Home  
✔ Registrazione (se non loggato)  
✔ Login (se non loggato)  
✔ Logout (se loggato)  
✔ Quiz (se loggato)  
✔ Classifica (se loggato)

### FOOTER
✔ Nome dello sviluppatore  
✔ Footer fisso in fondo alla pagina  

------------------------------------------------------------
# HOSTING (Python PRO)
------------------------------------------------------------

Completamente compatibile con **PythonAnywhere**:
- Copiare la cartella pythonPRO/
- Configurare WSGI
- Impostare variabile d’ambiente OPENWEATHER_API_KEY
- Assicurarsi che `templates/` e `static/` siano nella stessa directory di app.py

------------------------------------------------------------
# ZIP & CONSEGNA
------------------------------------------------------------

Evita di includere `.venv/`.
Comando consigliato:

zip -r kodland_project.zip kodland -x "kodland/.venv/*"

------------------------------------------------------------
# LICENZE
------------------------------------------------------------

Codice © 2025 Ismaele.  
Asset grafici/audio Kenney (CC0 / pubblico dominio).  

------------------------------------------------------------
# ROADMAP
------------------------------------------------------------

### Python Base
- Gioco completo e già conforme.

### Python Pro
Possibili estensioni future:
- Icone meteo
- Domande personalizzabili da pannello admin
- Sistema a livelli del quiz
- Profili utente avanzati
