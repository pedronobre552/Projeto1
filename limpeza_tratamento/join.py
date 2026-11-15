"""Fase 1: auditar e concatenar os Excel anuais em quatro CSV locais.

Conserva todos os anos, distritos, colunas e registos não vazios de cada entidade.
Acrescenta o ano do ficheiro e a proveniência. Não filtra, agrega nem cruza
entidades: essas decisões dependem do objetivo da análise futura.
Ver docs/fase1.md para o procedimento e as regras de validação.
"""

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import tempfile

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    "30 Dias_Cond_Veic": "condutores_veiculos",
    "30 Dias_Passag": "passageiros",
    "30 Dias _ Acidentes": "acidentes",
    "30 Dias_Peões": "peoes",
    "30dias_acV": "acidentes",
    "30dias_cond": "condutores_veiculos",
    "30dias_psg": "passageiros",
    "30dias_peao": "peoes",
}
KEY = "Id. Acidente"
RESERVED = {"ano", "ficheiro_origem", "folha_origem", "linha_origem"}


def canonical_header(value):
    """Uniformizar apenas variantes conhecidas do mesmo nome de coluna.

    Não remover SUM dos grupos etários: a regra aplica-se só aos contadores
    de vítimas a 30 dias. Não normalizar categorias nem os valores das células.
    """
    text = re.sub(r"\s+", " ", str(value).strip())
    text = re.sub(r"Gr\.Etario\s+\(", "Gr.Etario(", text)
    if text.startswith("Num. ") and text.endswith(" a 30 dias SUM"):
        text = text.removesuffix(" SUM")
    return text


def find_header(sheet):
    """Encontrar o cabeçalho real, mesmo com margens vazias como em 2023.

    Guardar os índices originais evita deslocar dados quando há colunas vazias.
    Rejeitar colisões impede que um dicionário elimine silenciosamente colunas.
    """
    for number, row in enumerate(sheet.iter_rows(max_row=10, values_only=True), 1):
        if KEY in row:
            columns = {i: canonical_header(v) for i, v in enumerate(row) if v is not None}
            names = list(columns.values())
            if len(set(names)) != len(names) or RESERVED.intersection(names):
                raise ValueError(f"Cabeçalhos duplicados/reservados: {sheet.title}")
            return number, columns
    raise ValueError(f"Cabeçalho com {KEY!r} não encontrado: {sheet.title}")


def key_text(value):
    """Representar IDs como texto, preservando códigos e zeros em IDs textuais."""
    # IDs são identificadores: não converter códigos alfanuméricos em números.
    if value is None or value == "":
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def year_from_date(value):
    """Ler o ano apenas para auditoria, sem modificar a data original."""
    if isinstance(value, (datetime, date)):
        return value.year
    if isinstance(value, str):
        for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value.strip(), fmt).year
            except ValueError:
                pass
    return None


