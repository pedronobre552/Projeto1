# Registo do que foi feito

Este documento resume as operações e aponta para a evidência que permite
auditá-las. As instruções de repetição estão no README e nos documentos de cada
fase. Os resultados dos dados são locais, sem publicação no GitHub.

## Preparação dos acidentes — estado revisto em 15-11-2026

- Preservaram-se os Excel anuais em `data/` e os PDF fornecidos em
  `docs/referencias/`. Organizaram-se código, documentação, saídas e auditoria
  em pastas próprias. As movimentações estão em [organizacao.md](organizacao.md).
- Uniram-se os anos disponíveis, separadamente para acidentes, condutores/veículos,
  passageiros e peões. Acrescentaram-se ano e proveniência, preservando a união
  das colunas e os valores originais. Não se selecionaram variáveis finais nem
  se juntaram as quatro entidades entre si.
- Os anos disponíveis são 2010–2019 e 2023–2024. Faltam os Excel de 2020–2022.
  Há 402 016 acidentes, 617 890 condutores/veículos, 125 598 passageiros e
  66 448 peões nos CSV agregados.
- Compararam-se os CSV integralmente com os Excel: 1 211 952 linhas e
  57 688 572 células, sem divergências na execução registada. A metodologia e
  as transformações aceites estão em [integridade.md](integridade.md), com
  evidência em `outputs/fase1/comparacao_originais.*` e `auditoria.json`.
- Criaram-se dicionários das quatro tabelas com base nos cabeçalhos e documentos
  BEAV. As dúvidas de interpretação estão identificadas nos próprios dicionários.

## Meteorologia — estado revisto em 15-11-2026

- Recolheram-se dados históricos Open-Meteo/ERA5 de 2010–2024 para representar
  os 14 municípios do distrito de Braga. Não foram enviadas coordenadas de acidentes.
- As referências municipais, correções de associação e a resolução da grelha
  estão documentadas em [meteo.md](meteo.md). Municípios na mesma célula recebem
  os mesmos valores meteorológicos, sem simular maior precisão espacial.
- Geraram-se dois CSV: meteorologia horária (1 840 944 linhas) e nascer/pôr do
  sol diário (76 706 linhas). Abrangem 5 479 dias, incluindo anos bissextos.
- Conferiu-se a continuidade horária em UTC e a cobertura diária dos 14
  municípios, sem lacunas. A hora local mantém o desvio UTC nas mudanças de hora.
- As respostas originais estão em `outputs/meteo/respostas/`; a origem em
  `outputs/meteo/origem.json`. O script reutiliza as respostas e respeita as
  esperas pedidas pela API quando atinge limites de utilização.

## Jogos do Braga — 15-11-2026

- Âmbito confirmado pelo utilizador: equipa principal masculina, todas as
  competições oficiais, datas civis de 2010–2024.
- Consultou-se o endpoint público da ESPN. A época 2010/11 tinha 49 jogos,
  sem os cinco jogos das taças nacionais. Consultaram-se também outras fontes
  históricas. Escolheram-se as tabelas públicas do domínio português do
  Transfermarkt para a recolha, sem API, autenticação ou envio de dados locais.
- Criou-se o script comentado `aquisicao/obter_jogos_braga.py`, com cache local,
  pausa entre pedidos e opção explícita para atualizar as páginas.
- Descarregaram-se 16 calendários, de 2009/10 a 2024/25, e filtraram-se as datas
  de 2010–2024. Gerou-se `jogos/braga.csv` com 754 jogos, sem IDs repetidos.
- Na revisão detetaram-se dois jogos de 2012/13 com resultado mas sem a classe
  CSS habitual dos links. A extração foi corrigida para os incluir. O problema
  e a correção ficaram cobertos por um teste de regressão.
- Conferiram-se campeonato por época, formatos, presença de taças e leitura
  integral do CSV contra os valores extraídos. Conferiram-se pontualmente os
  totais de 2010/11 e 2012/13 em outra fonte secundária.
- A comparação exploratória com a ESPN encontrou duas divergências horárias,
  explicitadas em [jogos_braga.md](jogos_braga.md). Não foram corrigidas por
  suposição. Não foi feita validação integral contra fichas oficiais.
- Guardaram-se páginas originais, contagens e hashes em `outputs/jogos/`.
  Criaram-se o dicionário, instruções de repetição e descrição das limitações.
  O script foi acrescentado como sexta etapa do comando `python executar.py`.

## Código, verificações e Git

O comando geral executa união, verificações, dicionários, meteorologia e jogos,
interrompendo se alguma etapa falhar. A sequência é testada sem chamadas à rede.
As aquisições reutilizam os ficheiros já guardados para evitar novos pedidos.

Nesta atualização executou-se a aquisição real dos jogos e a regeneração a
partir das páginas guardadas. Os 15 testes passaram após as alterações, com
registo local em `outputs/jogos/testes.log`.
Não se repetiu a leitura integral dos Excel nem a aquisição meteorológica,
porque o código dessas etapas não foi alterado nesta atualização.

São versionados apenas código, testes e documentação. CSV, Excel, PDF,
respostas das APIs e páginas guardadas estão excluídos pelo `.gitignore`.
Os commits registam as versões do processo. Os hashes nas auditorias permitem
identificar as versões dos dados locais usadas em cada execução guardada.
As auditorias são substituídas quando se volta a executar a respetiva aquisição.
