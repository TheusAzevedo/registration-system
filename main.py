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

    name = get_text("  Nome: ")
    if name is None:
        print("Cancelado.")
        return

    age = get_age("  Idade: ")
    if age is None:
        print("Cancelado.")
        return

    city = get_text("  Cidade: ")
    if city is None:
        print("Cancelado.")
        return

    people.append({"name": name, "age": age, "city": city})
    save(people)
    print(f"\n{name} cadastrado(a) com sucesso.")
    voltar()


def listar(people):
    print("\n" + "=" * 40)
    print("CADASTROS")
    print("=" * 40)

    if not people:
        print("Nenhum registro.")
        voltar()
        return

    for i, p in enumerate(people, 1):
        print(f"{i}. {p['name']} | {p['age']} anos | {p['city']}")
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
    print(f"Mais velho: {old['name']} ({old['age']} anos)")
    print(f"Mais novo: {young['name']} ({young['age']} anos)")
    print(f"Média: {avg:.2f} anos")
    voltar()


def remove(people):
    if not people:
        print("\nNenhum registro.")
        voltar()
        return

    print("\n" + "=" * 40)
    print("CADASTROS")
    print("=" * 40)
    for i, p in enumerate(people, 1):
        print(f"{i}. {p['name']} | {p['age']} anos | {p['city']}")

    while True:
        e = input("\nNúmero pra remover (0 cancela): ").strip()
        if e == "0":
            return
        try:
            i = int(e)
            if 1 <= i <= len(people):
                p = people.pop(i - 1)
                save(people)
                print(f"\n{p['name']} removido(a).")
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
            r = input("Sair mesmo? (s/n): ").strip().lower()
            if r == "s":
                print("Tchau!")
                break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()