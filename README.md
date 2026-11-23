# Projeto de acidentes rodoviários

Base nacional de acidentes rodoviários. Os dados ficam locais e o repositório
versiona o código, os testes, a documentação e o notebook sem resultados guardados.

## Foco atual — previsão diária por tipo de acidente

O objetivo é prever as contagens diárias de despistes, colisões e
atropelamentos em Portugal continental. O filtro inclui os 18 distritos
continentais e aplica-se aos acidentes antes da agregação. A unidade de análise
é o dia civil. O período de desenvolvimento
vai de 2010 a 2019, 2023 serve para validação temporal e 2024 fica reservado para
o teste final. O ficheiro de acidentes não cobre 2020–2022.

O [notebook de preparação](analise/preparar_serie_diaria.ipynb) constrói a base
diária usada pelo [notebook de análise exploratória](analise/eda_acidentes_diarios.ipynb).
Os ficheiros e o fluxo de trabalho estão descritos no [guia da pasta de análise](analise/README.md).
A fase de modelação vai comparar SARIMA e redes neuronais por
tipo de acidente. A meteorologia ERA5 do próprio dia permite uma avaliação
retrospetiva. Uma previsão operacional precisa de informação meteorológica
disponível antes do dia-alvo.

## Onde está cada coisa

| Pasta | Conteúdo |
| --- | --- |
| `data/` | Excel anuais originais, preservados |
| `data_agregada/` | Quatro CSV finais, com todos os anos e `ano` |
| `meteo/` | Meteorologia diária dos 18 distritos continentais e, para Braga, meteorologia horária e horas solares por concelho |
| `jogos/` | CSV dos jogos oficiais do Braga, 2010–2024 |
| `aquisicao/` | Scripts de aquisição da meteorologia e dos jogos |
| `analise/` | Preparação da série diária, dados para modelação, análise exploratória e resultados locais |
| `docs/dicionarios/` | Dicionários completos e regras de interpretação |
| `docs/referencias/` | Formulário BEAV, manual e relatório da Parte I |
| `outputs/fase1/` | Auditoria detalhada e resumo dos resultados |
| `limpeza_tratamento/` | Scripts comentados de geração, verificação e documentação |
| `tests/` | Testes com dados sintéticos |

Dados, PDF, relatórios e ambiente virtual estão excluídos do Git.

## Documentação

- [Meteorologia diária de Portugal continental e integração na análise](docs/meteo_diaria.md)
- [Classificação provisória das 171 variáveis para o estudo inicial de Braga](docs/classificacao_provisoria_eda.md)
- [Escolhas iniciais para perfis — histórico, não seleção atual da EDA](docs/selecao_variaveis.md)
- [Dicionários dos quatro CSV](docs/dicionarios/README.md)
- [Procedimento da união dos anos](docs/fase1.md)
- [Como se verifica a correspondência com os originais](docs/integridade.md)
- [Organização e registo da limpeza](docs/organizacao.md)
- [Meteorologia: colunas, coordenadas e origem](docs/meteo.md)
- [Jogos do Braga: aquisição, dicionário e limitações](docs/jogos_braga.md)
- [Registo do que foi feito e evidência para auditoria](docs/registo_trabalho.md)

## Como repetir

Na primeira utilização, instalar as dependências:

```powershell
python -m pip install -r requirements.txt
```

Um comando permite unir e verificar os ficheiros, atualizar os dicionários e obter
meteorologia e jogos.

```powershell
python executar.py
```

O processo segue a ordem abaixo e para se alguma etapa falhar. Usa o mesmo
Python em todas as etapas. A meteorologia e as páginas de jogos já descarregadas são reutilizadas.
Para executar uma etapa isoladamente:

```powershell
python limpeza_tratamento/join.py
python limpeza_tratamento/verificar_resultados.py
python limpeza_tratamento/verificar_originais.py
python limpeza_tratamento/gerar_dicionarios.py
python aquisicao/obter_meteo_diaria.py
python aquisicao/obter_meteo.py
python aquisicao/obter_jogos_braga.py
python -m unittest discover -s tests -v
```

`join.py` lê `data/acidentes-AAAA.xlsx`, escreve os CSV em `data_agregada/`
e a auditoria em `outputs/fase1/`. Não altera os Excel originais.
`verificar_resultados.py` confere os CSV e grava o resumo da auditoria.
`verificar_originais.py` compara todos os valores com os Excel, sem amostragem,
e regista hashes SHA-256 e evidência em `outputs/fase1/comparacao_originais.*`.
`gerar_dicionarios.py` documenta os cabeçalhos e os anos de disponibilidade.
Usar `--help` para configurar caminhos. `join.py --audit-only` atualiza apenas
a auditoria, não os CSV; não substitui uma regeneração completa.

Para criar a série diária usada pela análise, instalar as dependências,
executar primeiro o notebook de preparação e depois abrir a EDA.

```powershell
python -m pip install -r analise/requirements.txt
python -m notebook analise/preparar_serie_diaria.ipynb
python -m notebook analise/eda_acidentes_diarios.ipynb
```

## Regras para continuar

Os agregados preservam os distritos, os anos e os campos de origem. As quatro
entidades continuam separadas. Juntá-las diretamente pode multiplicar registos.
Ler IDs como texto e `ano` como inteiro.
Uma coluna ausente num ano não equivale a zero. Faltam os ficheiros de 2020–2022.

Antes de um commit, rever `git status --short` e `git diff --cached --stat`.
Adicionar apenas caminhos explícitos de código e documentação. Publicar no
GitHub após verificação e com instrução do utilizador.
