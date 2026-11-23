"""Obter meteorologia diária ERA5 para os distritos de Portugal continental."""

import calendar
import csv
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://archive-api.open-meteo.com/v1/archive"
IPMA = "https://api.ipma.pt/open-data/distrits-islands.json"
CACHE = ROOT / "outputs" / "meteo_diaria" / "respostas"
DESTINO = ROOT / "meteo" / "meteorologia_diaria_portugal_continental.csv"
FUSO = "Europe/Lisbon"
DISTRITOS = (
    "Aveiro", "Beja", "Braga", "Bragança", "Castelo Branco", "Coimbra", "Évora",
    "Faro", "Guarda", "Leiria", "Lisboa", "Portalegre", "Porto", "Santarém",
    "Setúbal", "Viana do Castelo", "Vila Real", "Viseu",
)
VARIAVEIS = {
    "temperature_2m_mean": ("temperatura_media_c", "°C"),
    "precipitation_sum": ("precipitacao_total_mm", "mm"),
    "wind_speed_10m_max": ("vento_max_kmh", "km/h"),
    "cloud_cover_mean": ("nebulosidade_media_pct", "%"),
    "daylight_duration": ("duracao_dia_s", "s"),
    "sunshine_duration": ("horas_sol_s", "s"),
    "shortwave_radiation_sum": ("radiacao_total_mj_m2", "MJ/m²"),
}


def ler_json(url, ficheiro):
    if ficheiro.exists():
        return json.loads(ficheiro.read_bytes())
    for tentativa in range(3):
        try:
            pedido = Request(url, headers={"User-Agent": "PACD-Portugal/1.0"})
            with urlopen(pedido, timeout=150) as resposta:
                dados = resposta.read()
            conteudo = json.loads(dados)
            temporario = ficheiro.with_suffix(".tmp")
            temporario.write_bytes(dados)
            temporario.replace(ficheiro)
            return conteudo
        except HTTPError as erro:
            if tentativa == 2 or erro.code not in (429, 500, 502, 503, 504):
                raise
            espera = 60 if erro.code == 429 else (tentativa + 1) * 5
            retry_after = erro.headers.get("Retry-After", "")
            if retry_after.isdecimal():
                espera = max(espera, int(retry_after))
            print(f"API HTTP {erro.code} para {ficheiro.name}. Nova tentativa em {espera}s.", flush=True)
            time.sleep(espera)
        except (URLError, TimeoutError):
            if tentativa == 2:
                raise
            time.sleep((tentativa + 1) * 5)


def escrever_ponto(destino, area, ponto, resposta, dias):
    diario = resposta["daily"]
    if diario["time"] != dias or resposta["timezone"] != FUSO:
        raise ValueError(f"Datas ou fuso inesperados para {area}")
    for variavel, (_, unidade) in VARIAVEIS.items():
        if resposta["daily_units"][variavel] != unidade or len(diario[variavel]) != len(dias):
            raise ValueError(f"Unidade ou cobertura inesperada para {area}/{variavel}")
    for i, dia in enumerate(dias):
        destino.writerow({
            "area": area, "tipo_area": "distrito",
            "data": dia, "ponto_ipma": ponto["local"], "fuso": FUSO,
            "latitude_ponto": ponto["latitude"], "longitude_ponto": ponto["longitude"],
            "latitude_era5": resposta["latitude"], "longitude_era5": resposta["longitude"],
            **{coluna: diario[var][i] for var, (coluna, _) in VARIAVEIS.items()},
        })


def adquirir():
    CACHE.mkdir(parents=True, exist_ok=True)
    DESTINO.parent.mkdir(exist_ok=True)
    locais = {item["local"]: item for item in ler_json(IPMA, CACHE / "ipma.json")["data"]}
    pontos = {area: locais[area] for area in DISTRITOS}
    origem = {"fonte": ENDPOINT, "coordenadas": IPMA, "modelo": "ERA5", "consultas": []}
    total = 0
    temporario = DESTINO.with_suffix(".tmp")
    campos = ["area", "tipo_area", "data", "ponto_ipma", "fuso", "latitude_ponto",
              "longitude_ponto", "latitude_era5", "longitude_era5"]
    with temporario.open("w", encoding="utf-8-sig", newline="") as ficheiro:
        destino = csv.DictWriter(ficheiro, fieldnames=[*campos, *(c for c, _ in VARIAVEIS.values())])
        destino.writeheader()
        for ano in range(2010, 2025, 5):
            inicio = date(ano, 1, 1)
            fim = date(ano + 4, 12, 31)
            dias = [(inicio + timedelta(days=i)).isoformat() for i in range((fim - inicio).days + 1)]
            for pos in range(0, len(DISTRITOS), 6):
                lote = DISTRITOS[pos:pos + 6]
                parametros = {
                    "latitude": ",".join(pontos[area]["latitude"] for area in lote),
                    "longitude": ",".join(pontos[area]["longitude"] for area in lote),
                    "elevation": ",".join(["nan"] * len(lote)),
                    "start_date": inicio.isoformat(), "end_date": fim.isoformat(),
                    "daily": ",".join(VARIAVEIS), "models": "era5",
                    "timezone": FUSO, "cell_selection": "land",
                }
                url = f"{ENDPOINT}?{urlencode(parametros)}"
                cache = CACHE / f"era5_{ano}_Lisbon_{pos}.json"
                dados = ler_json(url, cache)
                if isinstance(dados, dict):
                    dados = [dados]
                for area, resposta in zip(lote, dados, strict=True):
                    ponto = pontos[area]
                    if (abs(float(ponto["latitude"]) - resposta["latitude"]) > 0.5
                            or abs(float(ponto["longitude"]) - resposta["longitude"]) > 0.5):
                        raise ValueError(f"A célula devolvida fica fora da vizinhança de {area}")
                    escrever_ponto(destino, area, ponto, resposta, dias)
                    total += len(dias)
                origem["consultas"].append({"areas": lote, "url": url, "cache": cache.name})
                print(f"{ano}–{ano + 4} {FUSO} | {', '.join(lote)}", flush=True)
    esperado = len(pontos) * sum(365 + calendar.isleap(ano) for ano in range(2010, 2025))
    if total != esperado:
        raise ValueError(f"Esperavam-se {esperado} linhas e foram obtidas {total}")
    temporario.replace(DESTINO)
    origem.update(linhas=total, obtido_em=datetime.now(timezone.utc).isoformat())
    (CACHE.parent / "origem_continente.json").write_text(
        json.dumps(origem, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{total} linhas guardadas em {DESTINO}", flush=True)


if __name__ == "__main__":
    adquirir()
