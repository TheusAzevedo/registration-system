import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Person
from admin import admin_bp
from validator import (
    COUNTRIES, validate_first_name, validate_last_name, validate_age,
    validate_phone, validate_location, get_states_list, get_cities_list
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# Ajusta a URL do banco pra funcionar em nuvem (Render/Railway) com psycopg3
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
app.secret_key = os.getenv("SECRET_KEY")

db.init_app(app)
app.register_blueprint(admin_bp) 

with app.app_context():
    db.create_all()


@app.after_request
def add_security_headers(response):
    # Headers de segurança (clickjacking, XSS) e CSP pro CDN do Bootstrap
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
    )
    return response


@app.route("/")
def index():
    return render_template("index.html", countries=COUNTRIES)


@app.route("/register", methods=["POST"])
def register():
    # Valida nome, sobrenome e idade
    ok_first, first_name = validate_first_name(request.form.get("first_name"))
    if not ok_first:
        flash(first_name, "danger")
        return redirect(url_for("index"))

    ok_last, last_name = validate_last_name(request.form.get("last_name"))
    if not ok_last:
        flash(last_name, "danger")
        return redirect(url_for("index"))

    ok_age, age = validate_age(request.form.get("age"))
    if not ok_age:
        flash(age, "danger")
        return redirect(url_for("index"))

    # Valida a localização (pra ver se o usuário não burlou o HTML)
    ok_loc, loc = validate_location(
        request.form.get("country_iso"),
        request.form.get("state"),
        request.form.get("city"),
    )
    if not ok_loc:
        flash("Localização inválida.", "danger")
        return redirect(url_for("index"))

    # Desempacota os dados da localização
    country, iso, ddi, state_code, state_name, city = loc

    ok_phone, phone = validate_phone(request.form.get("phone"), ddi=ddi)
    if not ok_phone:
        flash(phone, "danger")
        return redirect(url_for("index"))

    # Salva no banco
    new_person = Person(
        first_name=first_name,
        last_name=last_name,
        age=age,
        country=country,
        country_iso=iso,
        phone_code=ddi,
        state=state_name,
        state_code=state_code,
        city=city,
        phone=phone,
    )

    db.session.add(new_person)
    db.session.commit()

    flash("Cadastro realizado com sucesso!", "success")
    return redirect(url_for("index"))


# Rotas API pro JavaScript buscar estados e cidades
@app.route("/api/states/<country_iso>")
def api_states(country_iso):
    return jsonify(get_states_list(country_iso))


@app.route("/api/cities/<country_iso>/<state_code>/<path:state_name>")
def api_cities(country_iso, state_code, state_name):
    return jsonify(get_cities_list(country_iso, state_code, state_name))


if __name__ == "__main__":
    print("Rodando o servidor...")
    app.run(debug=False)