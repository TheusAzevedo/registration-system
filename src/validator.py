import re
import unicodedata
from country_state_city import Country, State, City

# Pega todos os países e ordena por nome
PAISES = sorted(Country.get_countries(), key=lambda c: c.name)

VOGAIS = "aeiouyáéíóúâêîôûãõàü"
CONSOANTES = "bcdfghjklmnpqrstvwxzç"


def tirar_acento(txt):
    # Limpa a string pra não bugar a busca no banco depois
    return "".join(
        c for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    ).strip().lower()


def palavra_valida(txt):
    # Validação pra evitar que o usuário digite "aaaaa" ou "bcd fgh"
    txt = txt.replace("'", "").lower()
    
    if len(txt) < 2:
        return False, "Muito curto."
        
    if re.search(r"(.)\1{2,}", txt):
        return False, "Letra repetida demais."
        
    if re.search(r"(.{2,})\1{2,}", txt):
        return False, "Repetição estranha."
        
    if re.search(r"[bcdfghjklmnpqrstvwxzç]{4,}", txt):
        return False, "Muitas consoantes juntas."
        
    # Verifica se tem vogal e consoante
    if not any(c in VOGAIS for c in txt) or not any(c in CONSOANTES for c in txt):
        return False, "Não parece um nome real."
        
    return True, ""


def valida_nome(valor):
    v = (valor or "").strip().title()
    
    if not v:
        return False, "O nome tá vazio."
        
    if " " in v:
        return False, "Coloca só o primeiro nome aqui, sem sobrenome."
        
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\-]+", v):
        return False, "Sem números ou símbolos no nome."
        
    ok, erro = palavra_valida(v)
    if not ok:
        return False, f"Nome inválido: {erro}"
        
    return True, v


def valida_sobrenome(valor):
    # Junta os espaços extras que o povo digita por engano
    v = " ".join((valor or "").strip().split()).title()
    
    if not v:
        return False, "Sobrenome não pode ficar vazio."
        
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\s\-]+", v):
        return False, "Apenas letras e espaços no sobrenome."
        
    # Valida cada pedaço do sobrenome (ex: "Da Silva" valida "Da" e "Silva")
    for p in v.split():
        ok, erro = palavra_valida(p)
        if not ok:
            return False, f"Deu erro no sobrenome ({p}): {erro}"
            
    return True, v


def valida_idade(valor):
    try:
        n = int(valor)
        if n < 0 or n > 130:
            return False, "Idade tem que ser entre 0 e 130."
        return True, n
    except (ValueError, TypeError):
        return False, "Manda um número inteiro aí."


def formata_telefone(digits, ddi=""):
    prefixo = f"+{ddi} " if ddi else ""
    
    # Se for fixo (10 dígitos)
    if len(digits) <= 10:
        return f"{prefixo}({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        
    # Se for celular (11 dígitos)
    return f"{prefixo}({digits[:2]}) {digits[2:7]}-{digits[7:11]}"


def valida_telefone(valor, ddi=""):
    # Limpa tudo que não for número (parênteses, traços, etc)
    digits = re.sub(r"\D", "", valor or "")
    
    if len(digits) not in (10, 11):
        return False, "Telefone inválido. Precisa de DDD + número."
        
    return True, formata_telefone(digits, ddi)


def pegar_info_pais(iso_code):
    for p in PAISES:
        p_iso = getattr(p, "iso_code", getattr(p, "iso2", ""))
        if p_iso == iso_code:
            ddi = str(getattr(p, "phone_code", getattr(p, "phonecode", ""))).lstrip("+")
            return p.name, p_iso, ddi
    return None, None, None

def pegar_estados(country_code):
    todos = State.get_states_of_country(country_code)
    estados = [
        s for s in todos
        if len(getattr(s, "iso_code", getattr(s, "state_code", ""))) == 2
    ] or todos

    if not estados:
        return [{"name": "Único", "iso_code": "UN"}]

    estados.sort(key=lambda s: getattr(s, "iso_code", getattr(s, "state_code", "")))
    return [
        {
            "name": s.name,
            "iso_code": getattr(s, "iso_code", getattr(s, "state_code", "")).upper(),
        }
        for s in estados
    ]

def pegar_cidades(country_code, state_code, state_name):
    cidades = City.get_cities_of_state(country_code, state_code)
    if not cidades:
        return [state_name]
    return sorted([c.name for c in cidades])