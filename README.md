# Projeto de acidentes rodoviários

## Fase 1: auditoria e união dos anos

Os dados ficam exclusivamente no computador. `data/`, `dados/`, `outputs/`,
ficheiros de dados e o ambiente virtual estão excluídos do Git. Não fazer push
de dados, relatórios de auditoria ou amostras. Versionar apenas código e documentação.

Com Python e as dependências de `requirements.txt` instaladas:

```powershell
python limpeza_tratamento/join.py
# Integrar peoes por acidente no distrito do relatorio:
python limpeza_tratamento/integrar_peoes.py --district Braga
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
Fórmulas/erros Excel, cabeçalhos ambíguos, folhas desconhecidas e valores sem
cabeçalho interrompem a execução antes de publicar as saídas.

As quatro entidades relacionam-se por `(ano, Id. Acidente)`. As tabelas de pessoas
podem ter várias linhas por acidente. Um join direto entre elas pode criar um
produto cartesiano. Antes de construir uma tabela única por acidente, é preciso
definir agregações e resolver identificadores sem correspondência. Nesta fase,
esses registos ficam preservados nas tabelas respetivas e assinalados na auditoria.
O ID de veículo só existe nos anos recentes, impedindo inferir essa relação nos antigos.

### Alinhamento com o relatório da Parte I

O relatório local da equipa analisa Braga e usa contagens de peões por acidente.
`integrar_peoes.py` segue essa abordagem para todos os anos disponíveis: seleciona
os acidentes do distrito e conta os peões por `(ano, Id. Acidente)`, acrescentando
`peoes_envolvidos` e `acidente_com_peoes`. Mantém uma linha por acidente, inclusive
os acidentes sem peões (contagem zero), e preserva a variável `ano`.
Valida a unicidade dos acidentes selecionados e da chave
`(ano, Id. Acidente, Id. Peao)` dos peões associados. Não escolhe arbitrariamente
entre duplicados. A saída `acidentes_distrito_com_peoes.csv` e os totais em
`integracao_peoes.json` ficam em `outputs/fase1/`, fora do Git.
O distrito pode ser alterado com `--district`. As quatro tabelas nacionais
continuam disponíveis como base. Indicadores de gravidade, curvas, normalização
de categorias e análises mensais pertencem às fases seguintes.

Não há ficheiros de 2020, 2021 e 2022 no conjunto inicial. Não são criadas linhas
para preencher anos em falta. Diferenças de categorias, formatos de datas e
coordenadas ficam para uma fase posterior de tratamento.

## Git

Antes de cada commit, verificar `git status --short` e `git diff --cached --stat`.
Usar `git add` com caminhos explícitos de código/documentação. Os commits são locais.
Não executar `git push` sem instrução do utilizador.
