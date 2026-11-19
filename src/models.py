from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Pessoa(db.Model):
    __tablename__ = 'pessoas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(150), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    
    # Localização
    pais = db.Column(db.String(100), nullable=False)
    iso_pais = db.Column(db.String(10), nullable=False)
    ddi = db.Column(db.String(10), nullable=False)
    estado = db.Column(db.String(100), nullable=False)
    sigla_estado = db.Column(db.String(10), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    
    # Contato
    telefone = db.Column(db.String(30), nullable=False)
    
    # TODO: adicionar campo de email depois