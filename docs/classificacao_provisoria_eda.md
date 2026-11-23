# Classificação provisória para a análise exploratória

> Documento histórico do estudo de Braga. A análise em curso usa as contagens
> diárias nacionais por tipo. Consultar o [notebook](../analise/eda_acidentes_diarios.ipynb)
> e a [documentação da meteorologia diária](meteo_diaria.md).

Proposta de 2026-11-16, orientada pelas perguntas de investigação do estudo inicial. A seleção anterior para perfis permanece em `selecao_variaveis.md`. Esta proposta documenta a preparação da análise inicial de Braga.

### Decisões de âmbito confirmadas na conversa

- A análise será recortada para **Braga numa etapa posterior**. Os agregados nacionais continuam intactos. Antes de executar o filtro, explicitar se Braga significa distrito ou concelho; a fonte meteorológica atual cobre os 14 concelhos do distrito.
- Manter **encandeamento registado** e **potencial de encandeamento estimado** como medidas separadas e complementares. O segundo será construído com dados solares/meteorológicos, sem substituir Luminosidade nem assumir ocorrência confirmada.
- A concordância e as discordâncias entre os indicadores poderão ser analisadas por tipo de acidente. Discordância não comprova erro de preenchimento nem erro da estimativa.
- Não foram ainda escolhidos limiares de proximidade ao nascer/pôr do sol ou radiação, nem calculados indicadores, feitas ligações ou executada a EDA.

## Perguntas

- **Q0 — Tipos e evolução:** número e composição dos tipos de acidentes em 2010–2019 e 2023–2024.
- **Q1 — Luz e meteorologia:** associação de tipo de acidente com sol encandeante registado, proximidade ao nascer/pôr do sol, dia/noite e condições meteorológicas.
- **Q2 — Futebol:** associação entre períodos de jogos do Braga e grandes clubes e número/tipo de acidentes.
- **Q3 — Veículos:** associação entre tipo de acidente e idade aproximada, categoria, utilização e condições de carga/lotação.

## Leitura da classificação

**Inicial:** entra na primeira EDA. **Suporte:** necessário para ligações, validação ou localização, sem exigir gráficos próprios. **Secundária:** analisar se esclarecer um resultado inicial. **Reserva:** preservar para necessidade técnica futura. **Fora da EDA inicial:** não explorar nesta fase; não eliminar dos originais.

O papel é separado da prioridade: resultado, fator, contexto ou técnica. Nenhum destes papéis decide ainda a entrada futura na formação de perfis. Contexto não significa ajuste estatístico obrigatório; escolher ajustes segundo cada pergunta.

## Regras e limites

- Unidade principal: acidente, com chave `(ano, Id. Acidente)`. Para idade/categoria, pode existir uma análise separada por veículo associado a acidente; declarar esse denominador e não tratar linhas de veículos como acidentes independentes.
- Validar unicidade e cobertura antes de agregar. Um acidente pode envolver veículos de várias categorias/idades; indicadores por categoria podem sobrepor-se e as suas contagens não têm de somar o total de acidentes.
- A disponibilidade da coluna não mede o preenchimento. A proposta é conceptual; faltas e distribuições ainda não foram avaliadas nesta etapa.
- Não imputar zero quando uma coluna ou ano está ausente. 2020–2022 não são períodos sem acidentes.
- Datahora é fonte preferida do calendário após validação. Validar hora legal, mudanças de hora e associação ao intervalo meteorológico: precipitação/radiação atuais referem-se à hora anterior ao instante indicado.
- O número de acidentes é uma variável derivada da contagem de acidentes únicos por intervalo/área. Para jogos, criar também intervalos observados sem acidentes; períodos sem fonte não recebem zero. Comparar janelas equivalentes em duração, hora, dia da semana, época e área.
- O recorte futuro para Braga está confirmado; a unidade administrativa exata deve ser explicitada antes do filtro. Os acidentes são nacionais; as fontes meteorológicas/solares atuais cobrem os 14 concelhos do distrito de Braga. Não atribuir esses valores a acidentes de outros distritos.
- A fonte atual de jogos é do Braga. Inclui adversários grandes clubes quando jogam contra o Braga, mas não constitui o calendário completo desses clubes. Benfica, Porto e Sporting são uma hipótese de âmbito a confirmar, não uma definição já acordada.
- Casa/fora no CSV dos jogos não comprova estádio/município. Não existe hora de fim nem duração real: janelas posteriores ao início são aproximações explicitamente definidas, não o fim real do jogo.
- Sol encandeante registado em Luminosidade e proximidade a nascer/pôr do sol são medidas distintas. As fontes solares atuais não fornecem orientação de circulação nem comprovam encandeamento.
- Idade do veículo é aproximada por diferença de anos. Carga Lotação não é capacidade nem número de ocupantes. O significado pretendido de lotação permanece por definir; passageiros não permitem reconstruir ocupação completa sem validação.
- Associações entre acidentes não demonstram causalidade nem risco por veículo sem dados de exposição à circulação.

