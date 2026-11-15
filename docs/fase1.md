# Fase 1 — Auditoria e união dos anos

## Objetivo e âmbito

Criar um CSV por tabela com todos os anos disponíveis, acrescentando a variável
`ano`. Preservar a informação necessária para escolher posteriormente as
variáveis finais em função do objetivo do projeto.

Não aplicar filtros por distrito, selecionar variáveis, criar indicadores de
gravidade ou curvas, agregar pessoas, imputar dados nem remover duplicados.
O relatório da Parte I ajuda a compreender as entidades e os riscos de junção,
mas o seu recorte de Braga e a análise de 2019/2023 não limitam esta preparação.

## Organização dos ficheiros

| Local | Conteúdo | Git |
| --- | --- | --- |
| `data/acidentes-AAAA.xlsx` | Fontes anuais, preservadas | Excluído |
| `data_agregada/` | CSV finais por entidade | Excluído |
| `outputs/fase1/` | Resultados da auditoria | Excluído |
| `docs/referencias/` | Documentos oficiais e referência da equipa | Excluído |
| `limpeza_tratamento/` | Scripts reproduzíveis e comentados | Versionado |
| `tests/` | Testes com dados sintéticos | Versionado |
| `docs/` | Procedimento e decisões técnicas | Versionado |

Todos os passos decorrem localmente. O script não acede à rede. Os commits
guardam apenas código, testes, configuração e documentação. Não fazer push
sem instrução explícita do utilizador.

## Procedimento

1. Verificar `git status --short --branch` e os caminhos já versionados com
   `git ls-files`. Confirmar que os dados estão excluídos com `git check-ignore`.
2. Descobrir todos os ficheiros `acidentes-AAAA.xlsx` e extrair o ano do nome.
   Nomes inesperados interrompem a execução. Anos em falta são assinalados.
3. Mapear as folhas para entidades pelo nome, nunca pela posição no Excel.
4. Procurar `Id. Acidente` nas primeiras dez linhas para localizar o cabeçalho.
   As margens e linhas vazias de 2023 não devem deslocar os dados.
5. Construir a união das colunas de cada entidade. Alinhar valores por nome,
   mantendo campos ausentes num ano vazios, sem os substituir por zero.
6. Ler todas as linhas e recolher diagnósticos. Ignorar apenas linhas totalmente
   vazias. Preservar duplicados, IDs sem correspondência e valores problemáticos.
7. Acrescentar `ano`, `ficheiro_origem`, `folha_origem` e `linha_origem`.
8. Concluir a leitura antes de publicar os ficheiros. A execução usa uma pasta
   temporária dentro da pasta dos CSV e não substitui os resultados anteriores perante
   um erro de leitura ou validação. A publicação final de vários ficheiros não
   constitui uma transação atómica face a falhas do sistema/disco.
9. Verificar estrutura/contagens contra a auditoria e comparar integralmente os
   valores dos CSV com os Excel através de `verificar_originais.py`. Executar os testes e
   registar as alterações técnicas num commit local com caminhos explícitos.

## Correspondência de folhas

| Entidade / saída | Folha antiga | Folha recente |
| --- | --- | --- |
| `acidentes.csv` | `30 Dias _ Acidentes` | `30dias_acV` |
| `condutores_veiculos.csv` | `30 Dias_Cond_Veic` | `30dias_cond` |
| `passageiros.csv` | `30 Dias_Passag` | `30dias_psg` |
| `peoes.csv` | `30 Dias_Peões` | `30dias_peao` |

São exigidas as quatro entidades em cada ficheiro. Folhas desconhecidas,
entidades repetidas, cabeçalhos duplicados após normalização, nomes reservados
ou valores em colunas sem cabeçalho interrompem a execução para evitar perdas.

## Regras de transformação

- `ano` provém do nome do ficheiro e é comparado com `Datahora` quando existente.
  O campo original `Ano` de alguns ficheiros é preservado e também comparado.
- Os cabeçalhos perdem espaços exteriores e espaços repetidos. Uniformiza-se
  o espaço antes dos parênteses dos grupos etários. O sufixo `SUM` é retirado
  apenas dos três contadores de mortos/feridos a 30 dias.
