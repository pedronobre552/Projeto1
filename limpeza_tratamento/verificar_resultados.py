"""Conferir os CSV contra a auditoria e escrever um resumo legível, apenas local."""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(folder):
    """Verificar esquema, ano, proveniência e contagens sem alterar os CSV."""
    report = json.loads((folder / "auditoria.json").read_text(encoding="utf-8"))
    if not report["csv_gerados"]:
        raise ValueError("A auditoria não corresponde a uma geração de CSV")
    sources = {(s["ficheiro"], s["folha"]): s for s in report["fontes"]}
    counts = Counter()
    previous_line = {}
    verified = {}
    for table, info in report["tabelas"].items():
        with (folder / f"{table}.csv").open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != info["colunas"]:
                raise ValueError(f"Cabeçalho divergente em {table}")
            total = 0
            for row in reader:
                # Uma vírgula mal escapada ou uma linha truncada altera a estrutura.
                if None in row or any(v is None for v in row.values()):
                    raise ValueError(f"Linha CSV inválida em {table}: {reader.line_num}")
                key = (row["ficheiro_origem"], row["folha_origem"])
                source = sources[key]
                if source["tabela"] != table or row["ano"] != str(source["ano"]):
                    raise ValueError(f"Ano/proveniência divergente em {table}")
                number = int(row["linha_origem"])
                if number <= previous_line.get(key, source["linha_cabecalho"]):
                    raise ValueError(f"Proveniência repetida ou fora de ordem em {table}")
                previous_line[key] = number
                counts[key] += 1
                total += 1
        if total != info["linhas"]:
            raise ValueError(f"Contagem divergente em {table}: {total}")
        verified[table] = total
    for key, source in sources.items():
        if counts[key] != source["linhas"]:
            raise ValueError(f"Contagem divergente para a fonte {key}")

    # O resumo contém diagnósticos dos dados e fica na pasta excluída do Git.
    lines = [
        "# Fase 1 — Resultados da auditoria e validação", "",
        "União vertical de todos os anos, separada por entidade. Sem filtros geográficos, seleção de variáveis ou agregações.", "",
        "Anos disponíveis: " + ", ".join(map(str, report["anos"])) + ".",
        "Anos em falta no intervalo: " + (", ".join(map(str, report["anos_em_falta"])) or "nenhum") + ".", "",
        "## CSV validados", "", "| Tabela | Linhas |", "| --- | ---: |",
    ]
    lines += [f"| {table} | {total:,} |" for table, total in verified.items()]
    lines += ["", "Validação: cabeçalhos, número de campos, ano e contagens por ficheiro/folha correspondem à auditoria. A linha de origem é única e crescente em cada fonte.", "",
              "## Diagnósticos por fonte", "",
              "Duplicados são registos integralmente iguais dentro da mesma folha. Foram preservados. Nas entidades de pessoas, repetir o ID de acidente é esperado e não implica duplicação da pessoa.", "",
              "| Ano | Tabela | Linhas | Duplicados exatos | IDs vazios | Datas inválidas | Ano data divergente | Ano original divergente | Fórmulas/erros |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for source in report["fontes"]:
        lines.append(f"| {source['ano']} | {source['tabela']} | {source['linhas']} | {source['duplicados_exatos']} | {source['id_vazio']} | {source['datas_invalidas']} | {source['datas_ano_divergente']} | {source['ano_original_divergente']} | {len(source['celulas_formulas_erros'])} |")
    lines += ["", "## Correspondência para futuros joins", "",
              "| Ano | Tabela | IDs sem acidente | Linhas sem acidente | Acidentes com várias linhas na entidade |",
              "| --- | --- | ---: | ---: | ---: |"]
    for relation in report["relacoes"]:
        lines.append(f"| {relation['ano']} | {relation['tabela']} | {relation['ids_sem_acidente']} | {relation['linhas_sem_acidente']} | {relation['acidentes_com_multiplas_linhas']} |")
    lines += ["", "Os IDs sem correspondência não impedem a concatenação dos anos. Impedem associar com segurança essas linhas a um acidente usando a chave atual. Foram preservados nos respetivos CSV.", "",
              "Uma junção direta entre várias entidades de pessoas pode multiplicar registos. A chave para futuras relações é `(ano, Id. Acidente)`; definir primeiro a unidade de análise e as agregações.", "",
              "## Limitações e próximos passos", "",
              "Datas, categorias e coordenadas mantêm os valores originais. Colunas ausentes por ano ficam vazias. Fórmulas/erros são texto e estão localizados em auditoria.json. A equivalência semântica das categorias e formatos exige tratamento posterior.", "",
              "Antes da seleção de variáveis, definir o objetivo futuro. Não houve seleção por Braga nem extração dos indicadores do relatório da Parte I.", ""]
    (folder / "resumo_auditoria.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"validacao": "OK", "linhas_por_tabela": verified}, ensure_ascii=False))
    return verified


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=ROOT / "outputs" / "fase1")
    verify(parser.parse_args().folder)
