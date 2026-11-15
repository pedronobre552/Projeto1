# Projeto de acidentes rodoviários

O procedimento completo, decisões e limitações estão em [docs/fase1.md](docs/fase1.md).

## Fase 1: auditoria e união dos anos

Os dados ficam exclusivamente no computador. `data/`, `dados/`, `outputs/`,
ficheiros de dados e o ambiente virtual estão excluídos do Git. Não fazer push
de dados, relatórios de auditoria ou amostras. Versionar apenas código e documentação.

Com Python e as dependências de `requirements.txt` instaladas:

```powershell
python limpeza_tratamento/join.py
python limpeza_tratamento/verificar_resultados.py
# Para executar apenas a auditoria:
python limpeza_tratamento/join.py --audit-only
```

Lê todos os `data/acidentes-AAAA.xlsx`, sem alterar os originais.
Produz quatro CSV em UTF-8 com BOM em `outputs/fase1/`: acidentes,
condutores_veiculos, passageiros e peoes. A união é vertical, por nome de coluna,
mantendo a granularidade de cada entidade. Cada linha recebe `ano` (inteiro,
extraído do nome do ficheiro), ficheiro, folha e linha de origem.
O campo original `Ano`, quando existe, é preservado e comparado com `ano`.

Deteta cabeçalhos nas primeiras dez linhas, incluindo o formato de 2023.
Uniformiza espaços nos cabeçalhos e o sufixo `SUM` nos três contadores de vítimas.
Mantém todas as colunas existentes em qualquer ano; as ausentes ficam vazias.
Preserva os valores originais, exceto a representação dos IDs como texto.
Não remove duplicados, não imputa valores e não altera categorias, datas ou GPS.
CSV não guarda tipos: ao importar, ler `Id. Acidente` como texto e `ano` como inteiro.

`auditoria.json` contém contagens por fonte, colunas ausentes, tipos, nulos,
duplicados exatos, IDs repetidos/vazios, validação do ano e relações sem acidente.
`verificar_resultados.py` confere os CSV contra a auditoria e grava o resumo
legível `outputs/fase1/resumo_auditoria.md`, também apenas local.
Fórmulas e erros Excel são preservados como texto e assinalados por coordenada
na auditoria, sem avaliar expressões nem substituir valores.
Cabeçalhos ambíguos, folhas desconhecidas e valores sem cabeçalho interrompem
a execução antes de publicar as saídas.

As quatro entidades relacionam-se por `(ano, Id. Acidente)`. As tabelas de pessoas
podem ter várias linhas por acidente. Um join direto entre elas pode criar um
produto cartesiano. Antes de construir uma tabela única por acidente, é preciso
definir agregações e resolver identificadores sem correspondência. Nesta fase,
esses registos ficam preservados nas tabelas respetivas e assinalados na auditoria.
O ID de veículo só existe nos anos recentes, impedindo inferir essa relação nos antigos.

### Âmbito desta fase

O relatório da Parte I serve como referência para a interpretação das tabelas.
Nesta fase mantém-se a totalidade dos anos e distritos, acrescentando apenas
`ano` e a proveniência. A escolha de variáveis, filtros geográficos, integração
de contagens de pessoas e indicadores fica para depois de definido o objetivo.

Não há ficheiros de 2020, 2021 e 2022 no conjunto inicial. Não são criadas linhas
para preencher anos em falta. Diferenças de categorias, formatos de datas e
coordenadas ficam para uma fase posterior de tratamento.

## Git

Antes de cada commit, verificar `git status --short` e `git diff --cached --stat`.
Usar `git add` com caminhos explícitos de código/documentação. Os commits são locais.
Não executar `git push` sem instrução do utilizador.
