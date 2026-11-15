# Dicionários de dados

| CSV em `data_agregada/` | Dicionário | Colunas |
| --- | --- | ---: |
| `acidentes.csv` | [Acidentes](acidentes.md) | 55 |
| `condutores_veiculos.csv` | [Condutores e veículos](condutores_veiculos.md) | 47 |
| `passageiros.csv` | [Passageiros](passageiros.md) | 33 |
| `peoes.csv` | [Peões](peoes.md) | 36 |

Cada dicionário documenta todas as colunas, na ordem do CSV: significado,
tipo/unidade de leitura, anos em que a coluna existe na fonte, referência e
cuidados de interpretação. A cobertura anual não garante preenchimento de
todas as linhas. Não se incluem amostras de pessoas nem de localizações.

## Fontes e alcance

- **M**: [Manual de Preenchimento BEAV](../referencias/MANUAL%20PREENCHIMENTO%20BEAV.pdf),
  documento oficial fornecido localmente. Indicam-se grupo e página do PDF,
  contando a partir de 1.
- **B**: [Formulário BEAV](../referencias/BEAV.pdf), páginas 1–2. Confirma as opções
  e a numeração dos subgrupos. A edição fornecida indica validade até 31/12/2014;
  não demonstra codificação idêntica em todos os anos.
- **Exportação**: campo/transformação presente nos Excel sem correspondência
  literal especificada no manual. Inclui IDs, grupos etários, alguns nomes de
  coluna e classificação com seguimento a 30 dias.
- **Projeto**: `ano` e três campos de proveniência acrescentados pelo script.

As definições são paráfrases das fontes. O manual explica o preenchimento do
boletim; não fornece um dicionário exaustivo dos Excel distribuídos. A associação
dos nomes dos CSV aos campos BEAV é interpretação do projeto. Casos incertos
ficam assinalados. As regras desta edição não são apresentadas como legislação atual.

## Conceitos importantes

Segundo o manual, pp.6–7, uma vítima mortal a 30 dias morre no local ou nos 30
dias seguintes ao acidente. Ferido grave implica hospitalização superior a 24
horas sem morte nesse período. Ferido ligeiro/leve corresponde a lesões sem
hospitalização ou com hospitalização inferior a 24 horas, também sem morte
nesse período. Aplicar a classificação exportada, sem inventar regras para
situações-limite que o texto não esclarece.

O manual distingue condutor, passageiro e peão, incluindo neste último situações
específicas de deslocação ou permanência na via. Consultar a p.7 antes de
interpretar o grupo apenas como pessoas a caminhar.

## Como ler os dados

CSV não conserva tipos. Importar identificadores como **texto** e `ano` como
inteiro. Datas, horas e decimais exigem conversão validada; evitar conversões
automáticas de Excel que modifiquem códigos.

Um campo vazio pode significar ausência da coluna no ano, informação não
registada ou campo não aplicável. Não substituir indiscriminadamente por zero.
Não definido, ignorado, inexistente e não aplicável têm significados distintos:
um sinal inexistente pode ser observação válida; idade não definida é desconhecida.

Os grupos etários são campos da exportação, não idades exatas. Não interpretar
`SUM` como unidade de idade nem reconstruir idades pontuais sem regra definida.
Em condutores, o grupo 60–64 só aparece nos anos recentes; a ausência histórica
da coluna não demonstra ausência de condutores desse grupo.

A relação entre entidades usa `(ano, Id. Acidente)`. As tabelas de pessoas podem
ter múltiplas linhas por acidente. A seleção de variáveis e as agregações ficam
para depois. A proveniência mantém-se para auditoria, sem a usar como preditor.

## Atualização

Definições no script comentado `limpeza_tratamento/gerar_dicionarios.py`.
Depois de gerar e verificar os CSV:

```powershell
python limpeza_tratamento/gerar_dicionarios.py
```

O gerador exige correspondência exata entre cabeçalho e auditoria e recusa
colunas novas sem definição. Lê cabeçalhos e metadados, sem copiar registos.
Os tipos indicados são os esperados para leitura; os tipos encontrados e os
nulos estão na auditoria local.
