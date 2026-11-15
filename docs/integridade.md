# Como se verifica a correspondência com os originais

O objetivo é demonstrar que os quatro CSV reproduzem os dados dos Excel anuais,
admitindo apenas as transformações documentadas. Não basta contar linhas: um
valor poderia ser alterado sem mudar o número de registos.

Há duas verificações complementares. `verificar_resultados.py` confere a
estrutura dos CSV contra a auditoria produzida durante a união.
`verificar_originais.py` volta a abrir os Excel e compara diretamente todos os
valores com os CSV. A segunda verificação não usa `auditoria.json`, o mapa de
folhas nem as funções de transformação de `join.py` para calcular o esperado.

## Controlos e evidência

| Controlo | O que é verificado | O que permite detetar |
| --- | --- | --- |
| Fontes e folhas | Descoberta dos Excel anuais e das quatro entidades em cada ficheiro | Fontes/folhas inesperadas, ausentes ou repetidas |
| Cabeçalhos | Reconstrução da união de colunas a partir dos Excel e comparação com os cabeçalhos dos CSV | Colunas omitidas, acrescentadas ou colocadas na ordem errada |
| Estrutura e contagens | Número de campos e de registos por entidade, ficheiro e folha | Linhas perdidas/extra e CSV mal formados |
| Proveniência | Ficheiro, folha e número da linha original, comparados com cada registo | Registos atribuídos à origem errada ou fora da ordem esperada |
| Valores | Comparação de todas as células, incluindo campos vazios | Valores alterados, colunas trocadas e preenchimentos indevidos |
| Ano | `ano` comparado com o nome da fonte; auditoria também compara com a data quando existente | Atribuição errada do ano; divergências entre ano e data nas fontes |
| SHA-256 | Hash dos bytes dos 12 Excel e dos quatro CSV, antes e depois da comparação, no conjunto atual | Alterações dos ficheiros entre os dois momentos e identificação das versões verificadas |

As contagens e o número de ficheiros dependem do conjunto existente em cada
execução. O script descobre as fontes novamente, sem fixar o resultado às
contagens de uma execução anterior.

## Comparação direta, passo a passo

1. Calcular os hashes SHA-256 dos Excel e dos quatro CSV.
2. Abrir os Excel em modo de leitura, localizar o cabeçalho verdadeiro e
   associar cada folha à entidade correta pelo nome. Não depender da posição
   da folha no livro. Rejeitar cabeçalhos ambíguos e campos sem nome.
3. Reconstruir a lista completa de colunas de cada entidade e verificar se
   coincide com o cabeçalho do CSV correspondente.
4. Voltar a percorrer todas as linhas não vazias dos Excel. Para cada uma,
   construir a representação esperada no CSV, segundo as regras abaixo.
5. Ler o registo correspondente do CSV e comparar todas as suas colunas,
   incluindo `ano` e os três campos de proveniência. Não usar amostragem,
   aproximação de IDs ou tolerância para diferenças numéricas.
6. Confirmar que não faltam registos nem sobram linhas no fim dos CSV.
7. Recalcular os hashes e comparar com os do início. Só concluir `OK` se a
   comparação terminar sem erros, sem divergências e com hashes iguais.
8. Gravar um relatório local com o estado, o número de linhas/células percorridas,
   as contagens por fonte, os hashes, a hora de início/fim em UTC e o hash do
   próprio script executado.

O processamento é sequencial e não carrega os conjuntos completos em memória.
Os Excel e os CSV são abertos apenas para leitura. O verificador escreve
exclusivamente relatórios numa pasta separada dos dados.

## Diferenças de representação admitidas

Excel e CSV não são formatos equivalentes. A igualdade é verificada depois
destas transformações explícitas, sem aceitar outras alterações de valores:

| Elemento | Regra aceite |
| --- | --- |
| Cabeçalhos | Uniformizar espaços; retirar o espaço antes dos parênteses dos grupos etários; retirar `SUM` apenas dos três contadores de vítimas a 30 dias |
| `Id. Acidente` | Representar como texto, retirar espaços exteriores e evitar `.0` em números integrais; manter códigos alfanuméricos e zeros iniciais já guardados como texto |
| Célula vazia | Representar como campo vazio; Excel `None` e texto vazio não se distinguem no CSV |
| Coluna inexistente num ano | Exigir campo vazio no CSV unido; nunca substituir por zero |
| Fórmula/erro Excel | Preservar a expressão ou o erro como texto, sem calcular nem substituir pelo resultado em cache; fórmulas matriciais usam a sua expressão textual |
| Restantes valores | Comparar a representação textual da célula lida do Excel com o campo CSV; números, datas e horas são serializados para texto, sem arredondamento adicional |
| `ano` | Exigir os quatro algarismos do ano indicado no nome do Excel |
| Proveniência | Exigir nome do ficheiro, nome original da folha e número exato da linha, começando em 1 |
| Linha totalmente vazia | Não gerar registo; todas as restantes linhas têm de estar representadas, incluindo duplicados |

