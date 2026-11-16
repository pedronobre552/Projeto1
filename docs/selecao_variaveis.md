# Seleção de variáveis para a perfilagem de acidentes

**Histórico da discussão inicial, não seleção atual da análise exploratória.**
Depois destas escolhas, o objetivo imediato foi clarificado: selecionar variáveis
para a EDA segundo as perguntas de investigação. Consultar a
[classificação provisória da EDA](classificacao_provisoria_eda.md). As decisões
abaixo são preservadas como histórico; não são uma seleção final para agrupamento.

Decisões do utilizador recebidas na conversa em 2026-11-16. As variáveis não decididas permanecem explicitamente como **Por decidir**. Esta seleção é documental; não foram transformados ou eliminados campos nos CSV de dados.

## Papéis

- **Identificadora**: entra na formação dos perfis.
- **Caracterizadora**: descreve e compara os perfis depois de formados.
- **Técnica**: permite ligações, validação ou rastreabilidade.
- **Caracterizadora / técnica**: acumula esses dois papéis sem formar os perfis.
- **Excluir**: fica fora da seleção analítica, mantendo os originais.
- **Por decidir**: nenhuma decisão registada.

## Cuidados de análise

A unidade pretendida é o acidente. Variáveis de pessoas e veículos exigem agregação antes da perfilagem; juntar diretamente as tabelas pode multiplicar registos. As repetições de nomes nos quatro CSV têm decisões separadas. A chave de ligação é `(ano, Id. Acidente)`.

As três contagens de vítimas foram selecionadas como identificadoras. Assim, a gravidade participará na formação dos perfis; diferenças de gravidade entre esses perfis não constituirão uma validação independente.

As exclusões de latitude/longitude e de Datahora da formação dos perfis não impedem o uso técnico dos dados originais, se necessário para enriquecimento futuro. Datahora foi escolhida como técnica. A exclusão de Distrito exigirá verificar se Concelho/Freguesia continuam inequivocamente identificados nas ligações geográficas.

As descrições, os cuidados e os anos de disponibilidade estão no ficheiro local
`docs/selecao_variaveis.csv`, com uma linha para cada uma das 171 colunas. Esse CSV
documental não é publicado no GitHub. Os significados completos e fontes
permanecem nos [dicionários](dicionarios/README.md).

## acidentes.csv

53 de 55 variáveis com decisão.

| Variável | Categoria |
| --- | --- |
| `ano` | Caracterizadora / técnica |
| `Id. Acidente` | Técnica |
| `Datahora` | Técnica |
| `Dia` | Caracterizadora / técnica |
| `Mês` | Caracterizadora / técnica |
| `Hora` | Caracterizadora / técnica |
| `Entidades Fiscalizadoras` | Excluir |
| `Velocidade local` | Identificadora |
| `Velocidade geral` | Excluir |
| `Dia da Semana` | Caracterizadora |
| `Latitude GPS` | Excluir |
| `Longitude GPS` | Excluir |
| `Num. Mortos a 30 dias` | Identificadora |
| `Num. Feridos graves a 30 dias` | Identificadora |
| `Num. Feridos ligeiros a 30 dias` | Identificadora |
| `Características Tecnicas1` | Identificadora |
| `Cond Aderência` | Identificadora |
| `Distrito` | Excluir |
| `Concelho` | Caracterizadora / técnica |
| `Freguesia` | Caracterizadora / técnica |
| `Pov. Proxima` | Excluir |
| `Nome arruamento` | Excluir |
| `Tipos Vias` | Identificadora |
| `Cod Via` | Excluir |
| `Estado Conservação` | Identificadora |
| `Km` | Excluir |
| `Factores Atmosféricos` | Caracterizadora / técnica |
| `Reg Circulação1` | Por decidir |
| `Intersecção Vias` | Identificadora |
| `Localizações` | Identificadora |
| `Luminosidade` | Caracterizadora |
| `Marca Via` | Caracterizadora |
| `Natureza` | Identificadora |
| `Obras Arte` | Identificadora |
| `Obstáculos` | Identificadora |
| `Sentidos` | Excluir |
| `Sinais` | Identificadora |
| `Sinais Luminosos` | Identificadora |
| `Tipo Piso` | Identificadora |
| `Traçado 1` | Identificadora |
| `Traçado 2` | Identificadora |
| `Traçado 3` | Identificadora |
| `Traçado 4` | Identificadora |
| `Via Trânsito` | Por decidir |
| `Ano` | Excluir |
| `Nome Outra Via` | Excluir |
| `Desc. Esquema` | Excluir |
| `Num veículos envolvidos` | Excluir |
| `Num veículos ligeiros` | Excluir |
| `Num veículos pesados` | Excluir |
| `Num ciclomotores/motociclos` | Excluir |
| `Num outros veículos` | Excluir |
| `ficheiro_origem` | Técnica |
| `folha_origem` | Técnica |
| `linha_origem` | Técnica |

