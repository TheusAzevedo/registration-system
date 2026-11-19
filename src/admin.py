import hmac
import os
import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Person

admin_bp = Blueprint("admin", __name__)

# Proteção contra brute force (5 tentativas e bloqueia por 5 min)
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  
failed_attempts = {}   # Dicionário pra rastrear as tentativas: {ip: {"count": int, "locked_until": float}}


def get_client_ip():
    # Pega o IP real do usuário, mesmo atrás de proxy/Cloudflare
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    ip = get_client_ip()
    now = time.time()
    record = failed_attempts.get(ip, {"count": 0, "locked_until": 0})

    # Vê se o IP já tá de castigo
    if record["locked_until"] > now:
        remaining = int(record["locked_until"] - now)
        flash(f"Muitas tentativas falhas. Tenta de novo em {remaining} segundos.", "danger")
        return render_template("login.html"), 429

    if request.method == "POST":
        password = request.form.get("password", "")
        admin_pass = os.getenv("ADMIN_PASSWORD", "")

        # compare_digest evita timing attack (coisa de segurança chique)
        if admin_pass and hmac.compare_digest(password, admin_pass):
            failed_attempts.pop(ip, None)  # Acertou a senha, limpa o histórico dele
            session["is_admin"] = True
            return redirect(url_for("admin.panel"))

        # Errou a senha? Bora contar.
        record["count"] += 1
        if record["count"] >= MAX_ATTEMPTS:
            record["locked_until"] = now + LOCKOUT_SECONDS
            record["count"] = 0
            failed_attempts[ip] = record
            flash("Limite de tentativas excedido. Bloqueado por 5 minutos.", "danger")
            return render_template("login.html"), 429

        failed_attempts[ip] = record
        attempts_left = MAX_ATTEMPTS - record["count"]
        flash(f"Senha incorreta. Restam {attempts_left} tentativas.", "danger")
        return redirect(url_for("admin.login"))

    return render_template("login.html")


@admin_bp.route("/admin")
def panel():
    if not session.get("is_admin"):
        return redirect(url_for("admin.login"))

    # Puxa a galera toda do banco
    people = Person.query.order_by(Person.id.desc()).all()
    return render_template("admin.html", people=people)


@admin_bp.route("/admin/delete/<int:person_id>", methods=["POST"])
def delete_person(person_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin.login"))

    person = Person.query.get_or_404(person_id)
    db.session.delete(person)
    db.session.commit()
    
    flash("Registro apagado.", "warning")
    return redirect(url_for("admin.panel"))


@admin_bp.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))