## Variáveis derivadas e fontes externas a preparar

| Elemento | Papel / prioridade | Origem e cuidado |
| --- | --- | --- |
| Número de acidentes por intervalo e área | Resultado / inicial Q0, Q2 | Contar acidentes únicos e incluir intervalos observados com zero. |
| Tipo amplo de acidente | Resultado / inicial Q0–Q3 | Derivar de Natureza por correspondência validada; preservar detalhe. Não depender de Tipo Natureza na tabela de peões. |
| Data, hora/faixa horária, dia da semana e mês | Contexto / inicial Q0–Q3 | Derivar de Datahora; bandas horárias justificadas pela pergunta. |
| Idade aproximada do veículo | Fator / inicial Q3 | ano − Ano matricula; só valores válidos, sem inventar data de matrícula exata. |
| Dia/noite calculado | Fator / inicial Q1 | Datahora e nascer_sol/por_sol por concelho; manter Luminosidade registada em separado. |
| Distância temporal ao nascer/pôr do sol | Fator / inicial Q1 | Calcular minutos; explorar antes de fixar limiar. Não chamar encandeamento confirmado. |
| Precipitação, nebulosidade e radiação direta | Fatores / inicial Q1; contexto Q2 | meteorologia_horaria.csv: precipitacao_mm, nebulosidade_pct, radiacao_direta_w_m2. Reanálise por referência municipal, não medição no acidente. |
| Temperatura, vento, código meteorológico | Fatores / secundária Q1 | temperatura_c, vento_kmh, codigo_tempo_wmo. Escolher conforme padrões observados. |
| Humidade e radiação global | Reserva analítica Q1 | humidade_pct, radiacao_solar_w_m2; avaliar valor adicional e redundância antes de explorar. |
| Município e instantes meteorológicos | Técnica / suporte | municipio, data_hora_utc, data_hora_local; validar ligação temporal e nomes. |
| Data e horas solares | Técnica / suporte | sol_diario.csv: municipio, data, nascer_sol, por_sol. |
| Data/hora de jogo e clube | Fator / inicial Q2 | Calendário atual do Braga; adquirir calendários completos de outros clubes se incluídos no âmbito. |
| Presença de jogo e janela relativa ao início | Fator / inicial Q2 | Derivar com regra explícita; permitir jogos simultâneos sem multiplicar contagens de acidentes. |
| Adversário, competição, casa/fora | Contexto / inicial Q2 | adversario, competicao, condicao_braga_fonte. Estádio/município não estão confirmados por estes campos. |
| ID do jogo, URL e época | Técnica / suporte Q2 | id_jogo, url_fonte, epoca; conservar proveniência. Fase e resultado ficam secundários. |

## Classificação completa dos quatro CSV


### acidentes.csv

Inicial: 11; Suporte: 19; Secundária: 18; Reserva: 6; Fora da EDA inicial: 1.