## condutores_veiculos.csv

1 de 47 variáveis com decisão.

| Variável | Categoria |
| --- | --- |
| `ano` | Caracterizadora / técnica |
| `Id. Acidente` | Por decidir |
| `Datahora` | Por decidir |
| `Sexo` | Por decidir |
| `Lesões a 30 dias` | Por decidir |
| `Licença Condução` | Por decidir |
| `Teste Alcool` | Por decidir |
| `Acções Condutores` | Por decidir |
| `Inf. Comp. a Acções e Manobras` | Por decidir |
| `Nomeoutrosfactores` | Por decidir |
| `Tempo Condução Continuada` | Por decidir |
| `Acessórios Condutores` | Por decidir |
| `Categoria Veículos` | Por decidir |
| `Tipo Veiculo` | Por decidir |
| `Tipo Serviço` | Por decidir |
| `Veiculo Especial` | Por decidir |
| `Ano matricula` | Por decidir |
| `Inspecção Periódica` | Por decidir |
| `Certificado Adr` | Por decidir |
| `Carga Lotação` | Por decidir |
| `Pneus` | Por decidir |
| `Seguros` | Por decidir |
| `Distrito` | Por decidir |
| `Concelho` | Por decidir |
| `Condutor Gr.Etario(<=5) SUM` | Por decidir |
| `Condutor Gr.Etario(6-9) SUM` | Por decidir |
| `Condutor Gr.Etario(10-14) SUM` | Por decidir |
| `Condutor Gr.Etario(15-17) SUM` | Por decidir |
| `Condutor Gr.Etario(18-20) SUM` | Por decidir |
| `Condutor Gr.Etario(21-24) SUM` | Por decidir |
| `Condutor Gr.Etario(25-29) SUM` | Por decidir |
| `Condutor Gr.Etario(30-34) SUM` | Por decidir |
| `Condutor Gr.Etario(35-39) SUM` | Por decidir |
| `Condutor Gr.Etario(40-44) SUM` | Por decidir |
| `Condutor Gr.Etario(45-49) SUM` | Por decidir |
| `Condutor Gr.Etario(50-54) SUM` | Por decidir |
| `Condutor Gr.Etario(55-59) SUM` | Por decidir |
| `Condutor Gr.Etario(65-69) SUM` | Por decidir |
| `Condutor Gr.Etario(70-74) SUM` | Por decidir |
| `Condutor Gr.Etario(>=75) SUM` | Por decidir |
| `Condutor Gr.Etario(Não Def.) SUM` | Por decidir |
| `Id. Veículo` | Por decidir |
| `Reboque` | Por decidir |
| `Condutor Gr.Etario(60-64) SUM` | Por decidir |
| `ficheiro_origem` | Por decidir |
| `folha_origem` | Por decidir |
| `linha_origem` | Por decidir |

## passageiros.csv

1 de 33 variáveis com decisão.

