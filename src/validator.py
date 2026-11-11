import msvcrt
import re
import unicodedata
from country_state_city import Country, State, City


PAISES = sorted(Country.get_countries(), key=lambda c: c.name)
VOGAIS = "aeiouyáéíóúâêîôûãõàü"
CONSOANTES = "bcdfghjklmnpqrstvwxzç"


def sem_acento(t):
    return "".join(
        c for c in unicodedata.normalize("NFD", t)
        if unicodedata.category(c) != "Mn"
    ).strip().lower()


def palavra_valida(p):
    p = p.replace("'", "").lower()
    if len(p) < 2:
        return False, "Mínimo 2 letras."
    if re.search(r"(.)\1{2,}", p):
        return False, "Letra repetida demais."
    if re.search(r"(.{2,})\1{2,}", p):
        return False, "Repetição estranha."
    if re.search(r"[bcdfghjklmnpqrstvwxzç]{4,}", p):
        return False, "Muitas consoantes seguidas."
    if not any(c in VOGAIS for c in p) or not any(c in CONSOANTES for c in p):
        return False, "Não parece nome."
    return True, ""


def get_first_name(prompt):
    while True:
        v = input(prompt).strip().title()
        if v == "0":
            return None
        if not v:
            print("  Não pode ficar vazio.")
            continue
        if " " in v:
            print("  Só o primeiro nome, sem espaço.")
            continue
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\-]+", v):
            print("  Use apenas letras.")
            continue
        ok, erro = palavra_valida(v)
        if ok:
            return v
        print(f"  {erro}")


def get_last_name(prompt):
    while True:
        v = " ".join(input(prompt).strip().split()).title()
        if v == "0":
            return None
        if not v:
            print("  Não pode ficar vazio.")
            continue
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\s\-]+", v):
            print("  Use apenas letras e espaços.")
            continue
        falhou = False
        for p in v.split():
            ok, erro = palavra_valida(p)
            if not ok:
                print(f"  {erro}")
                falhou = True
                break
        if not falhou:
            return v


def get_citizenship():
    print("\nEscolha o país de cidadania:")
    for i, c in enumerate(PAISES, 1):
        ddi = str(c.phonecode).lstrip("+")
        print(f"  {i:3d}. {c.name} (+{ddi})", end="\n" if i % 3 == 0 else "")
    if len(PAISES) % 3:
        print()

    while True:
        e = input("\nNúmero (0 volta): ").strip()
        if e == "0":
            return None, None, None
        try:
            i = int(e)
            if 1 <= i <= len(PAISES):
                c = PAISES[i - 1]
                return c.name, c.iso_code, str(c.phonecode).lstrip("+")
            print(f"  Fora do intervalo (1 a {len(PAISES)}).")
        except ValueError:
            print("  Digite só o número.")


def get_state(country_code):
    todos = State.get_states_of_country(country_code)

    estados = [s for s in todos if len(s.iso_code) == 2] or todos
    if not estados:
        return "Único", "UN"

    estados.sort(key=lambda s: s.iso_code)

    print("\nEscolha o estado:")
    for i, st in enumerate(estados, 1):
        print(f"  {i:2d}. {st.iso_code.upper():<6}", end="\n" if i % 5 == 0 else "")
    if len(estados) % 5:
        print()

    while True:
        e = input("\nNúmero (0 volta): ").strip()
        if e == "0":
            return None, None
        try:
            i = int(e)
            if 1 <= i <= len(estados):
                st = estados[i - 1]
                return st.name, st.iso_code.upper()
            print(f"  Fora do intervalo (1 a {len(estados)}).")
        except ValueError:
            print("  Digite só o número.")


def get_city(country_code, state_code, state_name):
    cidades = City.get_cities_of_state(country_code, state_code)
    if not cidades:
        return state_name

    nomes = {sem_acento(c.name): c.name for c in cidades}

    while True:
        raw = input(f"  Cidade ({state_code}) (0 volta): ").strip()
        if raw == "0":
            return None
        if len(raw) < 3:
            print("  Mínimo 3 letras, sem abreviar.")
            continue
        chave = sem_acento(raw)
        if chave in nomes:
            return nomes[chave]
        print(f"  '{raw.title()}' não existe em {state_code}.")


def format_phone(digits, ddi=""):
    prefixo = f"+{ddi} " if ddi else ""
    if not digits:
        return prefixo
    if len(digits) <= 2:
        return f"{prefixo}({digits}"
    if len(digits) <= 6:
        return f"{prefixo}({digits[:2]}) {digits[2:]}"
    if len(digits) <= 10:
        return f"{prefixo}({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return f"{prefixo}({digits[:2]}) {digits[2:7]}-{digits[7:11]}"


def redraw(prompt, digits, ddi=""):
    print(f"\r{' ' * 75}\r{prompt}{format_phone(digits, ddi)}", end="", flush=True)


def get_phone(prompt, ddi="", opcional=False):
    while True:
        digits = ""
        redraw(prompt, digits, ddi)

        while True:
            ch = msvcrt.getwch()

            if ch == "\r":
                print()
                break

            if ch == "\x08":
                digits = digits[:-1]
                redraw(prompt, digits, ddi)
                continue

            if ch in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue

            if ch.isdigit() and len(digits) < 11:
                digits += ch
                redraw(prompt, digits, ddi)

        if digits == "0":
            return None
        if opcional and not digits:
            return "Não informado"
        if len(digits) in (10, 11):
            return format_phone(digits, ddi)

        print("  Telefone inválido. Use DDD + número (10 ou 11 dígitos).")


def get_age(prompt):
    while True:
        e = input(prompt).strip()
        if e == "0":
            return None
        try:
            n = int(e)
            if n < 0 or n > 130:
                print("  Idade inválida (0 a 130).")
                continue
            return n
        except ValueError:
            print("  Digite um número inteiro.")