from storage import load, save
from validator import (
    get_first_name,
    get_last_name,
    get_citizenship,
    get_state,
    get_city,
    get_phone,
    get_age,
)


def cadastrar_pessoa():
    dados = {}
    etapa = 0

    while etapa < 7:
        if etapa == 0:
            nome = get_first_name("\nNome (0 sai): ")
            if nome is None:
                return None
            dados["nome"] = nome
            etapa += 1

        elif etapa == 1:
            sobrenome = get_last_name("Sobrenome (0 volta): ")
            if sobrenome is None:
                etapa -= 1
                continue
            dados["sobrenome"] = sobrenome
            etapa += 1

        elif etapa == 2:
            idade = get_age("Idade (0 volta): ")
            if idade is None:
                etapa -= 1
                continue
            dados["idade"] = idade
            etapa += 1

        elif etapa == 3:
            pais, iso, ddi = get_citizenship()
            if pais is None:
                etapa -= 1
                continue
            dados["pais"] = pais
            dados["iso_pais"] = iso
            dados["ddi"] = ddi
            etapa += 1

        elif etapa == 4:
            estado, uf = get_state(dados["iso_pais"])
            if estado is None:
                etapa -= 1
                continue
            dados["estado"] = estado
            dados["sigla_estado"] = uf
            etapa += 1

        elif etapa == 5:
            cidade = get_city(dados["iso_pais"], dados["sigla_estado"], dados["estado"])
            if cidade is None:
                etapa -= 1
                continue
            dados["cidade"] = cidade
            etapa += 1

        elif etapa == 6:
            tel = get_phone("Telefone (0 volta): ", ddi=dados["ddi"])
            if tel is None:
                etapa -= 1
                continue
            dados["telefone"] = tel
            etapa += 1

    return dados


def listar(cadastros):
    if not cadastros:
        print("\nNenhum cadastro.")
        return

    print(f"\n=== CADASTROS ({len(cadastros)}) ===")
    for i, p in enumerate(cadastros, 1):
        nome_completo = f"{p['nome']} {p.get('sobrenome', '')}".strip()
        print(
            f"  {i}. {nome_completo} ({p['idade']}) - {p['cidade']}/{p['sigla_estado']} "
            f"({p['pais']}) - Tel: {p['telefone']}"
        )


def editar(cadastros):
    if not cadastros:
        print("\nNenhum cadastro.")
        return

    listar(cadastros)

    while True:
        e = input("\nNúmero do cadastro pra editar (0 volta): ").strip()
        if e == "0":
            return
        try:
            i = int(e)
            if 1 <= i <= len(cadastros):
                p = cadastros[i - 1]
                break
            print(f"  Fora do intervalo (1 a {len(cadastros)}).")
        except ValueError:
            print("  Digite só o número.")

    while True:
        nome_completo = f"{p['nome']} {p.get('sobrenome', '')}".strip()
        print(f"\nEditando: {nome_completo}")
        print(f"  1. Nome ({p['nome']})")
        print(f"  2. Sobrenome ({p.get('sobrenome', '')})")
        print(f"  3. Idade ({p['idade']})")
        print(f"  4. Localização ({p['cidade']}/{p['sigla_estado']} - {p['pais']})")
        print(f"  5. Telefone ({p['telefone']})")
        print("  0. Voltar")

        op = input("\nCampo: ").strip()

        if op == "0":
            return

        if op == "1":
            novo = get_first_name("Novo nome (0 volta): ")
            if novo:
                p["nome"] = novo
                save(cadastros)

        elif op == "2":
            novo = get_last_name("Novo sobrenome (0 volta): ")
            if novo:
                p["sobrenome"] = novo
                save(cadastros)

        elif op == "3":
            nova = get_age("Nova idade (0 volta): ")
            if nova is not None:
                p["idade"] = nova
                save(cadastros)

        elif op == "4":
            pais, iso, ddi = get_citizenship()
            if pais is None:
                continue
            estado, uf = get_state(iso)
            if estado is None:
                continue
            cidade = get_city(iso, uf, estado)
            if cidade is None:
                continue
            p["pais"] = pais
            p["iso_pais"] = iso
            p["ddi"] = ddi
            p["estado"] = estado
            p["sigla_estado"] = uf
            p["cidade"] = cidade
            save(cadastros)

        elif op == "5":
            novo = get_phone("Novo telefone (0 volta): ", ddi=p["ddi"])
            if novo:
                p["telefone"] = novo
                save(cadastros)

        else:
            print("  Opção inválida.")


def estatisticas(cadastros):
    if not cadastros:
        print("\nNenhum cadastro.")
        return

    idades = [p["idade"] for p in cadastros]
    velho = max(cadastros, key=lambda p: p["idade"])
    novo = min(cadastros, key=lambda p: p["idade"])

    por_pais = {}
    for p in cadastros:
        por_pais[p["pais"]] = por_pais.get(p["pais"], 0) + 1

    velho_nome = f"{velho['nome']} {velho.get('sobrenome', '')}".strip()
    novo_nome = f"{novo['nome']} {novo.get('sobrenome', '')}".strip()

    print("\n=== ESTATÍSTICAS ===")
    print(f"  Total: {len(cadastros)}")
    print(f"  Média: {sum(idades) / len(idades):.1f} anos")
    print(f"  Mais velho: {velho_nome} ({velho['idade']})")
    print(f"  Mais novo: {novo_nome} ({novo['idade']})")
    print("  Por país:")
    for pais, qtd in sorted(por_pais.items(), key=lambda x: x[1], reverse=True):
        print(f"    {pais}: {qtd}")


def remover(cadastros):
    if not cadastros:
        print("\nNenhum cadastro.")
        return

    listar(cadastros)

    while True:
        e = input("\nNúmero pra remover (0 volta): ").strip()
        if e == "0":
            return
        try:
            i = int(e)
            if 1 <= i <= len(cadastros):
                alvo = cadastros[i - 1]
                nome_completo = f"{alvo['nome']} {alvo.get('sobrenome', '')}".strip()
                r = input(f"  Remover '{nome_completo}'? (s/n): ").strip().lower()
                if r == "s":
                    cadastros.pop(i - 1)
                    save(cadastros)
                return
            print(f"  Fora do intervalo (1 a {len(cadastros)}).")
        except ValueError:
            print("  Digite só o número.")


def main():
    cadastros = load()

    while True:
        print("\n=== CADASTRO ===")
        print("  1. Cadastrar")
        print("  2. Listar")
        print("  3. Editar")
        print("  4. Estatísticas")
        print("  5. Remover")
        print("  0. Sair")

        opcao = input("\nOpção: ").strip()

        if opcao == "1":
            pessoa = cadastrar_pessoa()
            if pessoa:
                cadastros.append(pessoa)
                save(cadastros)
                print(f"\n{pessoa['nome']} cadastrado(a).")

        elif opcao == "2":
            listar(cadastros)
            input("\nENTER pra voltar...")

        elif opcao == "3":
            editar(cadastros)

        elif opcao == "4":
            estatisticas(cadastros)
            input("\nENTER pra voltar...")

        elif opcao == "5":
            remover(cadastros)

        elif opcao == "0":
            r = input("\nSair mesmo? (s/n): ").strip().lower()
            if r == "s":
                break
        else:
            print("  Opção inválida.")


if __name__ == "__main__":
    main()