| Variável | Categoria |
| --- | --- |
| `ano` | Caracterizadora / técnica |
| `Id. Acidente` | Por decidir |
| `Datahora` | Por decidir |
| `Entidades Fiscalizadoras` | Por decidir |
| `Id. Passageiro` | Por decidir |
| `Lesões a 30 dias` | Por decidir |
| `Sexo` | Por decidir |
| `Posição Veiculo` | Por decidir |
| `Acessórios Passageiro` | Por decidir |
| `Distrito` | Por decidir |
| `Concelho` | Por decidir |
| `Passageiro Gr.Etario(<=5) SUM` | Por decidir |
| `Passageiro Gr.Etario(6-9) SUM` | Por decidir |
| `Passageiro Gr.Etario(10-14) SUM` | Por decidir |
| `Passageiro Gr.Etario(15-17) SUM` | Por decidir |
| `Passageiro Gr.Etario(18-20) SUM` | Por decidir |
| `Passageiro Gr.Etario(21-24) SUM` | Por decidir |
| `Passageiro Gr.Etario(25-29) SUM` | Por decidir |
| `Passageiro Gr.Etario(30-34) SUM` | Por decidir |
| `Passageiro Gr.Etario(35-39) SUM` | Por decidir |
| `Passageiro Gr.Etario(40-44) SUM` | Por decidir |
| `Passageiro Gr.Etario(45-49) SUM` | Por decidir |
| `Passageiro Gr.Etario(50-54) SUM` | Por decidir |
| `Passageiro Gr.Etario(55-59) SUM` | Por decidir |
| `Passageiro Gr.Etario(60-64) SUM` | Por decidir |
| `Passageiro Gr.Etario(65-69) SUM` | Por decidir |
| `Passageiro Gr.Etario(70-74) SUM` | Por decidir |
| `Passageiro Gr.Etario(>=75) SUM` | Por decidir |
| `Passageiro Gr.Etario(Não Def.) SUM` | Por decidir |
| `Id. Veículo` | Por decidir |
| `ficheiro_origem` | Por decidir |
| `folha_origem` | Por decidir |
| `linha_origem` | Por decidir |

## peoes.csv

1 de 36 variáveis com decisão.

| Variável | Categoria |
| --- | --- |
| `ano` | Caracterizadora / técnica |
| `Id. Acidente` | Por decidir |
| `Freguesia` | Por decidir |
| `Tipo Natureza` | Por decidir |
| `Natureza` | Por decidir |
| `Datahora` | Por decidir |
| `Entidades Fiscalizadoras` | Por decidir |
| `Id. Peao` | Por decidir |
| `Sexo` | Por decidir |
| `Acções Peão` | Por decidir |
| `Distrito` | Por decidir |
| `Concelho` | Por decidir |
| `Lesões a 30 dias` | Por decidir |
| `Peao Gr.Etario(<=5) SUM` | Por decidir |
| `Peao Gr.Etario(6-9) SUM` | Por decidir |
| `Peao Gr.Etario(10-14) SUM` | Por decidir |
| `Peao Gr.Etario(15-17) SUM` | Por decidir |
| `Peao Gr.Etario(18-20) SUM` | Por decidir |
| `Peao Gr.Etario(21-24) SUM` | Por decidir |
| `Peao Gr.Etario(25-29) SUM` | Por decidir |
| `Peao Gr.Etario(30-34) SUM` | Por decidir |
| `Peao Gr.Etario(35-39) SUM` | Por decidir |
| `Peao Gr.Etario(40-44) SUM` | Por decidir |
| `Peao Gr.Etario(45-49) SUM` | Por decidir |
| `Peao Gr.Etario(50-54) SUM` | Por decidir |
| `Peao Gr.Etario(55-59) SUM` | Por decidir |
| `Peao Gr.Etario(60-64) SUM` | Por decidir |
| `Peao Gr.Etario(65-69) SUM` | Por decidir |
| `Peao Gr.Etario(70-74) SUM` | Por decidir |
| `Peao Gr.Etario(>=75) SUM` | Por decidir |
| `Peao Gr.Etario(Não Def.) SUM` | Por decidir |
| `Tipo Peão` | Por decidir |
| `Material Reflector` | Por decidir |
| `ficheiro_origem` | Por decidir |
| `folha_origem` | Por decidir |
| `linha_origem` | Por decidir |
