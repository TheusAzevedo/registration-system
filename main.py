import json
import os

FILE = "people.json"


def load():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(people):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(people, f, indent=4, ensure_ascii=False)


def voltar():
    input("\nENTER pra voltar ao menu...")


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


def get_phone(prompt, opcional=False):
    while True:
        e = input(prompt).strip()
        if e == "0":
            return None
        if opcional and not e:
            return "Não informado"

        # deixa só os dígitos
        nums = "".join(c for c in e if c.isdigit())

        if len(nums) == 11:
            return f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
        if len(nums) == 10:
            return f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"

        print("  Telefone inválido. Use DDD + número.")


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


def register(people):
    print("\n--- NOVO CADASTRO ---")
    print("(digite 0 em qualquer campo pra cancelar)\n")

    first = get_text("  Nome: ")
    if first is None:
        return
    last = get_text("  Sobrenome: ")
    if last is None:
        return
    phone1 = get_phone("  Telefone principal (com DDD): ")
    if phone1 is None:
        return
    phone2 = get_phone("  Segundo telefone (ENTER pula): ", opcional=True)
    if phone2 is None:
        return
    age = get_age("  Idade: ")
    if age is None:
        return
    city = get_text("  Cidade completa (ex: São Paulo): ")
    if city is None:
        return
    abbr = get_abbr("  Abreviação da cidade (ex: SP): ")
    if abbr is None:
        return
    cidadania = get_text("  Cidadania (ex: Brasileira): ")
    if cidadania is None:
        return

    people.append({
        "first_name": first,
        "last_name": last,
        "phone1": phone1,
        "phone2": phone2,
        "age": age,
        "city": city,
        "city_abbr": abbr,
        "citizenship": cidadania,
    })
    save(people)
    print(f"\n{first} {last} cadastrado(a).")
    voltar()


def mostrar(people):
    print("\n" + "=" * 60)
    print("CADASTROS")
    print("=" * 60)

    for i, p in enumerate(people, 1):
        print(f"{i}. {p['first_name']} {p['last_name']} ({p['age']} anos) - {p['citizenship']}")
        print(f"   {p['city']} ({p['city_abbr']})")
        print(f"   Tel 1: {p['phone1']} | Tel 2: {p['phone2']}")
        print("-" * 60)


def listar(people):
    if not people:
        print("\nNenhum registro.")
        voltar()
        return
    mostrar(people)
    voltar()


def stats(people):
    print("\n" + "=" * 40)
    print("ESTATÍSTICAS")
    print("=" * 40)

    if not people:
        print("Nada pra calcular ainda.")
        voltar()
        return

    old = max(people, key=lambda p: p["age"])
    young = min(people, key=lambda p: p["age"])
    avg = sum(p["age"] for p in people) / len(people)

    print(f"Total: {len(people)}")
    print(f"Mais velho: {old['first_name']} {old['last_name']} ({old['age']} anos)")
    print(f"Mais novo: {young['first_name']} {young['last_name']} ({young['age']} anos)")
    print(f"Média: {avg:.2f} anos")
    voltar()


def remove(people):
    if not people:
        print("\nNenhum registro.")
        voltar()
        return

    mostrar(people)

    while True:
        e = input("\nNúmero pra remover (0 cancela): ").strip()
        if e == "0":
            return
        try:
            i = int(e)
            if 1 <= i <= len(people):
                p = people.pop(i - 1)
                save(people)
                print(f"\n{p['first_name']} {p['last_name']} removido(a).")
                voltar()
                return
            print("Número fora da lista.")
        except ValueError:
            print("Digite um número.")


def main():
    people = load()

    while True:
        print("\n=== CADASTRO ===")
        print("1. Cadastrar")
        print("2. Listar")
        print("3. Estatísticas")
        print("4. Remover")
        print("5. Sair")

        op = input("Opção: ").strip()

        if op == "1":
            register(people)
        elif op == "2":
            listar(people)
        elif op == "3":
            stats(people)
        elif op == "4":
            remove(people)
        elif op == "5":
            r = input("\nSair mesmo? (s/n): ").strip().lower()
            if r == "s":
                print("Tchau!")
                break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()