import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

from openpyxl import Workbook

SPEC = importlib.util.spec_from_file_location("join", Path(__file__).resolve().parents[1] / "limpeza_tratamento" / "join.py")
join = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(join)


class JoinTests(unittest.TestCase):
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

    def test_formula_aborts_before_publishing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_source(root, 2024, modern=True)
            path = root / "acidentes-2024.xlsx"
            workbook = join.openpyxl.load_workbook(path)
            workbook.worksheets[-1]["C3"] = "=1+1"
            workbook.save(path)
            workbook.close()
            output = root / "out"
            output.mkdir()
            (output / "acidentes.csv").write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Fórmula/erro"):
                join.run(root, output)
            self.assertEqual((output / "acidentes.csv").read_text(), "existing")
            self.assertFalse((output / "auditoria.json").exists())


if __name__ == "__main__":
    unittest.main()
