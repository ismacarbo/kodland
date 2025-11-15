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
app.config["SECRET_KEY"] = "ciao_mondo_12345"
app.config["DATABASE"] = "quiz.db"


OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "ciao_mondo_12345")

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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
