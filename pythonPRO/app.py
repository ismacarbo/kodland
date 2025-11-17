import os
import sqlite3
import random
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
import requests
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "cambia-questa-stringa-super-segreta"
app.config["DATABASE"] = "quiz.db"


OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "INSERISCI_LA_TUA_API_KEY_QUI")

def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea le tabelle se non esistono e inserisce alcune domande di esempio."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Tabella utenti
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nickname TEXT UNIQUE NOT NULL,
            total_score INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );
        """
    )

    # Tabella domande
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            correct_option INTEGER NOT NULL
        );
        """
    )

    # Inseriamo qualche domanda solo se la tabella è vuota
    cur.execute("SELECT COUNT(*) AS c FROM questions;")
    count = cur.fetchone()["c"]
    if count == 0:
        questions = [
            (
                "Quale libreria Python è più usata per il machine learning classico?",
                "NumPy",
                "pandas",
                "scikit-learn",
                "matplotlib",
                3,
            ),
            (
                "Quale libreria è spesso usata per reti neurali profonde in Python?",
                "TensorFlow",
                "scikit-image",
                "Flask",
                "Requests",
                1,
            ),
            (
                "Cosa significa NLP?",
                "Neural Linear Programming",
                "Natural Language Processing",
                "Natural Logic Programming",
                "Network Learning Protocol",
                2,
            ),
            (
                "Quale funzione di Python stampa un messaggio sullo schermo?",
                "echo()",
                "write()",
                "print()",
                "log()",
                3,
            ),
        ]

        cur.executemany(
            """
            INSERT INTO questions (text, option1, option2, option3, option4, correct_option)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            questions,
        )

    conn.commit()
    conn.close()


def current_user():
    """Ritorna l'utente loggato come record del database (oppure None)."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?;", (user_id,)
    ).fetchone()
    conn.close()
    return user


def login_required(view_func):
    """Decorator semplice per proteggere le pagine che richiedono login."""
    from functools import wraps

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Devi effettuare il login per accedere a questa pagina.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped

