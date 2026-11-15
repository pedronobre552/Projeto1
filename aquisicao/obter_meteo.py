"""Obter dois CSV simples: meteorologia horária e nascer/pôr do sol diário."""

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "outputs" / "meteo" / "respostas"
ENDPOINT = "https://archive-api.open-meteo.com/v1/archive"
LISBON = ZoneInfo("Europe/Lisbon")

# Pontos de referência do IPMA. Nunca são usadas coordenadas dos acidentes.
MUNICIPIOS = {
    "Amares": (41.6314, -8.3489), "Barcelos": (41.54, -8.61),
    "Braga": (41.5475, -8.4227), "Cabeceiras de Basto": (41.514, -7.9901),
    "Celorico de Basto": (41.39, -8.0), "Esposende": (41.5356, -8.7819),
    "Fafe": (41.4472, -8.1732), "Guimarães": (41.4434, -8.2938),
    "Póvoa de Lanhoso": (41.5762, -8.2708), "Terras de Bouro": (41.72, -8.31),
    "Vieira do Minho": (41.6355, -8.1416), "Vila Nova de Famalicão": (41.4087, -8.5205),
    "Vila Verde": (41.6545, -8.4348), "Vizela": (41.38, -8.31),
}
# Os pontos municipais correspondem a seis células ERA5 de 0,25°.
# Consultar cada célula uma vez evita pedidos repetidos para concelhos vizinhos.
GRELHAS = {nome: (round(lat*4)/4, round(lon*4)/4) for nome,(lat,lon) in MUNICIPIOS.items()}
VARIAVEIS = {
    "temperature_2m": "temperatura_c", "relative_humidity_2m": "humidade_pct",
    "precipitation": "precipitacao_mm", "cloud_cover": "nebulosidade_pct",
    "wind_speed_10m": "vento_kmh", "weather_code": "codigo_tempo_wmo",
    "shortwave_radiation": "radiacao_solar_w_m2", "direct_radiation": "radiacao_direta_w_m2",
}


def hora_portugal(valor):
    """Converter UTC para hora legal portuguesa, respeitando a hora de verão."""
    return datetime.fromisoformat(valor).replace(tzinfo=timezone.utc).astimezone(LISBON)


def adquirir(ultimo_ano=2024):
    """Guardar os valores API sem criar indicadores ou juntar aos acidentes."""
    pasta = ROOT / "meteo"
    pasta.mkdir(exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    pontos = sorted(set(GRELHAS.values()))
    origem = {"fonte": "Open-Meteo Historical Weather API", "modelo": "ERA5",
              "periodo": f"2010-01-01 a {ultimo_ano}-12-31", "coordenadas_concelhos": MUNICIPIOS,
              "fonte_coordenadas": "https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d0.json",
              "consultas": []}
    horas_temp, sol_temp = pasta / "meteorologia_horaria.csv.tmp", pasta / "sol_diario.csv.tmp"
    total_horas, total_dias, ultimo_pedido = 0, 0, 0.0
    with horas_temp.open("w", encoding="utf-8-sig", newline="") as fh, sol_temp.open("w", encoding="utf-8-sig", newline="") as fs:
        horas = csv.DictWriter(fh, fieldnames=["municipio", "data_hora_utc", "data_hora_local", *VARIAVEIS.values()])
        sol = csv.DictWriter(fs, fieldnames=["municipio", "data", "nascer_sol", "por_sol"])
        horas.writeheader()
        sol.writeheader()
        for ano in range(2010, ultimo_ano+1):
            parametros = {"latitude": ",".join(str(p[0]) for p in pontos),
                          "longitude": ",".join(str(p[1]) for p in pontos),
                          "start_date": f"{ano}-01-01", "end_date": f"{ano}-12-31",
                          "hourly": ",".join(VARIAVEIS), "daily": "sunrise,sunset",
                          "models": "era5", "timezone": "GMT", "cell_selection": "nearest",
                          "elevation": ",".join("nan" for _ in pontos)}
            url = ENDPOINT + "?" + urlencode(parametros)
            resposta = CACHE / f"{ano}.json"
            if not resposta.exists():
                # Consultas longas contam como vários pedidos: respeitar a quota da API.
                espera = max(0, 30 - (time.monotonic()-ultimo_pedido))
                if espera:
                    time.sleep(espera)
                ultimo_pedido = time.monotonic()
                while True:
                    try:
                        with urlopen(Request(url, headers={"User-Agent": "PACD-Braga/1.0"}), timeout=180) as api:
                            dados = api.read()
                        break
                    except HTTPError as erro:
                        if erro.code != 429:
                            raise
                        # Uma única execução pode aguardar a quota sem perder os anos obtidos.
                        espera_api = max(60, int(erro.headers.get("Retry-After", "60"))) + 2
                        print(f"Quota da API: a aguardar {espera_api}s antes de retomar.", flush=True)
                        time.sleep(espera_api)
                json.loads(dados)
                resposta.write_bytes(dados)
            dados = json.loads(resposta.read_bytes())
            por_ponto = {(p["latitude"], p["longitude"]): p for p in dados}
            for municipio, ponto in GRELHAS.items():
                resposta_ponto = por_ponto[ponto]
                horario, diario = resposta_ponto["hourly"], resposta_ponto["daily"]
                dias = (datetime(ano+1,1,1)-datetime(ano,1,1)).days
                if len(horario["time"]) != dias*24 or len(diario["time"]) != dias:
                    raise ValueError(f"Cobertura incompleta em {ano}/{municipio}")
                for i, instante in enumerate(horario["time"]):
                    horas.writerow({"municipio": municipio, "data_hora_utc": instante+"+00:00",
                                    "data_hora_local": hora_portugal(instante).isoformat(),
                                    **{coluna: horario[variavel][i] for variavel,coluna in VARIAVEIS.items()}})
                    total_horas += 1
                for i, dia in enumerate(diario["time"]):
                    sol.writerow({"municipio": municipio, "data": dia,
                                  "nascer_sol": hora_portugal(diario["sunrise"][i]).strftime("%H:%M"),
                                  "por_sol": hora_portugal(diario["sunset"][i]).strftime("%H:%M")})
                    total_dias += 1
            origem["consultas"].append({"ano": ano, "url": url, "resposta": str(resposta.relative_to(ROOT))})
            print(f"{ano} concluído", flush=True)
    horas_temp.replace(pasta / "meteorologia_horaria.csv")
    sol_temp.replace(pasta / "sol_diario.csv")
    origem.update(linhas_horarias=total_horas, linhas_sol=total_dias, obtido_utc=datetime.now(timezone.utc).isoformat())
    (CACHE.parent / "origem.json").write_text(json.dumps(origem, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Concluído: {total_horas} linhas horárias e {total_dias} linhas diárias", flush=True)


if __name__ == "__main__":
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("--ate", type=int, choices=range(2010,2025), default=2024, help="Último ano a incluir")
    adquirir(argumentos.parse_args().ate)
