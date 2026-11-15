# Projeto de acidentes rodoviários

Base nacional por ano, ainda sem seleção das variáveis finais. Os dados ficam
locais; apenas código, testes e documentação são versionados. Não fazer push
sem instrução do utilizador.

## Onde está cada coisa

| Pasta | Conteúdo |
| --- | --- |
| `data/` | Excel anuais originais, preservados |
| `data_agregada/` | Quatro CSV finais, com todos os anos e `ano` |
| `meteo/` | Dois CSV: meteorologia horária e horas solares diárias por concelho, 2010–2024 |
| `jogos/` | CSV dos jogos oficiais do Braga, 2010–2024 |
| `aquisicao/` | Scripts de aquisição da meteorologia e dos jogos |
| `docs/dicionarios/` | Dicionários completos e regras de interpretação |
| `docs/referencias/` | Formulário BEAV, manual e relatório da Parte I |
| `outputs/fase1/` | Auditoria detalhada e resumo dos resultados |
| `limpeza_tratamento/` | Scripts comentados de geração, verificação e documentação |
| `tests/` | Testes com dados sintéticos |

Dados, PDF, relatórios e ambiente virtual estão excluídos do Git.

## Documentação

- [Dicionários dos quatro CSV](docs/dicionarios/README.md)
- [Procedimento da união dos anos](docs/fase1.md)
- [Como se verifica a correspondência com os originais](docs/integridade.md)
- [Organização e registo da limpeza](docs/organizacao.md)
- [Meteorologia: colunas, coordenadas e origem](docs/meteo.md)
- [Jogos do Braga: aquisição, dicionário e limitações](docs/jogos_braga.md)
- [Registo do que foi feito e evidência para auditoria](docs/registo_trabalho.md)

## Como repetir

Na primeira utilização, instalar as dependências:

```powershell
python -m pip install -r requirements.txt
```

Depois basta um comando para unir, verificar, documentar e obter meteorologia e jogos:

```powershell
python executar.py
```

O processo segue a ordem abaixo e para se alguma etapa falhar. Usa o mesmo
Python em todas as etapas. A meteorologia e as páginas de jogos já descarregadas são reutilizadas.
Para executar uma etapa isoladamente:

```powershell
python limpeza_tratamento/join.py
python limpeza_tratamento/verificar_resultados.py
python limpeza_tratamento/verificar_originais.py
python limpeza_tratamento/gerar_dicionarios.py
python aquisicao/obter_meteo.py
python aquisicao/obter_jogos_braga.py
python -m unittest discover -s tests -v
```

`join.py` lê `data/acidentes-AAAA.xlsx`, escreve os CSV em `data_agregada/`
e a auditoria em `outputs/fase1/`. Não altera os Excel originais.
`verificar_resultados.py` confere os CSV e grava o resumo da auditoria.
`verificar_originais.py` compara todos os valores com os Excel, sem amostragem,
e regista hashes SHA-256 e evidência em `outputs/fase1/comparacao_originais.*`.
`gerar_dicionarios.py` documenta os cabeçalhos e os anos de disponibilidade.
Usar `--help` para configurar caminhos. `join.py --audit-only` atualiza apenas
a auditoria, não os CSV; não substitui uma regeneração completa.

## Regras para continuar

Mantêm-se todos os distritos, anos e campos. A seleção de variáveis depende do
objetivo futuro. As quatro entidades continuam separadas; juntá-las diretamente
pode multiplicar registos. Ler IDs como texto e `ano` como inteiro.
Uma coluna ausente num ano não equivale a zero. Faltam os ficheiros de 2020–2022.

Antes de um commit, rever `git status --short` e `git diff --cached --stat`.
Adicionar apenas caminhos explícitos de código/documentação e manter os commits locais.
