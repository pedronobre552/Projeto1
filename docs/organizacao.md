# Organização e limpeza do projeto

## Estrutura adotada

```text
Projeto1/
  data/                         Excel originais
  data_agregada/                quatro CSV finais
  docs/
    dicionarios/                um dicionário por CSV e guia comum
    referencias/                os três PDF fornecidos
    fase1.md                    processo de união dos anos
    organizacao.md              este registo
  limpeza_tratamento/
    join.py                     união e auditoria das fontes
    verificar_resultados.py     validação dos CSV gravados
    verificar_originais.py      comparação integral com os Excel e hashes
    gerar_dicionarios.py        documentação das colunas
  outputs/fase1/                auditoria JSON e resumo Markdown
  tests/                        testes sintéticos
  README.md                     ponto de entrada
  requirements.txt              dependências do projeto
```

## Alterações efetuadas

- Corrigiu-se a pasta vazia `data_agragada` para `data_agregada` e moveram-se
  os quatro CSV de `outputs/fase1/`. Os dados não foram regenerados nem editados.
- Moveram-se o formulário BEAV, o manual e o relatório da Parte I da raiz para
  `docs/referencias/`, preservando os documentos originais.
- Os relatórios úteis mantiveram-se em `outputs/fase1/`, separados dos dados.
  Os scripts foram ajustados, incluindo argumentos configuráveis e compatibilidade
  com testes que usam uma só pasta.
- Criou-se um dicionário por CSV com todos os cabeçalhos, definições, tipos,
  disponibilidade anual e referências. Mantiveram-se explícitas as dúvidas de
  correspondência entre nomes da exportação e campos oficiais.
- Simplificou-se o README. As regras detalhadas continuam em `fase1.md`.
- Retiraram-se apenas extrações de texto dos PDF, imagens de inspeção e caches
  Python gerados durante o trabalho. Os PDF permitem repetir a consulta.
  Mantiveram-se o ambiente virtual, os testes e o histórico Git.

## O que não foi descartado

Excel originais, CSV, PDF oficiais, relatório da equipa e auditoria são úteis
para reproduzir e interpretar o trabalho. Mantiveram-se todas as variáveis,
incluindo proveniência. A escolha de variáveis finais depende do objetivo
futuro e não é substituída por esta limpeza de ficheiros.

## Validação e Git

O verificador confere novamente os CSV na nova pasta contra a auditoria:
cabeçalhos, contagens, ano e proveniência. Os testes verificam a separação das
pastas e as regras existentes. O gerador documenta cada coluna na ordem do
cabeçalho e falha perante campos desconhecidos.

O comparador `verificar_originais.py` relê as fontes e confere todos os valores,
incluindo campos vazios, sem depender da auditoria. O procedimento, as
transformações aceites e os limites estão em [integridade.md](integridade.md).

`data/`, `data_agregada/`, `outputs/`, PDF e `docs/referencias/` estão excluídos
do Git. Os dicionários contêm definições e esquema, sem registos individuais.
Os commits são locais e incluem apenas código, testes e documentação.
