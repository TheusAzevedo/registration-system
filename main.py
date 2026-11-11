from storage import load, save
from validator import get_text, get_abbr, get_phone, get_age


def voltar():
    input("\nENTER pra voltar ao menu...")


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
    city = get_text("  Cidade (ex: São Paulo): ")
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


def update(people):
    if not people:
        print("\nNenhum registro.")
        voltar()
        return

    mostrar(people)

    while True:
        e = input("\nNúmero do cadastro pra atualizar (0 cancela): ").strip()
        if e == "0":
            return
        try:
            i = int(e)
            if 1 <= i <= len(people):
                person = people [i - 1]
                break
            print("Numero fora da lista.")
        except ValueError:
            print("Digite um numero.")

    while True:
        print(f"\n--- ATUALIZAR: {person['first_name']}{person['last_name']} ---")
        print(f"1. Nome ({person['fitst_name']})")
        print(f"2. Sobrenome ({person['last_name']})")
        print(f"3. Telefone Princiapal ({['phone1']})")
        print(f"4. Segundo Telefone ({['phone2']})")
        print(f"5. Idade ({['age']}) anos")
        print(f"6. Cidade ({person['city']}) - {person['cit_abbr']}")
        print(f"7. Cidadania ({person['citizenship']})")
        print(f"0. Concluir")

        op = input("\nO que mudou? ").strip()

        if op == "0":
            return

        if op == "1":
            val = get_text(" Novo nome: ")
            if val is not None:
                person["first_name"] = val 

        elif op =="2":
            print(f"\n Sobrenome atual: {person['last_name']}")
            print (" 1. Adicionar (casamento, 3° nome)")
            print (" 2. Substituir")
            print (" 0 Cancelar")
            sub = input (" Opção: ").strip()

            if sub == "1":
                extra = get_text(" Sobrenome a adicionar:")
                if extra is not None:
                    person ["last_name"] = f"{person['last_name']} {extra}"
            elif sub == "2":
                novo = get_text (" Novo Sobrenome Completo:  ")
                if novo is not None:
                    person ["last_name"] = novo
            else:
                continue
        elif op == "3":
            val = get_phone(" Novo Telefone Principal: ")
            if val is not None:
                person["phone1"] = val

        elif op == "4":
            val = get_phone(" Novo Segundo Telefone (ENTER remove): ", opcional=True)
            if val is not None:
                person["phone2"] = val

        elif op == "5":
            val = get_age (" Nova idade: ")
            if val is not None:
                person["Age"] = val

        elif op == "6":
            nova = get_text (" Nova Cidade: ")
            if nova is None:
                continue
            abbr = get_abbr (" Abreviação (2 letra): ")
            if abbr is None:
                continue
            person["city"] = nova
            person["city_abbr"] = abbr

        elif op == "7":
            val = get_text (" Nova cidadania: ")
            if val is not None:
                person["citizenship"] = val

        else:
            print("Opção Invalida")
            continue

        save(people)
        print("Salvo")


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
        print("3. Editar")
        print("4. Estatísticas")
        print("5. Remover")
        print("6. Sair")

        op = input("Opção: ").strip()

        if op == "1":
            register(people)
        elif op == "2":
            listar(people)
        elif op == "3":
            update(people)
        elif op == "4":
            stats(people)
        elif op == "5":
            remove(people)
        elif op == "6":
            r = input("\nSair mesmo? (s/n): ").strip().lower()
            if r == "s":
                print("Tchau!")
                break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()