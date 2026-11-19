import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Pessoa
from validator import (
    PAISES, validate_first_name, validate_last_name, validate_age,
    validate_phone, get_country_info, get_states_list, get_cities_list
)

load_dotenv()

app = Flask(__name__)

# Configuração do banco e do Flask
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# TODO: Mudar essa secret key antes de subir pra produção no Render
app.secret_key = os.getenv("SECRET_KEY", "dev-key")

db.init_app(app)

# Cria as tabelas se não existirem
with app.app_context():
    db.create_all() 


@app.route("/")
def index():
    # Pega todos, do mais novo pro mais velho no sistema
    cadastros = Pessoa.query.order_by(Pessoa.id.desc()).all()

    stats = None
    if cadastros:
        idades = [p.idade for p in cadastros]
        velho = max(cadastros, key=lambda p: p.idade)
        novo = min(cadastros, key=lambda p: p.idade)
        
        # Contando quantos tem de cada país
        por_pais = {}
        for p in cadastros:
            if p.pais in por_pais:
                por_pais[p.pais] += 1
            else:
                por_pais[p.pais] = 1

        stats = {
            "total": len(cadastros),
            "media": round(sum(idades) / len(idades), 1),
            "velho": f"{velho.nome} {velho.sobrenome} ({velho.idade})",
            "novo": f"{novo.nome} {novo.sobrenome} ({novo.idade})",
            "por_pais": sorted(por_pais.items(), key=lambda x: x[1], reverse=True),
        }

    return render_template("index.html", cadastros=cadastros, paises=PAISES, stats=stats)


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    # Validações básicas
    ok_nome, nome = validate_first_name(request.form.get("nome"))
    if not ok_nome:
        flash(nome, "danger")
        return redirect(url_for("index"))

    ok_sobrenome, sobrenome = validate_last_name(request.form.get("sobrenome"))
    if not ok_sobrenome:
        flash(sobrenome, "danger")
        return redirect(url_for("index"))

    ok_idade, idade = validate_age(request.form.get("idade"))
    if not ok_idade:
        flash(idade, "danger")
        return redirect(url_for("index"))

    # Localização
    iso_pais = request.form.get("iso_pais")
    pais, iso, ddi = get_country_info(iso_pais)
    
    # O select de estado manda "UF|Nome do Estado" junto, por isso o split
    estado_raw = request.form.get("estado", "") 
    cidade = request.form.get("cidade")

    if not pais or "|" not in estado_raw or not cidade:
        flash("Escolha o país, estado e cidade direito.", "danger")
        return redirect(url_for("index"))

    uf, estado_nome = estado_raw.split("|", 1)

    ok_tel, telefone = validate_phone(request.form.get("telefone"), ddi=ddi)
    if not ok_tel:
        flash(telefone, "danger")
        return redirect(url_for("index"))

    # Tudo certo, salva no banco
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


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    pessoa = Pessoa.query.get_or_404(id)

    if request.method == "POST":
        # Mesma coisa do cadastro, mas atualiza o que já existe
        ok_nome, nome = validate_first_name(request.form.get("nome"))
        if not ok_nome:
            flash(nome, "danger")
            return redirect(url_for("editar", id=id))

        ok_sobrenome, sobrenome = validate_last_name(request.form.get("sobrenome"))
        if not ok_sobrenome:
            flash(sobrenome, "danger")
            return redirect(url_for("editar", id=id))

        ok_idade, idade = validate_age(request.form.get("idade"))
        if not ok_idade:
            flash(idade, "danger")
            return redirect(url_for("editar", id=id))

        iso_pais = request.form.get("iso_pais")
        pais, iso, ddi = get_country_info(iso_pais)
        estado_raw = request.form.get("estado", "")
        cidade = request.form.get("cidade")

        if not pais or "|" not in estado_raw or not cidade:
            flash("Localização inválida, confere aí.", "danger")
            return redirect(url_for("editar", id=id))

        uf, estado_nome = estado_raw.split("|", 1)

        ok_tel, telefone = validate_phone(request.form.get("telefone"), ddi=ddi)
        if not ok_tel:
            flash(telefone, "danger")
            return redirect(url_for("editar", id=id))

        # Atualizando os campos na mão
        pessoa.nome = nome
        pessoa.sobrenome = sobrenome
        pessoa.idade = idade
        pessoa.pais = pais
        pessoa.iso_pais = iso
        pessoa.ddi = ddi
        pessoa.estado = estado_nome
        pessoa.sigla_estado = uf
        pessoa.cidade = cidade
        pessoa.telefone = telefone

        db.session.commit()
        flash("Cadastro atualizado!", "success")
        return redirect(url_for("index"))

    return render_template("editar.html", pessoa=pessoa, paises=PAISES)


@app.route("/remover/<int:id>", methods=["POST"])
def remover(id):
    pessoa = Pessoa.query.get_or_404(id)
    db.session.delete(pessoa)
    db.session.commit()
    
    flash(f"{pessoa.nome} foi deletado do sistema.", "warning")
    return redirect(url_for("index"))


# --- Rotas AJAX pra carregar estado e cidade no front ---
@app.route("/api/estados/<iso_pais>")
def api_estados(iso_pais):
    return jsonify(get_states_list(iso_pais))


@app.route("/api/cidades/<iso_pais>/<uf>/<estado_nome>")
def api_cidades(iso_pais, uf, estado_nome):
    return jsonify(get_cities_list(iso_pais, uf, estado_nome))


if __name__ == "__main__":
    print("Iniciando servidor...")
    app.run(debug=True)