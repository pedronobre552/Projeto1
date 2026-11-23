"""Executar toda a preparação do projeto com um único comando: python executar.py."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ETAPAS = [
    ("Juntar os Excel anuais", "limpeza_tratamento/join.py"),
    ("Verificar a estrutura dos CSV", "limpeza_tratamento/verificar_resultados.py"),
    ("Comparar os CSV com os Excel originais", "limpeza_tratamento/verificar_originais.py"),
    ("Atualizar os dicionários", "limpeza_tratamento/gerar_dicionarios.py"),
    ("Obter meteorologia diária de Portugal continental", "aquisicao/obter_meteo_diaria.py"),
    ("Obter meteorologia e horas solares", "aquisicao/obter_meteo.py"),
    ("Obter jogos oficiais do Braga", "aquisicao/obter_jogos_braga.py"),
]


def main():
    """Usar o mesmo Python em todas as etapas e interromper perante qualquer erro."""
    for numero, (descricao, script) in enumerate(ETAPAS, 1):
        print(f"\n[{numero}/{len(ETAPAS)}] {descricao}", flush=True)
        try:
            subprocess.run([sys.executable, "-X", "utf8", str(ROOT / script)], cwd=ROOT, check=True)
        except subprocess.CalledProcessError as erro:
            print(f"\nProcesso interrompido na etapa {numero}: {descricao}.", file=sys.stderr)
            return erro.returncode
    print("\nConcluído: dados unidos, verificados, documentados, meteorologia e jogos obtidos.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
