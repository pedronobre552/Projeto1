import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest
import re
import json

from limpeza_tratamento.gerar_dicionarios import generate
from limpeza_tratamento.verificar_resultados import verify
from limpeza_tratamento.verificar_originais import validate

from openpyxl import Workbook
from openpyxl.worksheet.formula import ArrayFormula

SPEC = importlib.util.spec_from_file_location("join", Path(__file__).resolve().parents[1] / "limpeza_tratamento" / "join.py")
join = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(join)


class JoinTests(unittest.TestCase):
    """Validar preservação e compatibilidade com fontes sintéticas, sem dados reais."""
    def make_source(self, folder, year, modern=False):
        workbook = Workbook()
        workbook.remove(workbook.active)
        names = list(join.TABLES)[4:] if modern else list(join.TABLES)[:4]
        for name in names:
            sheet = workbook.create_sheet(name)
            if modern:
                sheet.append([None])
            headers = [join.KEY, "Num. Mortos a 30 dias SUM" if modern else "Num. Mortos a 30 dias", "Datahora"]
            prefix = [None] if modern else []
            sheet.append(prefix + headers)
            sheet.append(prefix + [123, 0, f"{year}:01:01 12:00:00"])
            if join.TABLES[name] == "condutores_veiculos":
                sheet.append(prefix + [123, 0, f"{year}:01:01 12:00:00"])
                sheet.append(prefix + ["G0001/24", 0, f"{year}:01:01 12:00:00"])
        workbook.save(folder / f"acidentes-{year}.xlsx")
        workbook.close()

    def test_preserves_rows_and_audits_relationships(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_source(root, 2010)
            self.make_source(root, 2023, modern=True)
            report = join.run(root, root / "out")
            with (root / "out" / "condutores_veiculos.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 6)
            self.assertEqual([r["ano"] for r in rows], ["2010"] * 3 + ["2023"] * 3)
            self.assertEqual(rows[-1][join.KEY], "G0001/24")
            self.assertEqual(rows[3]["linha_origem"], "3")
            self.assertNotIn("Num. Mortos a 30 dias SUM", rows[0])
            self.assertEqual(report["tabelas"]["acidentes"]["linhas"], 2)
            for source in report["fontes"]:
                self.assertEqual(source["datas_ano_divergente"], 0)
                if source["tabela"] == "condutores_veiculos":
                    self.assertEqual(source["duplicados_exatos"], 1)
            for relation in report["relacoes"]:
                if relation["tabela"] == "condutores_veiculos":
                    self.assertEqual(relation["linhas_sem_acidente"], 1)
                    self.assertEqual(relation["acidentes_com_multiplas_linhas"], 1)

    def test_value_without_header_aborts_before_publishing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_source(root, 2024, modern=True)
            path = root / "acidentes-2024.xlsx"
            workbook = join.openpyxl.load_workbook(path)
            workbook.worksheets[-1]["E3"] = "sem cabecalho"
            workbook.save(path)
            workbook.close()
            output = root / "out"
            output.mkdir()
            (output / "acidentes.csv").write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Valor sem cabeçalho"):
                join.run(root, output)
            self.assertEqual((output / "acidentes.csv").read_text(), "existing")
            self.assertFalse((output / "auditoria.json").exists())

    def test_formula_is_preserved_as_text_and_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_source(root, 2024, modern=True)
            path = root / "acidentes-2024.xlsx"
            workbook = join.openpyxl.load_workbook(path)
            workbook.worksheets[-1]["C3"] = "=1+1"
            workbook.save(path)
            workbook.close()
            report = join.run(root, root / "out")
            source = next(s for s in report["fontes"] if s["tabela"] == "peoes")
            self.assertEqual(source["celulas_formulas_erros"][0]["conteudo_original"], "=1+1")
            with (root / "out" / "peoes.csv").open(encoding="utf-8-sig", newline="") as handle:
                self.assertEqual(next(csv.DictReader(handle))["Num. Mortos a 30 dias"], "=1+1")

    def test_array_formula_text_is_preserved(self):
        # Reproduzir o tipo de célula encontrado na fonte de 2023.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_source(root, 2023, modern=True)
            path = root / "acidentes-2023.xlsx"
            workbook = join.openpyxl.load_workbook(path)
            workbook.worksheets[-1]["C3"] = ArrayFormula(ref="C3", text="=- descricao sintetica")
            workbook.worksheets[-1]["D3"] = "#NAME?"
            workbook.save(path)
            workbook.close()
            report = join.run(root, root / "out")
            source = next(s for s in report["fontes"] if s["tabela"] == "peoes")
            self.assertEqual(len(source["celulas_formulas_erros"]), 2)
            with (root / "out" / "peoes.csv").open(encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["Num. Mortos a 30 dias"], "=- descricao sintetica")
            self.assertEqual(row["Datahora"], "#NAME?")
            self.assertEqual(validate(root, root / "out", root / "check")["estado"], "OK")

    def test_separate_folders_and_dictionary_cover_every_column(self):
        # Reproduzir a organização real sem recorrer aos ficheiros do utilizador.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_source(root, 2023, modern=True)
            csv_dir, report_dir = root / "csv", root / "reports"
            report = join.run(root, csv_dir, report_dir=report_dir)
            self.assertFalse((csv_dir / "auditoria.json").exists())
            self.assertTrue((report_dir / "auditoria.json").exists())
            verified = verify(csv_dir, report_dir)
            self.assertEqual(verified["acidentes"], 1)
            self.assertTrue((report_dir / "resumo_auditoria.md").exists())
            generate(csv_dir, report_dir / "auditoria.json", root / "dict")
            for table, info in report["tabelas"].items():
                text = (root / "dict" / f"{table}.md").read_text(encoding="utf-8")
                documented = re.findall(r"^\| `([^`]+)` \|", text, flags=re.MULTILINE)
                self.assertEqual(documented, info["colunas"])
            direct = validate(root, csv_dir, report_dir)
            self.assertEqual(direct["estado"], "OK")
            self.assertEqual(direct["linhas_comparadas"], 6)
            self.assertTrue(direct["ficheiros_estaveis_durante_verificacao"])

    def test_direct_comparison_detects_value_change_despite_same_counts(self):
        # As contagens e a proveniência mantêm-se; só muda uma medida.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_source(root, 2010)
            self.make_source(root, 2023, modern=True)
            csv_dir, report_dir = root / "csv", root / "reports"
            join.run(root, csv_dir, report_dir=report_dir)
            path = csv_dir / "acidentes.csv"
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                fields, rows = reader.fieldnames, list(reader)
            rows[0]["Num. Mortos a 30 dias"] = "99"
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            verify(csv_dir, report_dir)  # A verificação estrutural isolada não deteta isto.
            with self.assertRaisesRegex(ValueError, "comparação falhou"):
                validate(root, csv_dir, report_dir)
            result = json.loads((report_dir / "comparacao_originais.json").read_text(encoding="utf-8"))
            self.assertEqual(result["divergencias"], 1)
            self.assertEqual(result["primeiras_divergencias"][0]["coluna"], "Num. Mortos a 30 dias")

    def test_direct_comparison_detects_missing_extra_and_filled_absent_field(self):
        for mutation in ("missing", "extra", "absent_column"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                self.make_source(root, 2010)
                self.make_source(root, 2023, modern=True)
                # Uma coluna nova em 2023 tem de ficar vazia nas linhas de 2010.
                path = root / "acidentes-2023.xlsx"
                workbook = join.openpyxl.load_workbook(path)
                workbook.worksheets[0]["E2"] = "Ano"
                workbook.worksheets[0]["E3"] = 2023
                workbook.save(path)
                workbook.close()
                csv_dir, report_dir = root / "csv", root / "reports"
                join.run(root, csv_dir, report_dir=report_dir)
                path = csv_dir / "acidentes.csv"
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    reader = csv.DictReader(handle)
                    fields, rows = reader.fieldnames, list(reader)
                if mutation == "missing":
                    rows.pop()
                elif mutation == "extra":
                    rows.append(rows[-1].copy())
                else:
                    self.assertEqual(rows[0]["Ano"], "")
                    rows[0]["Ano"] = "0"
                with path.open("w", encoding="utf-8-sig", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)
                with self.assertRaisesRegex(ValueError, "comparação falhou"):
                    validate(root, csv_dir, report_dir)


if __name__ == "__main__":
    unittest.main()
