# Análise e modelação de acidentes rodoviários

Esta pasta reúne a preparação, a análise exploratória e a base diária que será
usada para comparar SARIMA e redes neuronais em Portugal continental.

| Caminho | Conteúdo |
| --- | --- |
| [`preparar_serie_diaria.ipynb`](preparar_serie_diaria.ipynb) | Filtra os 18 distritos, constrói as contagens e agrega a meteorologia. |
| `dados/serie_diaria_continente.csv` | Base local pronta para a análise e a modelação, com uma linha por dia. |
| [`eda_acidentes_diarios.ipynb`](eda_acidentes_diarios.ipynb) | Análise exploratória que lê a base diária preparada. |
| `resultados/` | Cópias locais dos notebooks executados, com as tabelas e os gráficos. |
| [`requirements.txt`](requirements.txt) | Dependências dos notebooks atuais. |

Os dados de origem ficam em `data_agregada/` e `meteo/` na raiz do projeto.
O CSV preparado e os resultados executados são ficheiros locais gerados pelos
notebooks.

## Base diária

| Coluna | Conteúdo |
| --- | --- |
| `data` | Data civil no formato `AAAA-MM-DD`. Chave única da série. |
| `periodo` | `desenvolvimento` (2010–2019), `sem_dados` (2020–2022), `validacao` (2023) ou `teste_reservado` (2024). |
| `Despiste`, `Colisão`, `Atropelamento` | Contagens diárias por tipo. Os vazios correspondem aos anos sem ficheiro de acidentes. |
| `temperatura_media_c` | Temperatura média diária a 2 m, em °C. |
| `precipitacao_total_mm` | Média ponderada da precipitação acumulada no dia nos 18 distritos, em mm. |
| `vento_max_kmh` | Média ponderada dos máximos diários locais do vento a 10 m, em km/h. |
| `nebulosidade_media_pct` | Nebulosidade média, em percentagem. |
| `duracao_dia_h` | Duração astronómica do dia, em horas. |
| `sol_direto_h` | Duração estimada de sol direto, em horas. |
| `radiacao_total_mj_m2` | Radiação solar acumulada no dia, em MJ/m². |
| `areas_com_chuva_pct` | Percentagem do peso histórico dos distritos que registaram pelo menos 1 mm de chuva nesse dia. |

Os indicadores meteorológicos e solares são agregados com os pesos históricos
da [documentação de meteorologia](../docs/meteo_diaria.md). As condições ERA5
do dia-alvo são reanálise e servem para avaliação retrospetiva. Para testar um
modelo operacional com meteorologia, usar previsões arquivadas que estivessem
disponíveis antes do dia-alvo. Os modelos SARIMA e rede neuronal pertencem à
fase seguinte. As contagens de 2024 ficam reservadas para a avaliação final.

## Como reproduzir

Com os CSV de origem disponíveis, instalar as dependências e executar os
notebooks nesta ordem a partir da raiz do projeto.

```powershell
python -m pip install -r analise/requirements.txt
python -m nbconvert --to notebook --execute --output-dir=analise/resultados analise/preparar_serie_diaria.ipynb
python -m nbconvert --to notebook --execute --output-dir=analise/resultados analise/eda_acidentes_diarios.ipynb
```

Com a base diária já disponível em `dados/`, a análise exploratória pode ser
reexecutada só com o conteúdo desta pasta.
