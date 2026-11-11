import msvcrt
import unicodedata
from country_state_city import Country, State, City


PAISES = sorted(Country.get_all_countries(), key=lambda c: c.name)

def sem_acento(t):
    return "".join(
        c for c in unicodedata.normalize("NFD", t)
        if unicodedata.category(c) != "Mn"
    ).strip().lower()

def get_text(prompt):
    while True:
        v = input(prompt).strip().title()
        if v == "0":
            return None
        if v:
            return v
        print(" Não pode ficar vazio.")

def get_citizenship():
    print("\nEscolha o país de cidadania:")
    for i, c in enumerate(PAISES, 1):
        ddi = str(c.phonecode).lstrip("+")
        label = f"{c.name} (+{ddi})"
        print(f"  {i:3d}. {label:<34}", end="\n" if i % 3 == 0 else "")
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

    estados.sort(key=lambda s: s.name)

    print("\nEscolha o estado:")
    for i, st in enumerate(estados, 1):
        print(f"  {i:2d}. {st.name} ({st.iso_code.upper()})", end="\n" if i % 2 == 0 else "")
    if len(estados) % 2:
        print()

    while True:
        e = input("\nNúmero (0 volta): ").strip()
        if e == "0":
            return None, None
        try:
            i = int(e)
            if 1 <= i <= len(estados):
                st = estados[i - 1]
                return st.name, st.iso_code
            print(f"  Fora do intervalo (1 a {len(estados)}).")
        except ValueError:
            print("  Digite só o número.")


def get_city(country_code, state_code, state_name):
    cidades = City.get_cities_of_state(country_code, state_code)
    if not cidades:
        return state_name

    nomes = {sem_acento(c.name): c.name for c in cidades}

    while True:
        raw = input(f"  Cidade de {state_name} ({state_code}) (0 volta): ").strip()
        if raw == "0":
            return None
        if len(raw) < 3:
            print("  Mínimo 3 letras, sem abreviar.")
            continue
        chave = sem_acento(raw)
        if chave in nomes:
            return nomes[chave]
        print(f"  '{raw.title()}' não existe em {state_name} ({state_code}).")

def format_phone(digits, ddi=""):
    prefixo = f"+{ddi} " if ddi else ""
    if not digits:
        return prefixo
    if len(digits) <= 2:
        return f"{prefixo} ({digits}"
    if len(digits) <= 6:
        return f"{prefixo} ({digits[:2]}) {digits[2:]}"
    if len(digits) <= 10:
        return f"{prefixo}({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return f"{prefixo}({digits[:2]}) {digits[2:7]}-{digits[7:11]}"

def redraw(prompt, digits, ddi=""):
    print(f"\r {' ' *75}\r {prompt}{format_phone(digits, ddi="")}", end="", flush=True)

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
        if len (digits) in (10, 11):
            return format_phone(digits, ddi)

        print(" Telefone invalido. Use DDD + nuymero (10 ou 11 digitos)")

def get_age(prompt):
    while True:
        e = input(prompt).strip()
        if e == "0":
            return None
        try:
            n = int(e)
            if n < 0:
                print(" Idade não pode ser negativa")
                continue
            return n
        except ValueError:
            print(" Digite um numero")