def run(input_dir, output_dir, audit_only=False, report_dir=None):
    """Descobrir esquemas, auditar todas as linhas e publicar os CSV completos.

    Uma primeira passagem lê só os cabeçalhos para construir a união das colunas.
    A segunda lê em streaming para não carregar os ficheiros completos em RAM.
    Não existem operações de rede nem comandos Git nesta função.
    """
    # Separar os CSV finais dos relatórios; chamadas antigas podem usar uma só pasta.
    report_dir = report_dir or output_dir
    files = sorted(input_dir.glob("acidentes-*.xlsx"))
    if not files:
        raise ValueError(f"Sem ficheiros acidentes-AAAA.xlsx em {input_dir}")
    # Ordem estável: colunas do primeiro ano, seguidas das novas colunas.
    schemas = defaultdict(list)
    sources = []
    years = []
    for path in files:
        match = re.fullmatch(r"acidentes-(\d{4})\.xlsx", path.name)
        if not match:
            raise ValueError(f"Nome de ficheiro inesperado: {path.name}")
        year = int(match[1])
        years.append(year)
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            found = set()
            for sheet in workbook:
                if sheet.title not in TABLES:
                    raise ValueError(f"Folha desconhecida: {path.name}/{sheet.title}")
                table = TABLES[sheet.title]
                if table in found:
                    raise ValueError(f"Tabela repetida em {path.name}: {table}")
                found.add(table)
                header_row, columns = find_header(sheet)
                for name in columns.values():
                    if name not in schemas[table]:
                        schemas[table].append(name)
                sources.append((path, year, sheet.title, table, header_row, columns))
            if found != set(TABLES.values()):
                raise ValueError(f"Faltam tabelas em {path.name}")
        finally:
            workbook.close()

    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "anos": years,
        "anos_em_falta": sorted(set(range(min(years), max(years) + 1)) - set(years)),
        "operacao": "concatenação vertical por entidade; sem join entre entidades",
        "chave_relacional": ["ano", KEY],
        "fontes": [],
        "relacoes": [],
        "tabelas": {},
    }
    # O ano faz parte da chave: IDs iguais em anos diferentes não são confundidos.
    # Repetições nas tabelas de pessoas são esperadas e não são eliminadas.
    keys = defaultdict(Counter)
    totals = Counter()
    # Publicar apenas depois de concluir a leitura e a validação de todas as fontes.
    with tempfile.TemporaryDirectory(prefix="join-", dir=output_dir) as temp:
        handles, writers = {}, {}
        try:
            if not audit_only:
                for table, columns in schemas.items():
                    handles[table] = (Path(temp) / f"{table}.csv").open("w", encoding="utf-8-sig", newline="")
                    writers[table] = csv.DictWriter(handles[table], fieldnames=["ano", *columns, "ficheiro_origem", "folha_origem", "linha_origem"])
                    writers[table].writeheader()
            for path, year, title, table, header_row, columns in sources:
                print(f"A processar {year}: {table}", flush=True)
                workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
                stats = {
                    "ficheiro": path.name, "ano": year, "folha": title, "tabela": table,
                    "linha_cabecalho": header_row, "linhas": 0, "linhas_vazias": 0,
                    "id_vazio": 0, "duplicados_exatos": 0, "datas_invalidas": 0,
                    "datas_ano_divergente": 0, "ano_original_divergente": 0,
                    "celulas_formulas_erros": [],
                    "colunas_ausentes": sorted(set(schemas[table]) - set(columns.values())),
                }
                # Os perfis registam diferenças sem imputar nem converter valores.
                nulls, types = Counter(), defaultdict(Counter)
                seen = set()
                try:
                    sheet = workbook[title]
                    for number, cells in enumerate(sheet.iter_rows(min_row=header_row + 1), header_row + 1):
                        values = [cell.value for cell in cells]
                        if all(v is None or v == "" for v in values):
                            stats["linhas_vazias"] += 1
                            continue
                        for i, cell in enumerate(cells):
                            if cell.data_type in {"f", "e"}:
                                # Alguns textos foram interpretados como fórmulas no Excel
                                # original. Preservar a expressão, sem a avaliar nem apagar.
                                expression = getattr(cell.value, "text", cell.value)
                                values[i] = expression
                                stats["celulas_formulas_erros"].append({
                                    "celula": cell.coordinate, "tipo": cell.data_type,
                                    "conteudo_original": str(expression),
                                })
                        if any(v is not None and v != "" and i not in columns for i, v in enumerate(values)):
                            raise ValueError(f"Valor sem cabeçalho em {path.name}/{title}:{number}")
                        record = {name: values[i] if i < len(values) else None for i, name in columns.items()}
                        identifier = key_text(record.get(KEY))
                        if not identifier:
                            stats["id_vazio"] += 1
                        else:
                            keys[(year, table)][identifier] += 1
                        # Comparar o registo inteiro, antes de adicionar a proveniência.
                        # Detetar duplicados não autoriza removê-los nesta fase.
                        digest = hashlib.sha256(json.dumps(record, ensure_ascii=False, default=str, sort_keys=True).encode()).digest()
                        stats["duplicados_exatos"] += int(digest in seen)
                        seen.add(digest)
                        if "Datahora" in record:
                            date_year = year_from_date(record["Datahora"])
                            stats["datas_invalidas"] += int(date_year is None)
                            stats["datas_ano_divergente"] += int(date_year is not None and date_year != year)
                        if "Ano" in record:
                            stats["ano_original_divergente"] += int(key_text(record["Ano"]) != str(year))
                        for name, value in record.items():
                            nulls[name] += int(value is None or value == "")
                            if value is not None and value != "":
                                types[name][type(value).__name__] += 1
                        record[KEY] = identifier
                        if not audit_only:
                            writers[table].writerow({"ano": year, **record, "ficheiro_origem": path.name, "folha_origem": title, "linha_origem": number})
                        stats["linhas"] += 1
                        totals[table] += 1
                finally:
                    workbook.close()
                stats["nulos_por_coluna"] = dict(nulls)
                stats["tipos_por_coluna"] = {k: dict(v) for k, v in types.items()}
                stats["ids_distintos"] = len(keys[(year, table)])
                stats["ids_repetidos"] = sum(v > 1 for v in keys[(year, table)].values())
                report["fontes"].append(stats)
        finally:
            for handle in handles.values():
                handle.close()

        # Medir a compatibilidade para futuros joins sem executar um join 1:N:N.
        # Linhas órfãs continuam no CSV da entidade e são contabilizadas no relatório.
        for year in years:
            parent = keys[(year, "acidentes")]
            for table in ("condutores_veiculos", "passageiros", "peoes"):
                children = keys[(year, table)]
                orphan = children.keys() - parent.keys()
                report["relacoes"].append({
                    "ano": year, "tabela": table,
                    "ids_sem_acidente": len(orphan),
                    "linhas_sem_acidente": sum(children[k] for k in orphan),
                    "acidentes_com_multiplas_linhas": sum(v > 1 for v in children.values()),
                })
        for table, count in totals.items():
            report["tabelas"][table] = {"linhas": count, "colunas": ["ano", *schemas[table], "ficheiro_origem", "folha_origem", "linha_origem"]}
        report["csv_gerados"] = not audit_only
        (Path(temp) / "auditoria.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        for path in Path(temp).iterdir():
            destination = report_dir if path.name == "auditoria.json" else output_dir
            path.replace(destination / path.name)
    print(json.dumps({"tabelas": dict(totals), "anos_em_falta": report["anos_em_falta"], "csv_gerados": not audit_only}, ensure_ascii=False), flush=True)
    return report


def main():
    """Permitir execução a partir de qualquer pasta, com caminhos configuráveis."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data_agregada")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "outputs" / "fase1")
    parser.add_argument("--audit-only", action="store_true", help="Gerar apenas o relatório de auditoria")
    args = parser.parse_args()
    if args.input_dir.resolve() in {args.output_dir.resolve(), args.report_dir.resolve()}:
        parser.error("As pastas de saída devem ser diferentes da pasta de origem")
    run(args.input_dir, args.output_dir, args.audit_only, args.report_dir)


if __name__ == "__main__":
    main()
