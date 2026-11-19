import re
import unicodedata
from country_state_city import Country, State, City

# Pega todos os países e ordena pra ficar bonito no select do front
PAISES = sorted(Country.get_countries(), key=lambda c: c.name)

VOGAIS = "aeiouyáéíóúâêîôûãõàü"
CONSOANTES = "bcdfghjklmnpqrstvwxzç"


def remove_acento(txt):
    # Função pra tirar acento, senão o banco de dados buga tudo
    return "".join(
        c for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    ).strip().lower()


def palavra_valida(txt):
    # Regex básico pra evitar que o usuário digite "aaaaaaaa" ou "bcd fgh"
    txt = txt.replace("'", "").lower()
    if len(txt) < 2:
        return False, "Muito curto."
    
    if re.search(r"(.)\1{2,}", txt):
        return False, "Letra repetida demais."
    
    if re.search(r"(.{2,})\1{2,}", txt):
        return False, "Repetição estranha."
    
    if re.search(r"[bcdfghjklmnpqrstvwxzç]{4,}", txt):
        return False, "Muitas consoantes juntas."
    
    if not any(c in VOGAIS for c in txt) or not any(c in CONSOANTES for c in txt):
        return False, "Não parece um nome real."
    
    return True, ""


def valida_nome(nome):
    v = (nome or "").strip().title()
    if not v:
        return False, "Nome tá vazio."
    
    if " " in v:
        return False, "Só o primeiro nome, sem sobrenome."
    
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\-]+", v):
        return False, "Sem números ou símbolos no nome."
    
    ok, erro = palavra_valida(v)
    if not ok:
        return False, f"Nome inválido: {erro}"
    return True, v


def valida_sobrenome(sobrenome):
    v = " ".join((sobrenome or "").strip().split()).title()
    if not v:
        return False, "Sobrenome tá vazio."
    
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\s\-]+", v):
        return False, "Apenas letras e espaços no sobrenome."
    
    for p in v.split():
        ok, erro = palavra_valida(p)
        if not ok:
            return False, f"Erro no sobrenome ({p}): {erro}"
    
    return True, v


def valida_idade(idade):
    try:
        n = int(idade)
        if n < 0 or n > 130:
            return False, "Idade tem que ser entre 0 e 130."
        return True, n
    except (ValueError, TypeError):
        return False, "Idade tem que ser um número inteiro."


def formata_telefone(digits, ddi=""):
    prefixo = f"+{ddi} " if ddi else ""
    if len(digits) <= 10:
        return f"{prefixo}({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    
    return f"{prefixo}({digits[:2]}) {digits[2:7]}-{digits[7:11]}"


def valida_telefone(tel, ddi=""):
    # Limpa tudo que não for número
    nums = re.sub(r"\D", "", tel or "")
    
    if len(nums) not in (10, 11):
        return False, "Telefone inválido. Precisa de DDD + número."
    
    return True, formata_telefone(nums, ddi)


def get_pais_info(iso):
    for p in PAISES:
        if p.iso_code == iso:
            return p.name, p.iso_code, str(p.phonecode).lstrip("+")
    return None, None, None


def get_estados(pais_iso):
    estados_todos = State.get_states_of_country(pais_iso)
    
    # Filtra só os que tem sigla de 2 letras (padrão BR)
    estados = [s for s in estados_todos if len(s.iso_code) == 2] or estados_todos
    
    if not estados:
        return [{"name": "Único", "iso_code": "UN"}]
    
    estados.sort(key=lambda s: s.iso_code)
    return [{"name": s.name, "iso_code": s.iso_code.upper()} for s in estados]


def get_cidades(pais_iso, estado_iso, nome_estado):
    cidades = City.get_cities_of_state(pais_iso, estado_iso)
    
    if not cidades:
        return [nome_estado]
    
    return sorted([c.name for c in cidades])