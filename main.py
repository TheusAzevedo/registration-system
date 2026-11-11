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


def get_text(prompt):
    while True:
        valor = input(prompt).strip().title()
        if valor:
            return valor
        print("  Campo vazio, tenta de novo.")


def get_age(prompt):
    while True:
        try:
            n = int(input(prompt))
            if n < 0:
                print("  Idade não pode ser negativa.")
                continue
            return n
        except ValueError:
            print("  Digita um número inteiro válido.")


def register(people):
    print("\n--- NOVO CADASTRO ---")
    name = get_text("  Nome: ")
    age = get_age("  Idade: ")
    city = get_text("  Cidade: ")

    people.append({"name": name, "age": age, "city": city})
    save(people)
    print(f"{name} cadastrado(a).")


def list_all(people):
    print("\n" + "=" * 40)
    print("CADASTROS")
    print("=" * 40)

    if not people:
        print("Nenhum registro.")
        return

    for i, p in enumerate(people, 1):
        print(f"{i}. {p['name']} | {p['age']} anos | {p['city']}")


def stats(people):
    if not people:
        print("\nNada pra calcular ainda.")
        return

    old = max(people, key=lambda p: p["age"])
    young = min(people, key=lambda p: p["age"])
    avg = sum(p["age"] for p in people) / len(people)

    print("\n" + "=" * 40)
    print("ESTATÍSTICAS")
    print("=" * 40)
    print(f"Total: {len(people)}")
    print(f"Mais velho: {old['name']} ({old['age']} anos)")
    print(f"Mais novo: {young['name']} ({young['age']} anos)")
    print(f"Média: {avg:.2f} anos")


def remove(people):
    list_all(people)
    if not people:
        return

    try:
        i = int(input("\nNúmero pra remover (0 cancela): "))
        if i == 0:
            return
        p = people.pop(i - 1)
        save(people)
        print(f"{p['name']} removido(a).")
    except (ValueError, IndexError):
        print("Opção inválida.")


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
            list_all(people)
        elif op == "3":
            stats(people)
        elif op == "4":
            remove(people)
        elif op == "5":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()