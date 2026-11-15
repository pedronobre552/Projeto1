import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("integrar", Path(__file__).resolve().parents[1] / "limpeza_tratamento" / "integrar_peoes.py")
integrar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integrar)


class IntegrationTests(unittest.TestCase):
    def write_csv(self, path, rows):
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def setup_sources(self, folder):
        self.write_csv(folder / "acidentes.csv", [
            {"ano": 2019, "Id. Acidente": "A", "Distrito": "Braga"},
            {"ano": 2023, "Id. Acidente": "A", "Distrito": "Braga"},
            {"ano": 2023, "Id. Acidente": "B", "Distrito": "Braga"},
            {"ano": 2023, "Id. Acidente": "C", "Distrito": "Porto"},
        ])
        self.write_csv(folder / "peoes.csv", [
            {"ano": 2019, "Id. Acidente": "A", "Id. Peao": 1},
            {"ano": 2019, "Id. Acidente": "A", "Id. Peao": 2},
            {"ano": 2023, "Id. Acidente": "A", "Id. Peao": 1},
            {"ano": 2023, "Id. Acidente": "C", "Id. Peao": 1},
            {"ano": 2023, "Id. Acidente": "ORFAO", "Id. Peao": 1},
        ])

    def test_join_preserves_accident_grain_and_separates_years(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.setup_sources(folder)
            result = integrar.integrate(folder)
            with (folder / "acidentes_distrito_com_peoes.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 3)
            self.assertEqual([r["peoes_envolvidos"] for r in rows], ["2", "1", "0"])
            self.assertEqual([r["acidente_com_peoes"] for r in rows], ["1", "1", "0"])
            self.assertEqual(result["totais_por_ano"]["2019"]["peoes_envolvidos"], 2)
            self.assertEqual(result["totais_por_ano"]["2023"]["peoes_envolvidos"], 1)

    def test_duplicate_pedestrian_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.setup_sources(folder)
            with (folder / "peoes.csv").open("a", encoding="utf-8", newline="") as handle:
                csv.writer(handle).writerow([2019, "A", 1])
            with self.assertRaisesRegex(ValueError, "peão vazia ou repetida"):
                integrar.integrate(folder)
            self.assertFalse((folder / "acidentes_distrito_com_peoes.csv").exists())


if __name__ == "__main__":
    unittest.main()