def get_weather_forecast(city_name):
    """
    Ritorna una lista di 3 giorni di previsioni per la città scelta.
    Ogni elemento è un dict: {date, weekday, temp_min, temp_max, description}
    Usa l'API 5-day/3-hour di OpenWeatherMap.
    """
    if not city_name or OPENWEATHER_API_KEY.startswith("INSERISCI_"):
        return None, "API key mancante o città non valida."

    try:
        url = (
            "https://api.openweathermap.org/data/2.5/forecast"
            f"?q={city_name}&units=metric&lang=it&appid={OPENWEATHER_API_KEY}"
        )
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None, "Errore nel recupero dei dati meteo."

        data = resp.json()
        if "list" not in data:
            return None, "Formato della risposta meteo non valido."

        # Raggruppiamo per data (YYYY-MM-DD)
        daily = {}
        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            date_str = dt.date().isoformat()
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"]

            if date_str not in daily:
                daily[date_str] = {
                    "temps": [temp],
                    "descriptions": [desc],
                }
            else:
                daily[date_str]["temps"].append(temp)
                daily[date_str]["descriptions"].append(desc)

        # Prendiamo solo i prossimi 3 giorni
        result = []
        for date_str in sorted(daily.keys())[:3]:
            temps = daily[date_str]["temps"]
            descriptions = daily[date_str]["descriptions"]
            temp_min = round(min(temps), 1)
            temp_max = round(max(temps), 1)
            # descrizione più frequente
            description = max(set(descriptions), key=descriptions.count)

            dt_date = datetime.fromisoformat(date_str)
            weekday = dt_date.strftime("%A")  # es. Monday

            result.append(
                {
                    "date": dt_date.strftime("%d/%m/%Y"),
                    "weekday": weekday,
                    "temp_min": temp_min,
                    "temp_max": temp_max,
                    "description": description,
                }
            )

        return result, None

    except Exception:
        return None, "Si è verificato un errore durante la richiesta meteo."

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Home page:
    - campo per il nome della città
    - tabella con previsioni per 3 giorni
    - data odierna con nome del giorno
    """
    forecast = None
    error = None
    city = ""

    today = datetime.now()
    today_str = today.strftime("%d/%m/%Y")
    weekday_str = today.strftime("%A")

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        forecast, error = get_weather_forecast(city)

    return render_template(
        "home.html",
        city=city,
        forecast=forecast,
        error=error,
        today=today_str,
        weekday=today_str + " - " + weekday_str,
        user=current_user(),
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Pagina di registrazione:
    - login (unico)
    - password
    - conferma password
    - nickname (unico)
    """
    if request.method == "POST":
        login_name = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        nickname = request.form.get("nickname", "").strip()

        if not login_name or not password or not nickname:
            flash("Compila tutti i campi.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Le password non coincidono.", "danger")
            return redirect(url_for("register"))

        conn = get_db_connection()
        cur = conn.cursor()

        # Verifica unicità login e nickname
        cur.execute("SELECT id FROM users WHERE login = ?;", (login_name,))
        if cur.fetchone():
            flash("Questo login è già in uso.", "danger")
            conn.close()
            return redirect(url_for("register"))

        cur.execute("SELECT id FROM users WHERE nickname = ?;", (nickname,))
        if cur.fetchone():
            flash("Questo nickname è già in uso.", "danger")
            conn.close()
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        created_at = datetime.now().isoformat(timespec="seconds")

        cur.execute(
            """
            INSERT INTO users (login, password_hash, nickname, total_score, created_at)
            VALUES (?, ?, ?, 0, ?);
            """,
            (login_name, password_hash, nickname, created_at),
        )
        conn.commit()
        user_id = cur.lastrowid
        conn.close()

        # login automatico dopo registrazione
        session["user_id"] = user_id
        flash("Registrazione completata. Benvenuto nel quiz!", "success")
        return redirect(url_for("quiz"))

    return render_template("register.html", user=current_user())


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Pagina di login: login + password
    """
    if request.method == "POST":
        login_name = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE login = ?;", (login_name,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Login effettuato con successo.", "success")
            return redirect(url_for("quiz"))
        else:
            flash("Login o password errati.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", user=current_user())


@app.route("/logout")
def logout():
    """
    Logout: visibile solo quando l'utente è connesso.
    """
    session.pop("user_id", None)
    flash("Sei stato disconnesso.", "info")
    return redirect(url_for("home"))


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    """
    Pagina del quiz:
    - mostra punteggio totale del giocatore
    - mostra una domanda alla volta, in ordine casuale
    - 4 opzioni di risposta
    - dopo la risposta, aggiorna il punteggio e mostra una nuova domanda
    """
    user = current_user()

    conn = get_db_connection()
    # numero totale di domande
    count_row = conn.execute("SELECT COUNT(*) AS c FROM questions;").fetchone()
    total_questions = count_row["c"]

    if total_questions == 0:
        conn.close()
        flash("Non ci sono domande nel database.", "warning")
        return render_template("quiz.html", user=user, question=None)

    if request.method == "POST":
        question_id = int(request.form.get("question_id"))
        selected_option = int(request.form.get("option"))

        question = conn.execute(
            "SELECT * FROM questions WHERE id = ?;", (question_id,)
        ).fetchone()

        if question and selected_option == question["correct_option"]:
            # aggiorna punteggio utente
            conn.execute(
                "UPDATE users SET total_score = total_score + 1 WHERE id = ?;",
                (user["id"],),
            )
            conn.commit()
            flash("Risposta corretta! +1 punto.", "success")
        else:
            flash("Risposta sbagliata, ritenta!", "danger")

        # ricarichiamo utente aggiornato
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?;", (user["id"],)
        ).fetchone()

    # scegliamo una domanda casuale
    question_ids = [
        row["id"] for row in conn.execute("SELECT id FROM questions;").fetchall()
    ]
    random_id = random.choice(question_ids)
    question = conn.execute(
        "SELECT * FROM questions WHERE id = ?;", (random_id,)
    ).fetchone()
    conn.close()

    return render_template("quiz.html", user=user, question=question)


@app.route("/leaderboard")
def leaderboard():
    """
    Classifica del quiz: mostra nickname e punteggi.
    """
    conn = get_db_connection()
    players = conn.execute(
        "SELECT nickname, total_score FROM users ORDER BY total_score DESC, id ASC;"
    ).fetchall()
    conn.close()
    return render_template("leaderboard.html", players=players, user=current_user())


if __name__ == "__main__":
    # Crea il database se necessario
    init_db()
    app.run(debug=True)