| Variável | Prioridade | Papel | Perguntas | Justificação |
| --- | --- | --- | --- | --- |
| `ano` | Inicial | Contexto / técnica | Q0; Q1; Q2; Q3 | Comparação temporal e chave com Id. Acidente; necessário também para derivar idade do veículo. |
| `Id. Acidente` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `Datahora` | Inicial | Contexto / técnica | Q0; Q1; Q2; Q3 | Base para hora, calendário, ligação solar/meteorológica e janelas de jogos; validar formato e fuso horário. |
| `Dia` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir com Datahora e ano. Usar mês, hora e dia da semana derivados e validados; dia do mês não é fator prioritário isoladamente. |
| `Mês` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir com Datahora e ano. Usar mês, hora e dia da semana derivados e validados; dia do mês não é fator prioritário isoladamente. |
| `Hora` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir com Datahora e ano. Usar mês, hora e dia da semana derivados e validados; dia do mês não é fator prioritário isoladamente. |
| `Entidades Fiscalizadoras` | Suporte | Técnica / qualidade | Q0 | Verificar alterações no padrão de registo entre entidades/anos se surgirem quebras; sem cruzamentos substantivos iniciais. |
| `Velocidade local` | Inicial | Contexto | Q1; Q2; Q3 | Estratificar comparações por ambiente rodoviário; velocidade local é limite permitido, não velocidade observada. Evitar abrir todos os cruzamentos de início. |
| `Velocidade geral` | Suporte | Validação / alternativa | Q1; Q2; Q3 | Conferir relação com Velocidade local; avaliar como alternativa se esta não tiver qualidade suficiente. Não substituir automaticamente. |
| `Dia da Semana` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir com Datahora e ano. Usar mês, hora e dia da semana derivados e validados; dia do mês não é fator prioritário isoladamente. |
| `Latitude GPS` | Suporte | Contexto / técnica | Q1; Q2 | Validar localização e permitir análises espaciais. A meteorologia atual liga por concelho; GPS não é requisito dessa ligação. Freguesias exigem harmonização histórica. |
| `Longitude GPS` | Suporte | Contexto / técnica | Q1; Q2 | Validar localização e permitir análises espaciais. A meteorologia atual liga por concelho; GPS não é requisito dessa ligação. Freguesias exigem harmonização histórica. |
| `Num. Mortos a 30 dias` | Secundária | Resultado complementar | Complementar | Descrever gravidade depois dos resultados de número/tipo; não é prioridade das perguntas atuais e não conta acidentes. |
| `Num. Feridos graves a 30 dias` | Secundária | Resultado complementar | Complementar | Descrever gravidade depois dos resultados de número/tipo; não é prioridade das perguntas atuais e não conta acidentes. |
| `Num. Feridos ligeiros a 30 dias` | Secundária | Resultado complementar | Complementar | Descrever gravidade depois dos resultados de número/tipo; não é prioridade das perguntas atuais e não conta acidentes. |
| `Características Tecnicas1` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Cond Aderência` | Inicial | Fator | Q1; Q2 | Condições registadas no acidente; cruzar com tipo e luminosidade e contextualizar jogos. Aderência pode fazer parte da relação meteorológica, não assumir controlo obrigatório. |
| `Distrito` | Inicial | Contexto / técnica | Q0; Q1; Q2; Q3 | Definir universo territorial e comparações; Distrito desambigua concelhos e permite selecionar a cobertura meteorológica de Braga. |
| `Concelho` | Inicial | Contexto / técnica | Q0; Q1; Q2; Q3 | Definir universo territorial e comparações; Distrito desambigua concelhos e permite selecionar a cobertura meteorológica de Braga. |
| `Freguesia` | Suporte | Contexto / técnica | Q1; Q2 | Validar localização e permitir análises espaciais. A meteorologia atual liga por concelho; GPS não é requisito dessa ligação. Freguesias exigem harmonização histórica. |
| `Pov. Proxima` | Reserva | Técnica condicional | Q1; Q2 | Guardar para eventual reconstrução/validação espacial. Sentidos é crescente/decrescente e não fornece azimute; isoladamente não demonstra encandeamento. |
| `Nome arruamento` | Reserva | Técnica condicional | Q1; Q2 | Guardar para eventual reconstrução/validação espacial. Sentidos é crescente/decrescente e não fornece azimute; isoladamente não demonstra encandeamento. |
| `Tipos Vias` | Inicial | Contexto | Q1; Q2; Q3 | Estratificar comparações por ambiente rodoviário; velocidade local é limite permitido, não velocidade observada. Evitar abrir todos os cruzamentos de início. |
| `Cod Via` | Reserva | Técnica condicional | Q1; Q2 | Guardar para eventual reconstrução/validação espacial. Sentidos é crescente/decrescente e não fornece azimute; isoladamente não demonstra encandeamento. |
| `Estado Conservação` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Km` | Reserva | Técnica condicional | Q1; Q2 | Guardar para eventual reconstrução/validação espacial. Sentidos é crescente/decrescente e não fornece azimute; isoladamente não demonstra encandeamento. |
| `Factores Atmosféricos` | Inicial | Fator | Q1; Q2 | Condições registadas no acidente; cruzar com tipo e luminosidade e contextualizar jogos. Aderência pode fazer parte da relação meteorológica, não assumir controlo obrigatório. |
| `Reg Circulação1` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Intersecção Vias` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Localizações` | Inicial | Contexto | Q1; Q2; Q3 | Estratificar comparações por ambiente rodoviário; velocidade local é limite permitido, não velocidade observada. Evitar abrir todos os cruzamentos de início. |
| `Luminosidade` | Inicial | Fator | Q1 | Central para sol encandeante registado, crepúsculo e noite com/sem iluminação; não substituir pelo indicador dia/noite calculado. |
| `Marca Via` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Natureza` | Inicial | Resultado | Q0; Q1; Q2; Q3 | Tipo de acidente é o resultado central; harmonizar categorias entre anos e derivar grupos amplos apenas com correspondência validada. |
| `Obras Arte` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Obstáculos` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Sentidos` | Reserva | Técnica condicional | Q1; Q2 | Guardar para eventual reconstrução/validação espacial. Sentidos é crescente/decrescente e não fornece azimute; isoladamente não demonstra encandeamento. |
| `Sinais` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Sinais Luminosos` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Tipo Piso` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Traçado 1` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Traçado 2` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Traçado 3` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Traçado 4` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Via Trânsito` | Secundária | Contexto complementar | Q1; Q3 | Infraestrutura/configuração da via: explorar apenas para esclarecer um padrão observado. Verificar cobertura, desconhecidos e redundância antes de cruzar. |
| `Ano` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir com Datahora e ano. Usar mês, hora e dia da semana derivados e validados; dia do mês não é fator prioritário isoladamente. |
| `Nome Outra Via` | Reserva | Técnica condicional | Q1; Q2 | Guardar para eventual reconstrução/validação espacial. Sentidos é crescente/decrescente e não fornece azimute; isoladamente não demonstra encandeamento. |
| `Desc. Esquema` | Fora da EDA inicial | Sem uso inicial | — | Apenas 2023 e interpretação a confirmar; Natureza é a fonte principal para tipos. |
| `Num veículos envolvidos` | Suporte | Validação / cobertura limitada | Q3 | Apenas 2024; útil para verificar contagens derivadas dos veículos nesse ano, sem extrapolar ausência histórica para zero. |
| `Num veículos ligeiros` | Suporte | Validação / cobertura limitada | Q3 | Apenas 2024; útil para verificar contagens derivadas dos veículos nesse ano, sem extrapolar ausência histórica para zero. |
| `Num veículos pesados` | Suporte | Validação / cobertura limitada | Q3 | Apenas 2024; útil para verificar contagens derivadas dos veículos nesse ano, sem extrapolar ausência histórica para zero. |
| `Num ciclomotores/motociclos` | Suporte | Validação / cobertura limitada | Q3 | Apenas 2024; útil para verificar contagens derivadas dos veículos nesse ano, sem extrapolar ausência histórica para zero. |
| `Num outros veículos` | Suporte | Validação / cobertura limitada | Q3 | Apenas 2024; útil para verificar contagens derivadas dos veículos nesse ano, sem extrapolar ausência histórica para zero. |
| `ficheiro_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `folha_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `linha_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |

### condutores_veiculos.csv

Inicial: 5; Suporte: 8; Secundária: 25; Fora da EDA inicial: 9.

| Variável | Prioridade | Papel | Perguntas | Justificação |
| --- | --- | --- | --- | --- |
| `ano` | Inicial | Contexto / técnica | Q0; Q1; Q2; Q3 | Comparação temporal e chave com Id. Acidente; necessário também para derivar idade do veículo. |
| `Id. Acidente` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `Datahora` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Sexo` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Lesões a 30 dias` | Secundária | Resultado complementar | Complementar | Gravidade do condutor, diferente da gravidade global do acidente; não somar tabelas sem validar âmbito e duplicações. |
| `Licença Condução` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Teste Alcool` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Acções Condutores` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Inf. Comp. a Acções e Manobras` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Nomeoutrosfactores` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Tempo Condução Continuada` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Acessórios Condutores` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Categoria Veículos` | Inicial | Fator | Q3 | Fator central da pergunta sobre veículos; comparar composição dos tipos, sem inferir risco sem exposição de circulação. |
| `Tipo Veiculo` | Inicial | Fator | Q3 | Distinguir utilização como passageiros/mercadorias quando aplicável; analisar em conjunto com categoria. |
| `Tipo Serviço` | Secundária | Contexto complementar | Q3 | Pode esclarecer padrões de categoria/idade/carga; não abrir cruzamentos antes dos fatores centrais. |
| `Veiculo Especial` | Secundária | Contexto complementar | Q3 | Pode esclarecer padrões de categoria/idade/carga; não abrir cruzamentos antes dos fatores centrais. |
| `Ano matricula` | Inicial | Fator | Q3 | Derivar idade aproximada = ano do acidente − ano da primeira matrícula; validar extremos, valores desconhecidos e categorias aplicáveis. |
| `Inspecção Periódica` | Secundária | Contexto complementar | Q3 | Pode esclarecer padrões de categoria/idade/carga; não abrir cruzamentos antes dos fatores centrais. |
| `Certificado Adr` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Carga Lotação` | Inicial | Fator | Q3 | Fator central provisório: mistura carga, acondicionamento e excesso de lotação. Não indica capacidade nem número exato de ocupantes; definição de lotação ainda pendente. |
| `Pneus` | Secundária | Contexto complementar | Q3 | Pode esclarecer padrões de categoria/idade/carga; não abrir cruzamentos antes dos fatores centrais. |
| `Seguros` | Fora da EDA inicial | Sem uso inicial | — | Não responde diretamente às perguntas atuais; preservar e reavaliar se uma pergunta específica surgir. |
| `Distrito` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Concelho` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Condutor Gr.Etario(<=5) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(6-9) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(10-14) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(15-17) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(18-20) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(21-24) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(25-29) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(30-34) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(35-39) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(40-44) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(45-49) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(50-54) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(55-59) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(65-69) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(70-74) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(>=75) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Condutor Gr.Etario(Não Def.) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `Id. Veículo` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `Reboque` | Secundária | Contexto complementar | Q3 | Pode esclarecer padrões de categoria/idade/carga; não abrir cruzamentos antes dos fatores centrais. |
| `Condutor Gr.Etario(60-64) SUM` | Secundária | Contexto complementar | Q3 | Possível composição dos condutores nos grupos de veículos. Grupos etários não são idades exatas; validar indicadores e cobertura antes de agregar. |
| `ficheiro_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `folha_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `linha_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |

### passageiros.csv

Inicial: 1; Suporte: 9; Fora da EDA inicial: 22; Secundária: 1.

| Variável | Prioridade | Papel | Perguntas | Justificação |
| --- | --- | --- | --- | --- |
| `ano` | Inicial | Contexto / técnica | Q0; Q1; Q2; Q3 | Comparação temporal e chave com Id. Acidente; necessário também para derivar idade do veículo. |
| `Id. Acidente` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `Datahora` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Entidades Fiscalizadoras` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Id. Passageiro` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `Lesões a 30 dias` | Secundária | Resultado complementar | Complementar | Caracterização da gravidade dos passageiros se necessária; não é uma contagem garantida de todos os ocupantes. |
| `Sexo` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Posição Veiculo` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Acessórios Passageiro` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Distrito` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Concelho` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Passageiro Gr.Etario(<=5) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(6-9) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(10-14) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(15-17) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(18-20) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(21-24) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(25-29) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(30-34) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(35-39) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(40-44) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(45-49) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(50-54) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(55-59) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(60-64) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(65-69) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(70-74) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(>=75) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Passageiro Gr.Etario(Não Def.) SUM` | Fora da EDA inicial | Sem uso inicial | Q3 condicional | Só reavaliar com pergunta explícita sobre ocupação. Não assumir que os registos de passageiros cobrem todos os ocupantes ou permitem calcular lotação. |
| `Id. Veículo` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `ficheiro_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `folha_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `linha_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |

### peoes.csv

Inicial: 1; Suporte: 11; Fora da EDA inicial: 20; Secundária: 4.

| Variável | Prioridade | Papel | Perguntas | Justificação |
| --- | --- | --- | --- | --- |
| `ano` | Inicial | Contexto / técnica | Q0; Q1; Q2; Q3 | Comparação temporal e chave com Id. Acidente; necessário também para derivar idade do veículo. |
| `Id. Acidente` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `Freguesia` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Tipo Natureza` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Natureza` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Datahora` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Entidades Fiscalizadoras` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Id. Peao` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `Sexo` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Acções Peão` | Secundária | Contexto complementar | Q1 | Subanálise de atropelamentos e luz, caso pertinente; Tipo Peão/Material Reflector existem apenas em 2023–2024. |
| `Distrito` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Concelho` | Suporte | Validação / redundância | Q0; Q1; Q2; Q3 | Conferir contra acidentes.csv; usar essa tabela como fonte principal do contexto do acidente. Não duplicar dimensões na análise. |
| `Lesões a 30 dias` | Secundária | Resultado complementar | Complementar | Gravidade dos peões para eventual caracterização específica. |
| `Peao Gr.Etario(<=5) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(6-9) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(10-14) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(15-17) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(18-20) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(21-24) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(25-29) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(30-34) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(35-39) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(40-44) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(45-49) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(50-54) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(55-59) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(60-64) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(65-69) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(70-74) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(>=75) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Peao Gr.Etario(Não Def.) SUM` | Fora da EDA inicial | Sem uso inicial | — | Sem ligação direta às perguntas atuais; reavaliar numa subanálise específica de peões. |
| `Tipo Peão` | Secundária | Contexto complementar | Q1 | Subanálise de atropelamentos e luz, caso pertinente; Tipo Peão/Material Reflector existem apenas em 2023–2024. |
| `Material Reflector` | Secundária | Contexto complementar | Q1 | Subanálise de atropelamentos e luz, caso pertinente; Tipo Peão/Material Reflector existem apenas em 2023–2024. |
| `ficheiro_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `folha_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
| `linha_origem` | Suporte | Técnica | Q0; Q1; Q2; Q3 | Ligar, validar unicidade ou rastrear registos. IDs de veículo e pessoa exigem validação por ano/acidente; não contam automaticamente pessoas únicas. |
