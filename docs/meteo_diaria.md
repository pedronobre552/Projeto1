# Meteorologia diária para a previsão nacional de acidentes

O script [obter_meteo_diaria.py](../aquisicao/obter_meteo_diaria.py) obtém
meteorologia de **2010-01-01 a 2024-12-31** usando a
[Historical Weather API da Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api)
com um modelo fixo, **ERA5**. A granularidade solicitada à API é diária. O CSV
tem uma linha por data e área e 29 pontos de referência: as capitais dos 18
distritos continentais, as nove ilhas dos Açores e as duas ilhas habitadas da
Madeira. Os pontos vêm do [catálogo do IPMA](https://api.ipma.pt/open-data/distrits-islands.json).

O fuso pedido à API segue cada área, com `Europe/Lisbon`, `Atlantic/Madeira`
ou `Atlantic/Azores`. A grelha ERA5 tem 0,25° de resolução. A célula terrestre
escolhida pela API representa a vizinhança do ponto. A série corresponde a
uma aproximação da meteorologia do distrito ou ilha. A aproximação pode ser
menos representativa em áreas extensas, costeiras ou montanhosas.

## Ficheiros e verificação

Executar a partir da raiz do projeto.

```powershell
python aquisicao/obter_meteo_diaria.py
```

- `meteo/meteorologia_diaria_portugal.csv` contém os 158.891 pares data–área esperados.
- `outputs/meteo_diaria/respostas/` guarda os JSON usados para reexecutar as consultas localmente.
- `outputs/meteo_diaria/origem.json` regista os lotes, URLs, modelo e data de aquisição.

O script confere o número de respostas, os dias, os fusos, as unidades e a
proximidade entre a coordenada de referência e a célula ERA5. O notebook verifica
a unicidade dos pares data–área, a cobertura das áreas presentes nos acidentes,
a disponibilidade das variáveis e os seus limites físicos.

## Dicionário

| Coluna | Definição |
| --- | --- |
| `area`, `tipo_area`, `data` | Área da fonte, categoria geográfica e dia no fuso pedido |
| `ponto_ipma`, `fuso` | Local de referência do IPMA e fuso pedido |
| `latitude_ponto`, `longitude_ponto` | Coordenadas do ponto no catálogo IPMA |
| `latitude_era5`, `longitude_era5` | Coordenadas da célula devolvida |
| `temperatura_media_c` | Temperatura média diária a 2 m, °C |
| `precipitacao_total_mm` | Precipitação total diária, mm |
| `vento_max_kmh` | Velocidade máxima diária do vento a 10 m, km/h |
| `nebulosidade_media_pct` | Nebulosidade média diária, % |
| `duracao_dia_s` | Duração astronómica do período diurno, segundos |
| `horas_sol_s` | Duração de sol direto estimada, em segundos |
| `radiacao_total_mj_m2` | Radiação de onda curta acumulada, MJ/m² |

## Integração nas contagens nacionais

O [notebook](../analise/eda_acidentes_diarios.ipynb) calcula médias nacionais
ponderadas. Os pesos são proporções de acidentes por área em 2010–2014, fixadas
antes dos períodos de validação. O Corvo está coberto pela meteorologia e tem
peso zero por ausência de registos de acidentes nesse período. A comparação
com pesos iguais mostra a sensibilidade dessa escolha.

Além da precipitação média ponderada, o notebook calcula a percentagem do
peso histórico em áreas com pelo menos 1 mm de precipitação no dia. Isto
mede a extensão da chuva nas áreas representadas e permite testar se a
informação acrescenta valor à média de precipitação.

As datas de 2020 a 2022 têm meteorologia, mas faltam contagens de acidentes.
O notebook mantém essas respostas em falta. Nos anos cobertos, o calendário
inclui os dias observados com zero ocorrências de um tipo.

O ERA5 descreve condições reconstruídas do próprio dia. Os resultados com
essas entradas são retrospetivos. Uma avaliação operacional exige previsões
meteorológicas arquivadas com uma origem anterior ao dia-alvo. A duração
astronómica do dia está disponível antecipadamente e pode ser redundante com
o calendário anual. Sol direto e radiação descrevem condições diárias e
dependem também da meteorologia.