- `Id. Acidente` é representado como texto. Um ID numérico integral não ganha
  o sufixo `.0`. Códigos alfanuméricos não são transformados nem associados por
  aproximação. Zeros iniciais em texto são preservados. Zeros que existam apenas
  na formatação visual do Excel não são reconstruídos.
- Fórmulas e erros Excel são preservados como texto, sem avaliação. A auditoria
  regista folha, célula, tipo e conteúdo. Isto permite conservar descrições que
  tenham sido interpretadas incorretamente como fórmulas nas fontes.
- Categorias, coordenadas, datas, idades e valores em falta não são tratados
  nesta fase. Uma divergência detetada é um diagnóstico, não uma correção automática.
- CSV usa UTF-8 com BOM e vírgula como separador. Importar explicitamente os IDs
  como texto e `ano` como inteiro. CSV não transporta tipos, estilos ou fórmulas
  Excel; não avaliar expressões preservadas ao importar para uma folha de cálculo.

## Auditoria e limitações

A garantia de correspondência com os Excel, as regras de comparação e os
limites da evidência estão descritos em [integridade.md](integridade.md).
Conferir contagens contra a auditoria, por si só, não prova igualdade dos valores.

`auditoria.json` regista, para cada fonte, linhas lidas/vazias, IDs vazios e
repetidos, duplicados exatos, tipos e nulos por coluna, colunas ausentes,
datas inválidas, anos divergentes e células de fórmula/erro.
Os nulos por coluna referem-se às colunas existentes nessa fonte. A ausência
estrutural de uma coluna é registada separadamente em `colunas_ausentes`.

Nas relações, usa-se `(ano, Id. Acidente)`. Contam-se IDs e linhas de pessoas
sem acidente correspondente e acidentes com várias linhas em cada entidade.
O relatório mede correspondências exatas depois da representação textual do ID.
Não garante equivalência semântica de categorias, unidades ou formatos ao longo
dos anos. Não prova que uma linha repetida seja um erro nem que um ID órfão possa
ser recuperado por outro campo.

Uma futura junção direta entre condutores, passageiros e peões pode multiplicar
linhas. Será necessário definir a unidade de análise e as agregações antes desse
passo. Esta fase concatena verticalmente os anos dentro de cada entidade.

## Como executar e validar

Preparar um ambiente Python com as dependências de `requirements.txt`.
Na execução assistida foi usado o Python com bibliotecas já incluído no Codex,
sem instalar pacotes pela rede nem alterar o ambiente virtual do projeto.

```powershell
python limpeza_tratamento/join.py
python limpeza_tratamento/verificar_resultados.py
python limpeza_tratamento/verificar_originais.py
python -m unittest discover -s tests -v
git diff --check
git status --short --branch
git check-ignore data/acidentes-2024.xlsx outputs/fase1/auditoria.json
```

Os CSV ficam em `data_agregada/`; a auditoria e o resumo ficam em `outputs/fase1/`.
Para outras pastas, usar `--input-dir`, `--output-dir` e `--report-dir`. Para repetir apenas a
auditoria, usar `--audit-only`: lê todas as fontes e grava o relatório sem gerar
novos CSV. CSV anteriores, se existirem, não são atualizados por esse modo.

Os testes usam pequenos Excel sintéticos para verificar a mudança de cabeçalho
de 2023, os anos, a rastreabilidade, a preservação de duplicados e códigos
alfanuméricos, a deteção de relações órfãs e a normalização dos contadores.
Também verificam a preservação de fórmulas como texto e a interrupção perante
valores sem cabeçalho sem substituir um resultado anterior.

Os resultados específicos da execução ficam em `outputs/fase1/auditoria.json` e no resumo
local `outputs/fase1/resumo_auditoria.md`. O script `verificar_resultados.py` lê os CSV já
gravados para conferir o esquema, o ano, as contagens totais e por fonte e a
unicidade/ordem da linha de origem. Não altera os dados nem extrai variáveis.
Antes de cada commit, rever `git diff --cached --stat` e usar `git add` apenas
com caminhos explícitos dos ficheiros técnicos.
