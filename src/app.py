import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Pessoa
from validator import (
    PAISES, valida_nome, valida_sobrenome, valida_idade, valida_telefone,
    pegar_info_pais, pegar_estados, pegar_cidades
)

# Aponta para a pasta principal do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

# Configurações básicas
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# TODO: Mudar essa secret key no servidor antes de subir pro ar
app.secret_key = os.getenv("SECRET_KEY", "dev-key")

db.init_app(app)

# Cria as tabelas na primeira execução
with app.app_context():
    db.create_all() 


@app.route("/")
def index():
    # Não envia a lista de pessoas nem nomes confidenciais para a página pública
    return render_template("index.html", paises=PAISES)


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    # Validações básicas do form
    ok_nome, nome = valida_nome(request.form.get("nome"))
    if not ok_nome:
        flash(nome, "danger")
        return redirect(url_for("index"))

    ok_sobrenome, sobrenome = valida_sobrenome(request.form.get("sobrenome"))
    if not ok_sobrenome:
        flash(sobrenome, "danger")
        return redirect(url_for("index"))

    ok_idade, idade = valida_idade(request.form.get("idade"))
    if not ok_idade:
        flash(idade, "danger")
        return redirect(url_for("index"))

    # Dados de localização
    iso_pais = request.form.get("iso_pais")
    pais, iso, ddi = pegar_info_pais(iso_pais)
    
    # O select manda "UF|Nome do Estado" junto, por isso o split
    estado_raw = request.form.get("estado", "") 
    cidade = request.form.get("cidade")

    if not pais or "|" not in estado_raw or not cidade:
        flash("Escolha o país, estado e cidade direito.", "danger")
        return redirect(url_for("index"))

    uf, estado_nome = estado_raw.split("|", 1)

    ok_tel, telefone = valida_telefone(request.form.get("telefone"), ddi=ddi)
    if not ok_tel:
        flash(telefone, "danger")
        return redirect(url_for("index"))

    # Se passou por tudo, salva no banco
    nova_pessoa = Pessoa(
        nome=nome,
        sobrenome=sobrenome,
        idade=idade,
        pais=pais,
        iso_pais=iso,
        ddi=ddi,
        estado=estado_nome,
        sigla_estado=uf,
        cidade=cidade,
        telefone=telefone,
    )
    
    db.session.add(nova_pessoa)
    db.session.commit()

    flash(f"{nome} cadastrado com sucesso!", "success")
    return redirect(url_for("index"))


# --- Rotas AJAX pro JavaScript buscar os estados e cidades ---
@app.route("/api/estados/<iso_pais>")
def api_estados(iso_pais):
    return jsonify(pegar_estados(iso_pais))


@app.route("/api/cidades/<iso_pais>/<uf>/<path:estado_nome>")
def api_cidades(iso_pais, uf, estado_nome):
    return jsonify(pegar_cidades(iso_pais, uf, estado_nome))


if __name__ == "__main__":
    print("Rodando o servidor local...")
    app.run(debug=False)