Assim, por exemplo, uma coluna histórica inexistente pode ficar vazia; um
valor presente no Excel não pode desaparecer nem passar para outra coluna.
Um zero continua zero. Valores com vírgulas, aspas ou mudanças de linha são
lidos com o módulo CSV, em vez de contar linhas físicas do ficheiro de texto.

## Como repetir e consultar o resultado

Com o Python e as dependências do projeto:

```powershell
python limpeza_tratamento/verificar_resultados.py
python limpeza_tratamento/verificar_originais.py
python -m unittest discover -s tests -v
```

O segundo comando pode demorar vários minutos porque relê integralmente os
Excel. Não é necessário regenerar os CSV para os comparar.
Usar `--input-dir`, `--csv-dir` e `--report-dir` para configurar os caminhos.

Os resultados desta comparação ficam fora do Git:

- [Resumo da comparação](../outputs/fase1/comparacao_originais.md):
  `outputs/fase1/comparacao_originais.md`.
- [Evidência completa](../outputs/fase1/comparacao_originais.json):
  `outputs/fase1/comparacao_originais.json`, com estado, hashes e contagens.
- `outputs/fase1/auditoria.json` e `resumo_auditoria.md`: diagnósticos da união e
  da verificação estrutural, que complementam a comparação direta.

O estado **OK** exige conclusão integral. Se houver erro de execução ou
diferenças, o estado é **FALHOU** e o comando termina com erro. O JSON identifica
as primeiras 20 divergências por ficheiro, folha, linha e coluna, sem copiar os
valores individuais. As restantes diferenças continuam a ser contabilizadas.
As contagens parciais de uma execução falhada não representam uma validação.

O resultado aplica-se aos ficheiros com os hashes registados nessa execução.
Depois de editar, regenerar ou substituir dados é necessário repetir a
verificação. Para comparar posteriormente o hash de um ficheiro com o valor
guardado em `sha256_depois`, pode usar-se, por exemplo:

```powershell
Get-FileHash -Algorithm SHA256 data_agregada/acidentes.csv
```

O hash desse CSV está na entrada `csv/acidentes.csv` do relatório JSON.
Reexecutar a comparação completa grava um novo relatório para os ficheiros
presentes; não constitui um histórico automático de todas as versões anteriores.

## Testes que sustentam o controlo

Os testes sintéticos cobrem cabeçalhos deslocados de 2023, variantes `SUM`,
códigos alfanuméricos, preservação de duplicados, fórmulas e erros, separação de
pastas e rastreabilidade. Há um teste que altera uma medida do CSV mantendo o
cabeçalho, o número de linhas e a proveniência: a verificação estrutural passa,
mas a comparação com o original falha e localiza a coluna alterada.
Este teste demonstra por que as duas verificações são necessárias.
Testam-se também linhas removidas, linhas acrescentadas e a substituição por
zero de um campo que deveria ficar vazio por ausência da coluna naquele ano.
O comparador rejeita estes três casos e aceita a preservação textual de fórmulas
matriciais e erros Excel no exemplo sintético correspondente.

## Limites da garantia

- **Fidelidade não é correção factual.** Um erro de preenchimento já presente
  no Excel pode ser reproduzido fielmente no CSV. O manual BEAV ajuda a
  interpretar e validar o domínio; não prova que cada ocorrência foi bem registada.
- **Os hashes identificam esta execução.** Não existia um hash de referência
  recolhido antes da primeira intervenção. Os hashes atuais não provam que os
  Excel nunca tenham sido alterados antes, nem autenticam os ficheiros junto da ANSR.
- **CSV não preserva um livro Excel inteiro.** Estilos, comentários, gráficos,
  formatos visuais, tipos nativos e resultados calculados de fórmulas não fazem
  parte da garantia. Zeros que só existam na formatação visual de um ID numérico
  não são recuperados. A expressão textual de uma fórmula é preservada.
- **A leitura partilha uma dependência.** O gerador e o comparador usam
  `openpyxl`; a implementação da comparação é separada, mas não é uma leitura
  independente por outro motor de Excel. Não se garante deteção de defeitos
  comuns à biblioteca.
- **A evidência é local e temporal.** Os hashes são comparados no início e no
  fim; não existe um snapshot atómico nem um bloqueio que impeça edições em
  simultâneo. O estado OK deve ser interpretado nesse contexto.

Esta combinação permite verificar a reprodução dos valores que foram lidos
das fontes, com regras conhecidas, rastreabilidade e evidência reproduzível.
