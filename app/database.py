import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "reservas.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL,
            telefono  TEXT NOT NULL,
            email     TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS tecnicos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            especialidad TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reservas (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id          INTEGER NOT NULL REFERENCES clientes(id),
            tecnico_id          INTEGER NOT NULL REFERENCES tecnicos(id),
            fecha_hora          TEXT NOT NULL,
            direccion           TEXT NOT NULL,
            descripcion         TEXT NOT NULL,
            estado              TEXT NOT NULL DEFAULT 'pendiente',
            motivo_cancelacion  TEXT
        );
    """)
    conn.commit()
    conn.close()
