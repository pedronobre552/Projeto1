# Jogos oficiais do Braga — aquisição e dicionário

## Fonte e âmbito

Equipa principal masculina, de 1 de janeiro de 2010 a 31 de dezembro de 2024.
O CSV está em `jogos/braga.csv`. Contém 754 jogos recolhidos dos calendários
públicos do [Transfermarkt](https://www.transfermarkt.pt/sc-braga/spielplan/verein/1075/saison_id/2010),
uma fonte desportiva secundária, não a entidade organizadora das provas.

Inclui campeonato, Taça de Portugal, Taça da Liga (nome atual apresentado pela
fonte: Allianz Cup), Supertaça e provas europeias, incluindo qualificações.
Os nomes das competições e dos adversários são os apresentados atualmente
pela fonte, podendo não corresponder ao nome comercial usado na data do jogo.
Não inclui amigáveis nem jogos das equipas B, formação ou feminina.

O método é **leitura de tabelas HTML públicas (web scraping), sem API**.
A ESPN disponibiliza um endpoint público em JSON, mas a consulta de 2010/11
devolveu 49 jogos e omitiu os cinco jogos das taças nacionais. Por isso não foi
escolhida como fonte principal para todas as competições.

## Repetir a recolha

Instalar as dependências de `requirements.txt` e executar:

```powershell
python aquisicao/obter_jogos_braga.py
```

O script comentado descarrega 16 páginas, das épocas 2009/10 a 2024/25, com
uma pausa de três segundos entre pedidos. As épocas que atravessam os limites
do período são necessárias para obter janeiro de 2010 e dezembro de 2024.
Depois de ler as épocas completas, seleciona apenas as datas de 2010–2024.

As páginas são guardadas em `outputs/jogos/transfermarkt/AAAA.html` e reutilizadas
nas execuções seguintes, sem novos pedidos. Para voltar a consultar o site:

```powershell
python aquisicao/obter_jogos_braga.py --atualizar
```

O comando geral `python executar.py` também executa esta etapa, depois da
meteorologia. Se o site estiver indisponível, mudar de formato ou devolver uma
competição desconhecida, a execução termina com erro. Não se contorna qualquer
bloqueio de acesso. A disponibilidade futura do site não é garantida.

## Dicionário do CSV

Uma linha por jogo. Separador `;`, codificação UTF-8 com BOM. Ler `id_jogo`
como texto e `data` como data ISO. Não há seleção de variáveis finais do estudo.

| Coluna | Significado |
| --- | --- |
| `id_jogo` | Identificador do relatório do jogo no Transfermarkt |
| `epoca` | Época desportiva, por exemplo `2010/2011` |
| `data` | Data publicada, convertida de DD/MM/AAAA para AAAA-MM-DD |
| `hora_inicio_portugal` | Hora publicada no domínio português, HH:MM, correspondente à hora de Portugal continental nas comparações efetuadas; não é uma hora certificada |
| `competicao` | Nome da competição tal como apresentado pela fonte |
| `fase` | Jornada, grupo ou eliminatória tal como apresentada pela fonte |
| `adversario` | Nome apresentado no calendário |
| `condicao_braga_fonte` | `C` casa, `F` fora, `N` neutro, conforme a marcação da fonte |
| `resultado_fonte` | Texto original do resultado, incluindo indicações de prolongamento/penáltis; ordem equipa da casa–visitante, não necessariamente Braga–adversário |
| `url_fonte` | Ligação para o relatório de cada jogo |

**Casa/fora não identifica o estádio nem o município.** Em finais em campo
neutro a fonte pode marcar o Braga como `C` ou `F` pela ordem das equipas.
Não usar este campo isoladamente para concluir que o jogo decorreu em Braga.
O CSV não contém estádio, assistência, duração real ou hora de fim.

Uma hora desconhecida fica vazia, sem preencher com `00:00`. Nesta recolha
todas as linhas tinham hora publicada, o que não garante que todas estejam corretas.
Não se estimaram horários nem se calcularam janelas de exposição a acidentes.

## Como se verifica a fidelidade à fonte

- As 16 páginas consultadas ficam preservadas localmente. Cada linha tem
  o identificador e a ligação para o jogo, permitindo conferência manual.
- `outputs/jogos/origem.json` regista os URLs dos calendários, os caminhos das
  páginas, a data de modificação dos ficheiros guardados, hashes SHA-256 das
  páginas e do CSV, contagens por época/competição e por ano civil, e horas vazias.
- A extração confere datas, horas, identificação do adversário, resultado e
  condição casa/fora. Competições desconhecidas provocam erro em vez de serem
  ignoradas. Incluem-se também resultados antigos sem a classe CSS usada nos
  restantes links, caso detetado nos jogos com Naval e Pampilhosa de 2012/13.
- O campeonato de cada época tem de apresentar 30 jogos até 2013/14 e 34 a
  partir de 2014/15. Confere-se a presença das taças nacionais e rejeitam-se IDs
  repetidos. O CSV só é gerado após a leitura válida de todas as épocas.
- O script relê o CSV e compara todas as linhas e valores com os registos
  extraídos das páginas. Apenas se normalizam espaços, formato da data e hora.
- Os testes sintéticos verificam preservação dos campos, falta de jornada,
  hora desconhecida, data inválida, competição desconhecida e jogos sem a
  classe CSS habitual. Não dependem da rede.

Estas verificações asseguram a correspondência entre a extração e as páginas
guardadas. **Não provam que a fonte não tenha erros ou omissões.** A contagem do
campeonato é uma verificação de quantidade, não uma confirmação independente de
cada jornada. Não se realizou uma validação integral contra fichas oficiais.

## Conferências adicionais e limitações encontradas

As épocas 2010/11 (54 jogos) e 2012/13 (47 jogos) coincidem com os totais dos
resumos das respetivas épocas na Wikipédia:
[2010/11](https://en.wikipedia.org/wiki/2010%E2%80%9311_S.C._Braga_season) e
[2012/13](https://en.wikipedia.org/wiki/2012%E2%80%9313_S.C._Braga_season).
É uma conferência pontual de contagens em outra fonte secundária.

Compararam-se os horários dos 49 jogos comuns de 2010/11 com a
[resposta pública da ESPN](https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams/2994/schedule?season=2010),
convertendo as datas UTC da ESPN para `Europe/Lisbon` e associando pela data.
47 horários coincidiram e dois divergiram:

| Data | Adversário | Transfermarkt | ESPN em Portugal |
| --- | --- | --- | --- |
| 2010-10-30 | Rio Ave | 19:15 | 20:15 |
| 2011-03-17 | Liverpool | 18:00 | 20:05 |

O CSV mantém o Transfermarkt, sem correções silenciosas. A resposta da ESPN está
em `outputs/jogos/sondagem_espn.json` e a comparação em
`outputs/jogos/comparacao_espn_2010.json`. Esta conferência foi feita durante a
aquisição inicial e não é repetida pelo comando geral. Antes de analisar janelas
horárias destes jogos, será necessário resolver as divergências com fichas oficiais.

## Contagens obtidas em 15-11-2026

| Ano civil | Jogos |
| --- | ---: |
| 2010 | 47 |
| 2011 | 51 |
| 2012 | 47 |
| 2013 | 42 |
| 2014 | 41 |
| 2015 | 51 |
| 2016 | 59 |
| 2017 | 54 |
| 2018 | 43 |
| 2019 | 54 |
| 2020 | 44 |
| 2021 | 60 |
| 2022 | 50 |
| 2023 | 56 |
| 2024 | 55 |
| **Total** | **754** |

Dados e páginas originais ficam locais e excluídos do Git. Código, testes e
documentação podem ser versionados. O cruzamento com os acidentes fica para a
fase seguinte, sem multiplicar os registos das tabelas originais.
