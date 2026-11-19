import re
import unicodedata
from country_state_city import Country, State, City

COUNTRIES = sorted(Country.get_countries(), key=lambda c: c.name)

VOWELS = "aeiouyáéíóúâêîôûãõàü"
CONSONANTS = "bcdfghjklmnpqrstvwxzç"

# Regex pra barrar XSS, SQL Injection e tags HTML chatas
THREAT_REGEX = re.compile(
    r"(<|>|script|javascript:|onerror|onload|select\s|insert\s|update\s|delete\s|drop\s|--|;|/\*|\*/|\{|\}|\[|\]|\$|\\)",
    re.IGNORECASE,
)


def contains_threat(txt):
    return bool(THREAT_REGEX.search(str(txt or "")))


def remove_accents(txt):
    return "".join(
        c for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    ).strip().lower()


def is_valid_word(txt):
    txt = txt.replace("'", "").lower()

    if len(txt) < 2 or len(txt) > 40:
        return False, "Length must be between 2 and 40."

    if re.search(r"(.)\1{2,}", txt):
        return False, "Too many repeated letters."

    if re.search(r"(.{2,})\1{2,}", txt):
        return False, "Weird repetition."

    if re.search(r"[bcdfghjklmnpqrstvwxzç]{4,}", txt):
        return False, "Too many consonants in a row."

    if not any(c in VOWELS for c in txt) or not any(c in CONSONANTS for c in txt):
        return False, "Doesn't look like a real name."

    return True, ""


def validate_first_name(value):
    if contains_threat(value):
        return False, "Forbidden characters."

    v = (value or "").strip().title()

    if not v:
        return False, "Name can't be empty."

    if " " in v:
        return False, "Just the first name, no spaces."

    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\-]+", v):
        return False, "Only letters, please."

    ok, error = is_valid_word(v)
    if not ok:
        return False, f"Invalid name: {error}"

    return True, v


def validate_last_name(value):
    if contains_threat(value):
        return False, "Forbidden characters."

    v = " ".join((value or "").strip().split()).title()

    if not v:
        return False, "Last name can't be empty."

    if len(v) > 100:
        return False, "Last name is too long (max 100)."

    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'\s\-]+", v):
        return False, "Only letters and spaces."

    for p in v.split():
        ok, error = is_valid_word(p)
        if not ok:
            return False, f"Invalid last name ({p}): {error}"

    return True, v


def validate_age(value):
    if not re.fullmatch(r"\d{1,3}", str(value or "").strip()):
        return False, "Age must be an integer."
    
    n = int(value)
    if n < 0 or n > 130:
        return False, "Age must be 0-130."
    
    return True, n


def format_phone(digits, ddi=""):
    prefix = f"+{ddi} " if ddi else ""
    if len(digits) <= 10:
        return f"{prefix}({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return f"{prefix}({digits[:2]}) {digits[2:7]}-{digits[7:11]}"


def validate_phone(value, ddi=""):
    if contains_threat(value):
        return False, "Invalid characters in phone."

    digits = re.sub(r"\D", "", value or "")
    if len(digits) not in (10, 11):
        return False, "Invalid phone. Use area code + number (10 or 11 digits)."

    return True, format_phone(digits, ddi)


def validate_location(country_iso, state_raw, city):
    # Valida se o usuário não alterou o HTML via Inspect Element
    if not re.fullmatch(r"[A-Z]{2,3}", str(country_iso or "")):
        return False, None

    if any(contains_threat(x) for x in (state_raw, city)):
        return False, None

    country, iso, ddi = get_country_info(country_iso)
    if not country or "|" not in str(state_raw or "") or not city:
        return False, None

    state_code, state_name = state_raw.split("|", 1)
    if not re.fullmatch(r"[A-Z0-9\-]{1,10}", state_code):
        return False, None

    valid_cities = get_cities_list(iso, state_code, state_name)
    if city not in valid_cities:
        return False, None

    return True, (country, iso, ddi, state_code, state_name, city)


def get_country_info(iso_code):
    for c in COUNTRIES:
        # Tenta pegar iso_code, se não tiver tenta iso2
        c_iso = getattr(c, "iso_code", None) or getattr(c, "iso2", "")
        
        if c_iso == iso_code:
            ddi = getattr(c, "phone_code", None) or getattr(c, "phonecode", "")
            return c.name, c_iso, str(ddi).lstrip("+")
            
    return None, None, None


def get_states_list(country_code):
    if not re.fullmatch(r"[A-Z]{2,3}", str(country_code or "")):
        return []
        
    all_states = State.get_states_of_country(country_code)
    
    # Filtra só os que tem sigla de 2 letras
    states_filtrados = []
    for s in all_states:
        uf = getattr(s, "iso_code", None) or getattr(s, "state_code", "")
        if len(uf) == 2:
            states_filtrados.append(s)
            
    states = states_filtrados if states_filtrados else all_states

    if not states:
        return [{"name": "Unique", "iso_code": "UN"}]

    states.sort(key=lambda s: s.name)
    
    # Monta a lista pro front
    result = []
    for s in states:
        sigla = getattr(s, "iso_code", None) or getattr(s, "state_code", "")
        result.append({
            "name": s.name,
            "iso_code": sigla.upper(),
        })
        
    return result


def get_cities_list(country_code, state_code, state_name):
    if not re.fullmatch(r"[A-Z]{2,3}", str(country_code or "")) or contains_threat(state_name):
        return []
        
    cities = City.get_cities_of_state(country_code, state_code)
    
    if not cities:
        return [state_name]
        
    return sorted([c.name for c in cities])