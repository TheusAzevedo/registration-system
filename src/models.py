import os
from cryptography.fernet import Fernet
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import TypeDecorator, Text

db = SQLAlchemy()


def get_cipher():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Se der isso em prod, o sistema quebra na hora de salvar
        raise RuntimeError("Faltou a ENCRYPTION_KEY no .env!")
    return Fernet(key.encode())


class EncryptedString(TypeDecorator):
    # Criptografa antes de mandar pro Postgres e descriptografa na leitura
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        # Criptografa o bagulho
        return get_cipher().encrypt(str(value).encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # Descriptografa pra aparecer legível na tela
        return get_cipher().decrypt(value.encode()).decode()


class Person(db.Model):
    __tablename__ = "people"

    id = db.Column(db.Integer, primary_key=True)
    
    # Dados pessoais (criptografados por segurança/LGPD)
    first_name = db.Column(EncryptedString, nullable=False)
    last_name = db.Column(EncryptedString, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # Localização (deixei aberto pra facilitar busca/filtros)
    country = db.Column(db.String(100), nullable=False)
    country_iso = db.Column(db.String(10), nullable=False)
    phone_code = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    state_code = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(100), nullable=False)

    # Contato (também criptografado)
    phone = db.Column(EncryptedString, nullable=False)