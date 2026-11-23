# Meteorologia e horas solares de Braga

Para a previsão diária em Portugal continental, consultar a [meteorologia diária dos 18 distritos](meteo_diaria.md).

São dois ficheiros na pasta `meteo`, para os 14 concelhos do distrito,
de **2010-01-01 a 2024-12-31**:

- `meteorologia_horaria.csv`: uma linha por município e hora.
- `sol_diario.csv`: uma linha por município e dia, com nascer e pôr do sol.

O intervalo pedido inclui 2020–2022, mesmo não havendo ficheiros de acidentes desses anos.
O intervalo acima é o pedido completo. A cobertura efetivamente obtida está
registada em `outputs/meteo/origem.json`; não se preenchem anos ainda não adquiridos.

## Origem e método

Os valores são os devolvidos pela
[Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api),
com o modelo **ERA5**, do ECMWF/Copernicus, fixo em todo o período.
São estimativas históricas de reanálise, não medições exatas em cada local.
Não criamos indicadores nem agregamos os valores meteorológicos. As horas são
convertidas de UTC para `Europe/Lisbon`, incluindo a hora de verão. O CSV horário
inclui UTC e hora local com o desvio `+00:00`/`+01:00`, para distinguir a hora
repetida no outono. Nascer/pôr do sol são apresentados como hora local `HH:MM`.

Usamos um ponto de referência por concelho, com coordenadas publicadas pelo
[IPMA](https://api.ipma.pt/open-data/forecast/meteorology/rcm/rcm-d0.json).
Não são usadas nem enviadas coordenadas de acidentes.
Os pontos foram confirmados territorialmente em
[GISCO/Eurostat, LAU 2024](https://gisco-services.ec.europa.eu/features/collections/gisco.lau_rg_01m_2024_4326.html).
A resposta IPMA consultada tinha os pontos de Amares e Barcelos associados aos
códigos trocados; a tabela abaixo usa a associação territorial confirmada.
Do IPMA utilizam-se apenas as coordenadas, não as previsões de risco de incêndio.

| Município | Latitude | Longitude |
| --- | ---: | ---: |
| Amares | 41.6314 | -8.3489 |
| Barcelos | 41.5400 | -8.6100 |
| Braga | 41.5475 | -8.4227 |
| Cabeceiras de Basto | 41.5140 | -7.9901 |
| Celorico de Basto | 41.3900 | -8.0000 |
| Esposende | 41.5356 | -8.7819 |
| Fafe | 41.4472 | -8.1732 |
| Guimarães | 41.4434 | -8.2938 |
| Póvoa de Lanhoso | 41.5762 | -8.2708 |
| Terras de Bouro | 41.7200 | -8.3100 |
| Vieira do Minho | 41.6355 | -8.1416 |
| Vila Nova de Famalicão | 41.4087 | -8.5205 |
| Vila Verde | 41.6545 | -8.4348 |
| Vizela | 41.3800 | -8.3100 |

O ERA5 tem uma grelha de 0,25° (aproximadamente 25 km). Estes pontos municipais
correspondem a seis células; consultamos cada célula uma vez e atribuímos os
valores aos concelhos correspondentes, sem correção de altitude. Por isso,
concelhos próximos podem ter valores iguais. Não são médias da área do município.

## Meteorologia horária

| Coluna | Informação |
| --- | --- |
| `municipio` | Nome do concelho |
| `data_hora_utc` | Data/hora UTC, com `+00:00` |
| `data_hora_local` | Data/hora legal portuguesa, com desvio UTC |
| `temperatura_c` | Temperatura a 2 m, °C |
| `humidade_pct` | Humidade relativa a 2 m, % |
| `precipitacao_mm` | Precipitação acumulada na hora anterior ao instante indicado, mm |
| `nebulosidade_pct` | Nebulosidade, % |
| `vento_kmh` | Velocidade do vento a 10 m, km/h |
| `codigo_tempo_wmo` | Código de condição meteorológica devolvido pela API |
| `radiacao_solar_w_m2` | Radiação solar global média na hora anterior, W/m² |
| `radiacao_direta_w_m2` | Radiação solar direta média na hora anterior, W/m² |

## Nascer e pôr do sol

| Coluna | Informação |
| --- | --- |
| `municipio` | Nome do concelho |
| `data` | Dia no formato `AAAA-MM-DD` |
| `nascer_sol` | Hora local do nascer do sol, `HH:MM` |
| `por_sol` | Hora local do pôr do sol, `HH:MM` |

Os dois ficheiros permitem relacionar meteorologia e período diurno com a hora
dos acidentes. A radiação e as horas solares não demonstram, por si só, que
houve encandeamento. As perguntas sobre jogos de futebol e veículos serão
tratadas separadamente. Para cruzar com os acidentes será necessário uniformizar
os nomes dos concelhos que aparecem com e sem acentos.

## Repetir a aquisição

```powershell
python aquisicao/obter_meteo.py
# Para montar apenas a parte já descarregada, sem esperar pelos restantes anos:
python aquisicao/obter_meteo.py --ate 2020
```

O script reutiliza respostas já guardadas e espaça os pedidos à API.
Se a API atingir a quota, aguarda o prazo indicado em `Retry-After` e retoma
na mesma execução. Com `python executar.py`, a aquisição meteorológica ocorre
automaticamente depois da união, verificações e atualização dos dicionários.
As respostas originais ficam em `outputs/meteo/respostas/` e os URLs
das consultas em `outputs/meteo/origem.json`. Os CSV e estas respostas ficam
apenas locais, excluídos do Git. Os dados Open-Meteo requerem atribuição à fonte
([condições](https://open-meteo.com/en/terms)).
