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
    # Pega a galera toda, do mais recente pro mais antigo
    pessoas = Pessoa.query.order_by(Pessoa.id.desc()).all()

    stats = None
    if pessoas:
        idades = [p.idade for p in pessoas]
        velho = max(pessoas, key=lambda p: p.idade)
        novo = min(pessoas, key=lambda p: p.idade)
        
        # Contando quantos tem de cada país
        por_pais = {}
        for p in pessoas:
            if p.pais in por_pais:
                por_pais[p.pais] += 1
            else:
                por_pais[p.pais] = 1

        stats = {
            "total": len(pessoas),
            "media": round(sum(idades) / len(idades), 1),
            "velho": f"{velho.nome} {velho.sobrenome} ({velho.idade})",
            "novo": f"{novo.nome} {novo.sobrenome} ({novo.idade})",
            # Ordena do país com mais gente pro com menos
            "por_pais": sorted(por_pais.items(), key=lambda x: x[1], reverse=True),
        }

    return render_template("index.html", cadastros=pessoas, paises=PAISES, stats=stats)


@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    # Pega e valida o nome
    ok_nome, nome = valida_nome(request.form.get("nome"))
    if not ok_nome:
        flash(nome, "danger")
        return redirect(url_for("index"))

    # Pega e valida o sobrenome
    ok_sobrenome, sobrenome = valida_sobrenome(request.form.get("sobrenome"))
    if not ok_sobrenome:
        flash(sobrenome, "danger")
        return redirect(url_for("index"))

    # Pega e valida a idade
    ok_idade, idade = valida_idade(request.form.get("idade"))
    if not ok_idade:
        flash(idade, "danger")
        return redirect(url_for("index"))

    # Pega os dados de localização
    iso_pais = request.form.get("iso_pais")
    pais, iso, ddi = pegar_info_pais(iso_pais)
    
    # O select manda "UF|Nome do Estado" junto
    estado_raw = request.form.get("estado", "") 
    cidade = request.form.get("cidade")

    if not pais or "|" not in estado_raw or not cidade:
        flash("Escolha o país, estado e cidade direito.", "danger")
        return redirect(url_for("index"))

    uf, estado_nome = estado_raw.split("|", 1)

    # Pega e valida o telefone
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


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    pessoa = Pessoa.query.get_or_404(id)

    if request.method == "POST":
        # Mesma coisa do cadastro, mas atualizando o que já existe
        ok_nome, nome = valida_nome(request.form.get("nome"))
        if not ok_nome:
            flash(nome, "danger")
            return redirect(url_for("editar", id=id))

        ok_sobrenome, sobrenome = valida_sobrenome(request.form.get("sobrenome"))
        if not ok_sobrenome:
            flash(sobrenome, "danger")
            return redirect(url_for("editar", id=id))

        ok_idade, idade = valida_idade(request.form.get("idade"))
        if not ok_idade:
            flash(idade, "danger")
            return redirect(url_for("editar", id=id))

        iso_pais = request.form.get("iso_pais")
        pais, iso, ddi = pegar_info_pais(iso_pais)
        estado_raw = request.form.get("estado", "")
        cidade = request.form.get("cidade")

        if not pais or "|" not in estado_raw or not cidade:
            flash("Localização inválida, confere aí.", "danger")
            return redirect(url_for("editar", id=id))

        uf, estado_nome = estado_raw.split("|", 1)

        ok_tel, telefone = valida_telefone(request.form.get("telefone"), ddi=ddi)
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
        flash("Dados atualizados!", "success")
        return redirect(url_for("index"))

    return render_template("editar.html", pessoa=pessoa, paises=PAISES)


@app.route("/remover/<int:id>", methods=["POST"])
def remover(id):
    pessoa = Pessoa.query.get_or_404(id)
    db.session.delete(pessoa)
    db.session.commit()
    
    flash(f"{pessoa.nome} foi removido do sistema.", "warning")
    return redirect(url_for("index"))


# --- Rotas AJAX pro JavaScript buscar os estados e cidades ---
@app.route("/api/estados/<iso_pais>")
def api_estados(iso_pais):
    return jsonify(pegar_estados(iso_pais))


@app.route("/api/cidades/<iso_pais>/<uf>/<estado_nome>")
def api_cidades(iso_pais, uf, estado_nome):
    return jsonify(pegar_cidades(iso_pais, uf, estado_nome))


if __name__ == "__main__":
    print("Rodando o servidor local...")
    app.run(debug=True)