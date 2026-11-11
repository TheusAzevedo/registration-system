import msvcrt


def get_text(prompt):
    while True:
        v = input(prompt).strip().title()
        if v == "0":
            return None
        if v:
            return v
        print("  Não pode ficar vazio.")


def get_abbr(prompt):
    while True:
        v = input(prompt).strip().upper()
        if v == "0":
            return None
        if v.isalpha() and len(v) in (2, 3):
            return v
        print("  Use 2 ou 3 letras (SP, RJ, BH...).")


def format_phone(digits):
    if not digits:
        return ""
    if len(digits) <= 2:
        return f"({digits}"
    if len(digits) <= 6:
        return f"({digits[:2]}) {digits[2:]}"
    if len(digits) <= 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return f"({digits[:2]}) {digits[2:7]}-{digits[7:11]}"


def redraw(prompt, digits):
    print(f"\r{' ' * 70}\r{prompt}{format_phone(digits)}", end="", flush=True)


def get_phone(prompt, opcional=False):
    while True:
        digits = ""
        print(prompt, end="", flush=True)

        while True:
            ch = msvcrt.getwch()

            if ch == "\r":
                print()
                break

            if ch == "\x08":
                digits = digits[:-1]
                redraw(prompt, digits)
                continue

            if ch in ("\x00", "\xe0"):
                msvcrt.getwch()  # ignora setas e teclas especiais
                continue

            if ch.isdigit() and len(digits) < 11:
                digits += ch
                redraw(prompt, digits)

        if digits == "0":
            return None
        if opcional and not digits:
            return "Não informado"
        if len(digits) in (10, 11):
            return format_phone(digits)

        print("  Telefone inválido. Use DDD + número (10 ou 11 dígitos).")


def get_age(prompt):
    while True:
        e = input(prompt).strip()
        if e == "0":
            return None
        try:
            n = int(e)
            if n < 0:
                print("  Idade não pode ser negativa.")
                continue
            return n
        except ValueError:
            print("  Digite um número inteiro.")