from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db, init_db
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = "reservas-tecnicas-2026"


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def valid_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def valid_phone(phone):
    return bool(re.match(r"^\+?[\d\s\-]{7,15}$", phone))


def now_str():
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


# ──────────────────────────────────────────────
# Index – reservas futuras
# ──────────────────────────────────────────────

@app.route("/")
def index():
    db = get_db()
    reservas = db.execute("""
        SELECT r.id, c.nombre AS cliente, t.nombre AS tecnico,
               t.especialidad, r.fecha_hora, r.direccion, r.descripcion, r.estado
        FROM   reservas r
        JOIN   clientes c ON c.id = r.cliente_id
        JOIN   tecnicos t ON t.id = r.tecnico_id
        WHERE  r.estado != 'cancelada'
          AND  r.fecha_hora >= ?
        ORDER  BY r.fecha_hora ASC
    """, (now_str(),)).fetchall()
    total_clientes  = db.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    total_tecnicos  = db.execute("SELECT COUNT(*) FROM tecnicos").fetchone()[0]
    total_canceladas = db.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'cancelada'").fetchone()[0]
    db.close()
    return render_template("index.html", reservas=reservas,
                           total_clientes=total_clientes,
                           total_tecnicos=total_tecnicos,
                           total_canceladas=total_canceladas)


# ──────────────────────────────────────────────
# Clientes
# ──────────────────────────────────────────────

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    db = get_db()

    if request.method == "POST":
        nombre   = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        email    = request.form.get("email", "").strip().lower()

        errors = []
        if not nombre:
            errors.append("El nombre es obligatorio.")
        if not telefono:
            errors.append("El teléfono es obligatorio.")
        elif not valid_phone(telefono):
            errors.append("El teléfono solo puede contener dígitos, espacios, guiones o '+'.")
        if not email:
            errors.append("El email es obligatorio.")
        elif not valid_email(email):
            errors.append("El email no tiene un formato válido.")

        if not errors:
            existing = db.execute("SELECT id FROM clientes WHERE email = ?", (email,)).fetchone()
            if existing:
                errors.append("Ya existe un cliente registrado con ese email.")

        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.execute(
                "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
                (nombre, telefono, email)
            )
            db.commit()
            flash("Cliente registrado correctamente.", "success")
            db.close()
            return redirect(url_for("clientes"))

    lista = db.execute("SELECT * FROM clientes ORDER BY nombre ASC").fetchall()
    db.close()
    return render_template("clientes.html", clientes=lista)


# ──────────────────────────────────────────────
# Técnicos
# ──────────────────────────────────────────────

@app.route("/tecnicos", methods=["GET", "POST"])
def tecnicos():
    db = get_db()

    if request.method == "POST":
        nombre       = request.form.get("nombre", "").strip()
        especialidad = request.form.get("especialidad", "").strip()

        errors = []
        if not nombre:
            errors.append("El nombre es obligatorio.")
        if not especialidad:
            errors.append("La especialidad es obligatoria.")

        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.execute(
                "INSERT INTO tecnicos (nombre, especialidad) VALUES (?, ?)",
                (nombre, especialidad)
            )
            db.commit()
            flash("Técnico registrado correctamente.", "success")
            db.close()
            return redirect(url_for("tecnicos"))

    lista = db.execute("SELECT * FROM tecnicos ORDER BY nombre ASC").fetchall()
    db.close()
    return render_template("tecnicos.html", tecnicos=lista)


# ──────────────────────────────────────────────
# Reservas – crear
# ──────────────────────────────────────────────

@app.route("/reservas/nueva", methods=["GET", "POST"])
def nueva_reserva():
    db = get_db()

    if request.method == "POST":
        cliente_id  = request.form.get("cliente_id", "").strip()
        tecnico_id  = request.form.get("tecnico_id", "").strip()
        fecha_hora  = request.form.get("fecha_hora", "").strip()
        direccion   = request.form.get("direccion", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        errors = []
        if not cliente_id:
            errors.append("Debe seleccionar un cliente.")
        if not tecnico_id:
            errors.append("Debe seleccionar un técnico.")
        if not fecha_hora:
            errors.append("La fecha y hora son obligatorias.")
        elif fecha_hora <= now_str():
            errors.append("La fecha y hora deben ser futuras.")
        if not direccion:
            errors.append("La dirección es obligatoria.")
        if not descripcion:
            errors.append("La descripción del problema es obligatoria.")

        if not errors:
            solapamiento = db.execute("""
                SELECT id FROM reservas
                WHERE tecnico_id = ? AND fecha_hora = ? AND estado != 'cancelada'
            """, (tecnico_id, fecha_hora)).fetchone()
            if solapamiento:
                errors.append("El técnico ya tiene una reserva en esa fecha y hora.")

        if errors:
            for e in errors:
                flash(e, "error")
        else:
            db.execute("""
                INSERT INTO reservas (cliente_id, tecnico_id, fecha_hora, direccion, descripcion)
                VALUES (?, ?, ?, ?, ?)
            """, (cliente_id, tecnico_id, fecha_hora, direccion, descripcion))
            db.commit()
            flash("Reserva creada correctamente.", "success")
            db.close()
            return redirect(url_for("index"))

    clientes = db.execute("SELECT id, nombre FROM clientes ORDER BY nombre ASC").fetchall()
    tecnicos = db.execute("SELECT id, nombre, especialidad FROM tecnicos ORDER BY nombre ASC").fetchall()
    db.close()
    return render_template("nueva_reserva.html", clientes=clientes, tecnicos=tecnicos)


# ──────────────────────────────────────────────
# Reservas – cancelar
# ──────────────────────────────────────────────

@app.route("/reservas/<int:reserva_id>/cancelar", methods=["GET", "POST"])
def cancelar_reserva(reserva_id):
    db = get_db()
    reserva = db.execute("""
        SELECT r.id, r.estado, r.fecha_hora, r.direccion, r.descripcion,
               c.nombre AS cliente, t.nombre AS tecnico
        FROM   reservas r
        JOIN   clientes c ON c.id = r.cliente_id
        JOIN   tecnicos t ON t.id = r.tecnico_id
        WHERE  r.id = ?
    """, (reserva_id,)).fetchone()

    if not reserva:
        flash("Reserva no encontrada.", "error")
        db.close()
        return redirect(url_for("index"))

    if reserva["estado"] == "cancelada":
        flash("La reserva ya fue cancelada.", "error")
        db.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        motivo = request.form.get("motivo", "").strip() or None
        db.execute("""
            UPDATE reservas SET estado = 'cancelada', motivo_cancelacion = ?
            WHERE id = ?
        """, (motivo, reserva_id))
        db.commit()
        flash("Reserva cancelada.", "success")
        db.close()
        return redirect(url_for("index"))

    db.close()
    return render_template("cancelar_reserva.html", reserva=reserva)


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
