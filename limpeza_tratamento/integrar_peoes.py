"""Integra contagens de peões por acidente, seguindo a metodologia do relatório."""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
KEY = "Id. Acidente"


def integrate(folder, district="Braga"):
    # A primeira fase preserva todas as entidades e todos os distritos.
    # Aqui a seleção é feita pelos acidentes, pois peões recentes não têm Distrito.
    accidents = {}
    with (folder / "acidentes.csv").open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames
        for row in reader:
            if row["Distrito"].strip().casefold() != district.strip().casefold():
                continue
            key = (row["ano"], row[KEY])
            if not key[1] or key in accidents:
                raise ValueError(f"Chave de acidente vazia ou repetida em {district}: {key}")
            accidents[key] = row
    if not accidents:
        raise ValueError(f"Sem acidentes para o distrito {district}")
    counts = Counter()
    pedestrians = set()
    with (folder / "peoes.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["ano"], row[KEY])
            if key not in accidents:
                continue
            person = (*key, row["Id. Peao"])
            if not person[-1] or person in pedestrians:
                raise ValueError(f"Chave de peão vazia ou repetida em {district}: {person}")
            pedestrians.add(person)
            counts[key] += 1

    # Não reproduz os indicadores/gráficos da análise posterior nesta fase.
    extra = ["peoes_envolvidos", "acidente_com_peoes"]
    if set(extra).intersection(columns):
        raise ValueError("Colunas de integração já presentes na origem")
    summary = {}
    with tempfile.TemporaryDirectory(prefix="integracao-", dir=folder) as temp:
        output = Path(temp) / "acidentes_distrito_com_peoes.csv"
        with output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[*columns, *extra])
            writer.writeheader()
            for key, row in accidents.items():
                count = counts[key]
                writer.writerow({**row, "peoes_envolvidos": count, "acidente_com_peoes": int(count > 0)})
                annual = summary.setdefault(key[0], {"acidentes": 0, "peoes_envolvidos": 0, "acidentes_com_peoes": 0})
                annual["acidentes"] += 1
                annual["peoes_envolvidos"] += count
                annual["acidentes_com_peoes"] += int(count > 0)
        if sum(v["peoes_envolvidos"] for v in summary.values()) != len(pedestrians):
            raise ValueError("A integração alterou a contagem de peões")
        result = {
            "distrito": district,
            "chave": ["ano", KEY],
            "metodo": "left join de acidentes com contagem de peões por acidente",
            "totais_por_ano": summary,
            "nota": "Peões sem acidente correspondente não são atribuídos a um distrito; consultar auditoria.json.",
        }
        (Path(temp) / "integracao_peoes.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        for path in Path(temp).iterdir():
            path.replace(folder / path.name)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=ROOT / "outputs" / "fase1")
    parser.add_argument("--district", default="Braga")
    args = parser.parse_args()
    integrate(args.folder, args.district)
