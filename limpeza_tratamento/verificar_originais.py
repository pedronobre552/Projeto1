"""Comparar todos os valores dos CSV com os Excel, sem alterar os dados.

Esta leitura é independente de join.py e de auditoria.json. Reconstrói o
resultado esperado diretamente das fontes, admitindo apenas as transformações
documentadas. Guarda evidência local e termina com erro se houver diferenças.
"""

import argparse
from contextlib import ExitStack
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
# Mapa próprio: não importar o mapa nem as funções do gerador que se vai conferir.
SHEETS = {
    "30 Dias _ Acidentes": "acidentes", "30dias_acV": "acidentes",
    "30 Dias_Cond_Veic": "condutores_veiculos", "30dias_cond": "condutores_veiculos",
    "30 Dias_Passag": "passageiros", "30dias_psg": "passageiros",
    "30 Dias_Peões": "peoes", "30dias_peao": "peoes",
}
META = ["ficheiro_origem", "folha_origem", "linha_origem"]


def normalized_name(value):
    """Aplicar só as equivalências de cabeçalho expressamente autorizadas."""
    name = " ".join(str(value).split())
    name = re.sub(r"Gr\.Etario\s+\(", "Gr.Etario(", name)
    if name.startswith("Num. ") and name.endswith(" a 30 dias SUM"):
        name = name[:-4]
    return name


def source_layout(input_dir):
    """Reconstruir a cobertura real das fontes e o esquema completo de cada CSV."""
    layouts, schemas = {}, {}
    for path in sorted(input_dir.glob("acidentes-*.xlsx")):
        match = re.fullmatch(r"acidentes-(\d{4})\.xlsx", path.name)
        if not match:
            raise ValueError(f"Nome de fonte inesperado: {path.name}")
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
        layouts[path] = []
        try:
            found = set()
            for sheet in workbook:
                table = SHEETS.get(sheet.title)
                if table is None or table in found:
                    raise ValueError(f"Folha desconhecida/repetida: {path.name}/{sheet.title}")
                found.add(table)
                for number, row in enumerate(sheet.iter_rows(max_row=10, values_only=True), 1):
                    if "Id. Acidente" in row:
                        columns = {i: normalized_name(v) for i, v in enumerate(row) if v is not None}
                        break
                else:
                    raise ValueError(f"Cabeçalho ausente: {path.name}/{sheet.title}")
                names = list(columns.values())
                if len(set(names)) != len(names) or set(names).intersection(["ano", *META]):
                    raise ValueError(f"Cabeçalho ambíguo: {path.name}/{sheet.title}")
                schema = schemas.setdefault(table, [])
                schema.extend(name for name in names if name not in schema)
                layouts[path].append((sheet.title, table, match[1], number, columns))
            if found != set(SHEETS.values()):
                raise ValueError(f"Faltam entidades em {path.name}")
        finally:
            workbook.close()
    if not layouts:
        raise ValueError("Não foram encontrados Excel anuais")
    return layouts, {table: ["ano", *columns, *META] for table, columns in schemas.items()}


def csv_value(value, identifier=False):
    """Representação textual esperada: CSV não transporta o tipo/formato Excel."""
    value = getattr(value, "text", value)  # expressão de fórmula matricial, sem avaliar
    if value is None:
        return ""
    if identifier:
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return str(value).strip()
    return str(value)


def hashes(input_dir, csv_dir):
    """Fotografar os bytes antes/depois, detetando alterações durante a comparação."""
    result = {}
    paths = [*(('excel/' + p.name, p) for p in sorted(input_dir.glob('acidentes-*.xlsx'))),
             *(("csv/" + table + ".csv", csv_dir / (table + ".csv")) for table in sorted(set(SHEETS.values())))]
    for label, path in paths:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        result[label] = digest.hexdigest()
    return result


