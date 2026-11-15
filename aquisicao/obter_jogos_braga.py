"""Recolher calendários públicos do Braga e gerar um CSV de jogos oficiais.

Uso: python aquisicao/obter_jogos_braga.py
As páginas ficam em outputs/jogos/transfermarkt/ e são reutilizadas.
Não lê nem transmite os ficheiros de acidentes.
"""

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.transfermarkt.pt"
# Só entram competições oficiais; nomes novos obrigam a rever a classificação.
OFICIAIS = {
    "Liga Portugal", "Liga Portugal Betclic", "Liga NOS", "Liga ZON Sagres",
    "UEFA Liga dos Campeões", "UEFA Liga Europa",
    "UEFA Liga dos Campeões - Fase de Qualificação",
    "UEFA Liga Europa - Fase de Qualificação",
    "Allianz Cup", "Taça da Liga", "Taça de Portugal",
    "Supertaça Cândido de Oliveira", "Supertaça", "UEFA Conference League",
    "UEFA Conference League - Fase de Qualificação",
    "UEFA Liga Conferência", "UEFA Liga Conferência - Fase de Qualificação",
}
COLUNAS = ["id_jogo", "epoca", "data", "hora_inicio_portugal", "competicao",
           "fase", "adversario", "condicao_braga_fonte", "resultado_fonte", "url_fonte"]


def texto(elemento):
    """Remover apenas espaços de apresentação, preservando o conteúdo."""
    return " ".join(elemento.text_content().split())