def validate(input_dir, csv_dir, report_dir):
    """Conferir todas as linhas e células, incluindo campos vazios e proveniência."""
    if report_dir.resolve() in {input_dir.resolve(), csv_dir.resolve()}:
        raise ValueError("Os relatórios devem ficar separados dos dados")
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {"inicio_utc": datetime.now(timezone.utc).isoformat(), "estado": "FALHOU",
              "linhas_comparadas": 0, "celulas_comparadas": 0, "divergencias": 0,
              "primeiras_divergencias": [], "fontes": []}

    def mismatch(context):
        # Guardar localização, não valores individuais, para reduzir dados no relatório.
        report["divergencias"] += 1
        if len(report["primeiras_divergencias"]) < 20:
            report["primeiras_divergencias"].append(context)

    try:
        report["sha256_antes"] = hashes(input_dir, csv_dir)
        layouts, schemas = source_layout(input_dir)
        with ExitStack() as stack:
            readers = {}
            for table, header in schemas.items():
                handle = stack.enter_context((csv_dir / f"{table}.csv").open(encoding="utf-8-sig", newline=""))
                readers[table] = csv.DictReader(handle)
                if readers[table].fieldnames != header:
                    raise ValueError(f"Cabeçalho do CSV diferente da união real das fontes: {table}")
            for path, sheets in layouts.items():
                print(f"A comparar com o original: {path.name}", flush=True)
                workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
                try:
                    for title, table, year, header_row, columns in sheets:
                        source_count = 0
                        for number, cells in enumerate(workbook[title].iter_rows(min_row=header_row + 1), header_row + 1):
                            values = [cell.value for cell in cells]
                            if all(v is None or v == "" for v in values):
                                continue
                            if any(v is not None and v != "" and i not in columns for i, v in enumerate(values)):
                                raise ValueError(f"Valor original sem cabeçalho: {path.name}/{title}:{number}")
                            expected = {name: csv_value(values[i] if i < len(values) else None, name == "Id. Acidente") for i, name in columns.items()}
                            expected.update(ano=year, ficheiro_origem=path.name, folha_origem=title, linha_origem=str(number))
                            actual = next(readers[table], None)
                            context = {"ficheiro": path.name, "folha": title, "linha": number, "tabela": table}
                            source_count += 1
                            report["linhas_comparadas"] += 1
                            if actual is None:
                                mismatch({**context, "erro": "linha ausente no CSV"})
                                continue
                            if None in actual or any(v is None for v in actual.values()):
                                mismatch({**context, "erro": "estrutura CSV inválida"})
                            for column in schemas[table]:
                                report["celulas_comparadas"] += 1
                                # Uma coluna estruturalmente ausente tem de ficar vazia.
                                if actual.get(column) != expected.get(column, ""):
                                    mismatch({**context, "coluna": column, "erro": "valor diferente"})
                        report["fontes"].append({"ficheiro": path.name, "folha": title, "tabela": table, "linhas": source_count})
                finally:
                    workbook.close()
            # Consumir os CSV até ao fim também deteta registos extra acrescentados.
            for table, reader in readers.items():
                for _ in reader:
                    mismatch({"tabela": table, "erro": "linha extra no CSV"})
        report["sha256_depois"] = hashes(input_dir, csv_dir)
        report["ficheiros_estaveis_durante_verificacao"] = report["sha256_antes"] == report["sha256_depois"]
        if not report["ficheiros_estaveis_durante_verificacao"]:
            mismatch({"erro": "ficheiro alterado durante a verificação"})
        if not report["divergencias"]:
            report["estado"] = "OK"
    except Exception as error:
        report["erro_execucao"] = f"{type(error).__name__}: {error}"
    report["fim_utc"] = datetime.now(timezone.utc).isoformat()
    report["sha256_script"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (report_dir / "comparacao_originais.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = (f"# Comparação direta com os originais\n\nEstado: **{report['estado']}**.\n\n"
               f"Linhas originais não vazias percorridas: {report['linhas_comparadas']:,}.\n\n"
               f"Células CSV comparadas, incluindo campos vazios e metadados: {report['celulas_comparadas']:,}.\n\n"
               f"Divergências: {report['divergencias']}. Fontes/folhas percorridas: {len(report['fontes'])}.\n\n"
               "A comparação é integral, sem amostragem, segundo as transformações descritas em docs/integridade.md. "
               "Os hashes SHA-256 identificam os ficheiros desta execução, não provam a sua história anterior nem a correção factual das fontes. "
               "Consultar comparacao_originais.json para o estado, erros, localizações e hashes.\n")
    (report_dir / "comparacao_originais.md").write_text(summary, encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("estado", "linhas_comparadas", "celulas_comparadas", "divergencias")}, ensure_ascii=True))
    if report["estado"] != "OK":
        raise ValueError("A comparação falhou; consultar comparacao_originais.json")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--csv-dir", type=Path, default=ROOT / "data_agregada")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "outputs" / "fase1")
    args = parser.parse_args()
    validate(args.input_dir, args.csv_dir, args.report_dir)