def extrair(pagina, ano):
    """Ler as linhas com relatório de jogo e rejeitar formatos inesperados."""
    arvore = html.fromstring(pagina)
    jogos = []
    contagens = Counter()
    for tabela in arvore.xpath("//table"):
        # Alguns jogos antigos têm resultado e link, mas não a classe ergebnis-link.
        linhas = tabela.xpath('.//tr[.//a[contains(@href,"/spielbericht/")]]')
        if not linhas:
            continue
        titulos = tabela.xpath('ancestor::div[contains(@class,"box")][1]//h2')
        if len(titulos) != 1:
            raise ValueError(f"{ano}: não foi possível identificar a competição")
        competicao = texto(titulos[0])
        if competicao not in OFICIAIS:
            raise ValueError(f"{ano}: rever competição não reconhecida: {competicao}")
        for linha in linhas:
            celulas = linha.xpath("./td")
            if len(celulas) < 8:
                raise ValueError(f"{ano}: estrutura da tabela alterada")
            data_texto = re.search(r"\d{2}/\d{2}/\d{4}", texto(celulas[1]))
            if not data_texto:
                raise ValueError(f"{ano}: data inválida: {texto(celulas[1])}")
            data = datetime.strptime(data_texto[0], "%d/%m/%Y").date()
            hora = texto(celulas[2])
            # A hora desconhecida fica vazia, nunca é substituída por meia-noite.
            if hora in {"-", "?", "", "A definir"}:
                hora = ""
            else:
                hora = datetime.strptime(hora, "%H:%M").strftime("%H:%M")
            condicao = texto(celulas[3])
            if condicao not in {"C", "F", "N"}:
                raise ValueError(f"{ano}: condição casa/fora inesperada: {condicao}")
            adversarios = linha.xpath('.//td[contains(@class,"no-border-links")]//a[@title]')
            resultado = linha.xpath('.//a[contains(@href,"/spielbericht/")]')
            if len(adversarios) != 1 or len(resultado) != 1:
                raise ValueError(f"{ano}: adversário/resultado ambíguo")
            id_jogo = re.search(r"/spielbericht/(\d+)", resultado[0].get("href", ""))
            if not id_jogo or not re.search(r"\d+\s*:\s*\d+", texto(resultado[0])):
                raise ValueError(f"{ano}: jogo sem resultado final identificável")
            if not ano <= data.year <= ano + 1:
                raise ValueError(f"{ano}: jogo fora da época: {data}")
            jogos.append(dict(zip(COLUNAS, [
                id_jogo[1], f"{ano}/{ano + 1}", data.isoformat(), hora, competicao,
                texto(celulas[0]), texto(adversarios[0]), condicao,
                texto(resultado[0]), BASE + resultado[0].get("href"),
            ])))
            contagens[competicao] += 1
    # Cada época completa deve conter 30 ou 34 jornadas do campeonato.
    liga = sum(n for c, n in contagens.items() if c.startswith("Liga "))
    esperado = 30 if ano < 2014 else 34
    if liga != esperado:
        raise ValueError(f"{ano}: campeonato com {liga} jogos, esperados {esperado}")
    if not any("Taça de Portugal" == c for c in contagens):
        raise ValueError(f"{ano}: Taça de Portugal ausente")
    if not any(c in {"Allianz Cup", "Taça da Liga"} for c in contagens):
        raise ValueError(f"{ano}: Taça da Liga ausente")
    return jogos, dict(contagens)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atualizar", action="store_true", help="Voltar a descarregar as páginas")
    args = parser.parse_args()
    cache = ROOT / "outputs/jogos/transfermarkt"
    cache.mkdir(parents=True, exist_ok=True)
    todos, fontes = {}, []
    for ano in range(2009, 2025):
        # São precisas as épocas 2009/10 e 2024/25 para cobrir os limites civis.
        url = f"{BASE}/sc-braga/spielplan/verein/1075/saison_id/{ano}"
        caminho = cache / f"{ano}.html"
        if args.atualizar or not caminho.exists():
            print(f"Descarregar época {ano}/{ano + 1}", flush=True)
            pedido = Request(url, headers={"User-Agent": "PACD-Braga-research/1.0"})
            with urlopen(pedido, timeout=60) as resposta:
                pagina = resposta.read()
            # Só guardar páginas que passem a validação, evitando cache de erros.
            extrair(pagina, ano)
            caminho.write_bytes(pagina)
            time.sleep(3)
        pagina = caminho.read_bytes()
        jogos, contagens = extrair(pagina, ano)
        fontes.append({"epoca": ano, "url": url, "ficheiro": str(caminho.relative_to(ROOT)),
                       "sha256": hashlib.sha256(pagina).hexdigest(),
                       "pagina_guardada_utc": datetime.fromtimestamp(caminho.stat().st_mtime, timezone.utc).isoformat(),
                       "jogos_por_competicao": contagens})
        for jogo in jogos:
            if "2010-01-01" <= jogo["data"] <= "2024-12-31":
                if jogo["id_jogo"] in todos:
                    raise ValueError(f"ID repetido: {jogo['id_jogo']}")
                todos[jogo["id_jogo"]] = jogo
    jogos = sorted(todos.values(), key=lambda j: (j["data"], j["hora_inicio_portugal"], j["id_jogo"]))
    destino = ROOT / "jogos/braga.csv"
    destino.parent.mkdir(exist_ok=True)
    # Publicar o CSV apenas depois de todas as épocas passarem as verificações.
    with destino.open("w", encoding="utf-8-sig", newline="") as ficheiro:
        writer = csv.DictWriter(ficheiro, fieldnames=COLUNAS, delimiter=";")
        writer.writeheader()
        writer.writerows(jogos)
    # Reler o ficheiro confirma que a escrita manteve todas as linhas e valores.
    with destino.open(encoding="utf-8-sig", newline="") as ficheiro:
        if list(csv.DictReader(ficheiro, delimiter=";")) != jogos:
            raise ValueError("O CSV gravado diverge dos jogos extraídos das páginas")
    auditoria = {"gerado_utc": datetime.now(timezone.utc).isoformat(), "fonte": "Transfermarkt (páginas públicas, sem API)",
                 "periodo": ["2010-01-01", "2024-12-31"], "linhas": len(jogos),
                 "por_ano": dict(sorted(Counter(j["data"][:4] for j in jogos).items())),
                 "horas_em_falta": sum(not j["hora_inicio_portugal"] for j in jogos),
                 "csv_sha256": hashlib.sha256(destino.read_bytes()).hexdigest(), "paginas": fontes}
    (ROOT / "outputs/jogos/origem.json").write_text(json.dumps(auditoria, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Criado {destino}: {len(jogos)} jogos. Origem e verificações em outputs/jogos/origem.json.")


if __name__ == "__main__":
    main()
