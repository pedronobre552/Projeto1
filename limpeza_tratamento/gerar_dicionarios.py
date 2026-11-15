"""Gerar um dicionário Markdown por CSV, com definições BEAV e cobertura anual.

As definições abaixo são paráfrases das referências locais. Campos específicos
da exportação, correspondências incertas e variáveis do projeto são assinalados.
Não se copiam valores individuais dos dados para a documentação versionada.
"""

import argparse
import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANUAL = "../referencias/MANUAL%20PREENCHIMENTO%20BEAV.pdf"


def definition(description, kind, source, note=""):
    """Manter o mesmo formato para todas as definições e notas de interpretação."""
    return (description, kind, source, note)


# M = Manual de Preenchimento; B = formulário BEAV. Páginas do PDF fornecido.
# Estes nomes são os da exportação, que não é integralmente especificada no manual.
FIELDS = {
    "ano": definition("Ano associado ao ficheiro anual de origem.", "inteiro", "Projeto", "Criado pelo script; não confundir com a coluna original Ano."),
    "Id. Acidente": definition("Identificador do acidente na exportação.", "texto / identificador", "Exportação; M p.9", "Usar com ano. Não assumir que é o número do boletim impresso nem interpretar a estrutura dos dígitos."),
    "Datahora": definition("Data e hora da ocorrência do acidente.", "data/hora a interpretar", "M A1 p.13", "O CSV conserva a representação original; validar a conversão, por exemplo AAAA:MM:DD HH:MM:SS."),
    "Ano": definition("Ano original incluído na exportação.", "inteiro esperado", "Exportação; M A1 p.13", "Redundante com ano apenas após validação; preservado nesta fase."),
    "Dia": definition("Dia do mês em que ocorreu o acidente.", "inteiro 1–31 esperado", "M A1 p.13", "Há exportações antigas com representações de data de 1900; preferir derivar de Datahora na preparação futura."),
    "Mês": definition("Mês da ocorrência.", "mês a interpretar", "M A1 p.13", "Pode ser número, abreviatura ou representação de data; não converter automaticamente."),
    "Hora": definition("Hora/minuto da ocorrência.", "hora a interpretar", "M A1 p.13", "Pode conter uma data de referência; não usar essa data como ano do acidente."),
    "Dia da Semana": definition("Dia da semana da ocorrência.", "categoria", "Exportação; M A1 p.13", "Pode ser recalculado de Datahora; preservar rótulos originais nesta fase."),
    "Entidades Fiscalizadoras": definition("Entidade que regista o acidente, designadamente GNR ou PSP.", "categoria", "M p.5 e p.9; B p.1", "Siglas e designações por extenso podem coexistir."),
    "Distrito": definition("Distrito onde ocorreu o acidente.", "categoria geográfica", "M A2 pp.14–16"),
    "Concelho": definition("Concelho onde ocorreu o acidente.", "categoria geográfica", "M A2 pp.14–16", "Identificar em conjunto com o distrito."),
    "Freguesia": definition("Freguesia onde ocorreu o acidente.", "categoria geográfica", "M A2 pp.14–16", "Nomes e limites administrativos podem variar ao longo dos anos."),
    "Pov. Proxima": definition("Povoação do local ou a mais próxima.", "texto", "M A2 pp.14–16", "A regra de preenchimento distingue acidentes fora das localidades."),
    "Latitude GPS": definition("Latitude do local do acidente.", "decimal em graus esperado", "M A2 p.14", "O manual pede graus decimais. Validar vírgula decimal e valores; o sistema geodésico não é confirmado aqui."),
    "Longitude GPS": definition("Longitude do local do acidente.", "decimal em graus esperado", "M A2 p.14", "Validar vírgula decimal e sinal; não corrigir o sinal só pela localização esperada."),
    "Localizações": definition("Ocorrência dentro ou fora das localidades.", "categoria", "M A2 pp.14–16; B p.1", "Categoria urbana, não uma coordenada GPS."),
    "Nome arruamento": definition("Designação do arruamento onde ocorreu o acidente.", "texto", "M A2 pp.14–16", "A correspondência do cabeçalho com o conteúdo deve ser confirmada por ano antes de usar geograficamente."),
    "Tipos Vias": definition("Tipo de via da localização do acidente.", "categoria", "M A2 pp.14–16", "Não confundir com as características técnicas nem presumir códigos idênticos em todos os anos."),
    "Cod Via": definition("Designação/código identificador da via na exportação.", "texto / identificador", "Exportação; M A2 pp.14–16", "Não tratar como medida numérica. A composição exata do código é específica da exportação."),
    "Nome Outra Via": definition("Nome de outra via associado à localização, segundo o cabeçalho da exportação.", "texto", "Exportação; M A2 p.15", "Correspondência a confirmar: o manual admite a segunda via numa interseção, mas não define este nome de coluna."),
    "Km": definition("Ponto quilométrico da via onde ocorreu o acidente.", "decimal em km esperado", "M A2 pp.15–16", "Não é distância percorrida; pode não se aplicar a arruamentos."),
    "Sentidos": definition("Sentido crescente/decrescente da quilometragem ou numeração, quando há separador central.", "categoria", "M A2 p.16; B p.1", "Não confundir com sentido único/dois sentidos de Reg Circulação1."),
    "Velocidade local": definition("Limite de velocidade permitido no local do acidente.", "numérico; km/h", "M B3 p.24", "Não é a velocidade do veículo no momento do acidente."),
    "Velocidade geral": definition("Limite geral de velocidade da via.", "numérico; km/h", "M B3 p.24", "Não é a velocidade observada de circulação."),
    "Características Tecnicas1": definition("Característica técnica da via: estrada com/sem separador e categoria associada.", "categoria", "M B1 pp.21–22; B p.1", "Este campo não corresponde ao número de vias de trânsito."),
    "Via Trânsito": definition("Via de trânsito em que ocorreu o acidente: esquerda, direita ou central.", "categoria", "M B1 pp.21–22; B p.1"),
    "Traçado 1": definition("Traçado em planta da via: reta ou curva.", "categoria", "M B2 pp.22–23; B p.1", "Base para um futuro indicador de curva; ainda não derivado."),
    "Traçado 2": definition("Perfil longitudinal: patamar, inclinação ou lomba.", "categoria", "M B2 pp.22–23; B p.1"),
    "Traçado 3": definition("Condição da berma: ausente/impraticável, não pavimentada ou pavimentada.", "categoria", "M B2 pp.22–23; B p.1"),
    "Traçado 4": definition("Situação do acidente na via: plena via, berma, passeio, pista reservada ou estacionamento.", "categoria", "M B2 pp.22–23; B p.1", "Não significa curva nem o sentido da curva."),
    "Intersecção Vias": definition("Tipo de interseção ou ocorrência fora de interseção.", "categoria", "M B2 p.23; B p.1", "O manual considera a proximidade inferior a 20 m para esta classificação."),
    "Obras Arte": definition("Ocorrência em túnel, viaduto/ponte ou passagem estreita.", "categoria", "M B2 p.23; B p.1", "Obras de arte são estruturas da via; não significam trabalhos de construção."),
    "Reg Circulação1": definition("Regime da faixa de rodagem: sentido único, dois sentidos ou reversível.", "categoria", "M B3 p.24; B p.1"),
    "Tipo Piso": definition("Material do piso: terra, betuminoso, betão ou calçada.", "categoria", "M B4 p.25; B p.1"),
    "Estado Conservação": definition("Estado de conservação do pavimento.", "categoria", "M B4 p.25; B p.1"),
    "Cond Aderência": definition("Estado de aderência do piso no momento do acidente.", "categoria", "M B4 p.25; B p.1", "Inclui seco/limpo, húmido, molhado, água, gelo/neve, lama, gravilha/areia e óleo."),
    "Obstáculos": definition("Existência e sinalização de obstáculos ou obras na faixa de rodagem.", "categoria", "M B4 p.25; B p.1", "Não inclui os equipamentos fixos da estrada; não equivale à natureza do acidente."),
    "Marca Via": definition("Existência/tipo de marcas rodoviárias no pavimento.", "categoria", "M B5 p.26; B p.1"),
    "Sinais": definition("Sinalização vertical existente no local.", "categoria", "M B5 p.26; B p.1", "O formulário distingue stop, cedência, proibição de ultrapassar, passagem de peões e outros."),
    "Sinais Luminosos": definition("Existência e funcionamento da sinalização luminosa.", "categoria", "M B5 p.26; B p.1"),
    "Luminosidade": definition("Condição de luz natural/artificial no momento do acidente.", "categoria", "M B6 pp.26–27; B p.1", "Não é uma classificação obtida apenas da hora do dia."),
    "Factores Atmosféricos": definition("Fator atmosférico registado como mais relevante para o acidente.", "categoria", "M B7 p.27; B p.1", "Não representa necessariamente todas as condições meteorológicas simultâneas."),
    "Natureza": definition("Descrição detalhada da natureza do acidente: modalidade de despiste, colisão ou atropelamento.", "categoria", "M C pp.28–29; B p.1", "O formulário classifica a situação que inicia o acidente; não concluir ausência de peões apenas a partir desta coluna."),
    "Tipo Natureza": definition("Natureza ampla do acidente: despiste, colisão ou atropelamento.", "categoria", "M A4 pp.17–18; B p.1", "Não confundir com a descrição detalhada de Natureza."),
    "Desc. Esquema": definition("Descrição do esquema ilustrativo usado para caracterizar o acidente.", "categoria / texto", "Exportação; M E3 pp.39–42", "Correspondência ao esquema BEAV inferida do nome; validar a codificação exata da exportação."),
    "Sexo": definition("Sexo registado da pessoa representada na linha.", "categoria", "M A6 p.20; F2 p.45; F3 p.47", "O formulário apresenta masculino/feminino. Marcadores de desconhecido na exportação não devem ser imputados."),
    "Lesões a 30 dias": definition("Classificação das lesões da pessoa na exportação com seguimento a 30 dias.", "categoria", "M conceitos pp.6–7; F pp.44–48", "Distinguir morto, ferido grave, ferido ligeiro/leve e ileso quando presente. Não confundir com a avaliação inicial de 24 h."),
    "Licença Condução": definition("Situação/adequação da habilitação ao veículo conduzido.", "categoria", "M E1 pp.35–37"),
    "Teste Alcool": definition("Situação de realização do teste de alcoolemia e/ou motivo de não realização.", "categoria", "M E2 pp.37–38", "Não contém a taxa de álcool nem prova resultado positivo. Rótulos posteriores da exportação podem alargar o formulário fornecido."),
    "Nomeoutrosfactores": definition("Outros fatores psicofísicos/comportamentais registados para o condutor.", "categoria / texto", "M E2 pp.37–38", "O formulário permite múltiplos fatores. Um rastreio de drogas não prova resultado positivo."),
    "Tempo Condução Continuada": definition("Intervalo de tempo de condução sem parar antes do acidente.", "categoria ordinal", "M E2 p.38; B p.2", "Ignorada é falta de informação, não zero horas."),
    "Acções Condutores": definition("Ação/manobra do condutor imediatamente antes do acidente.", "categoria", "M E3 pp.39–42; B p.2"),
    "Inf. Comp. a Acções e Manobras": definition("Informação complementar à ação/manobra do condutor.", "categoria", "M E4 p.42; B p.2", "Pode incluir infrações, falhas mecânicas e outros eventos; não equivale automaticamente à responsabilidade pelo acidente."),
    "Acessórios Condutores": definition("Uso ou isenção de equipamento de segurança do condutor.", "categoria", "M E5 p.43; B p.2"),
    "Categoria Veículos": definition("Categoria/classe do veículo associado ao condutor.", "categoria", "M D1 pp.30–31; B p.1"),
    "Tipo Veiculo": definition("Utilização/tipo do automóvel: passageiros, mercadorias, misto, trator ou especial.", "categoria", "M D1 pp.30–31; B p.1", "Aplica-se a automóveis ligeiros/pesados; vazio pode significar não aplicável."),
    "Veiculo Especial": definition("Designação do veículo especial, quando aplicável.", "categoria / texto", "M D1 p.31 e anexo II p.49; B p.1"),
    "Reboque": definition("Presença ou ausência de reboque/semirreboque.", "categoria", "M D1 p.31; B p.2"),
    "Tipo Serviço": definition("Serviço do veículo, particular ou público.", "categoria", "M D2 p.32; B p.2"),
    "Ano matricula": definition("Ano da primeira matrícula do veículo.", "inteiro / ano", "M D3 p.32", "Não é o ano da última matrícula/renovação; não pode exceder o ano do acidente segundo o manual."),
    "Inspecção Periódica": definition("Situação da inspeção periódica do veículo.", "categoria", "M D4 p.32; B p.2", "Regras descritas na edição fornecida do manual; não usar como parecer sobre legislação atual."),
    "Certificado Adr": definition("Situação de certificado ADR para transporte de matérias perigosas.", "categoria", "M D5 p.33 e E1 pp.36–37; B p.2", "Correspondência a confirmar: o manual distingue ADR do veículo e ADR do condutor; o cabeçalho isolado não os distingue."),
    "Carga Lotação": definition("Condição de carga, acondicionamento ou lotação do veículo.", "categoria", "M D6 pp.33–34; B p.2", "É uma classificação, não o peso da carga nem o número de ocupantes."),
    "Pneus": definition("Existência de deficiência nos pneus.", "categoria", "M D6 pp.33–34; B p.2"),
    "Seguros": definition("Situação do seguro do veículo: com seguro, sem seguro ou isento.", "categoria", "M D7 p.34; B p.2"),
    "Id. Veículo": definition("Identificador do veículo dentro da exportação do acidente.", "texto / identificador", "Exportação; M D p.30", "Usar com ano e Id. Acidente. A correspondência com letras do boletim não está documentada; falta nos anos antigos."),
    "Id. Passageiro": definition("Identificador do passageiro na exportação do acidente.", "texto / identificador", "Exportação; M F2 pp.44–45", "Não é identificador pessoal global. Validar a unicidade com ano, acidente e, quando aplicável, veículo."),
    "Posição Veiculo": definition("Posição do passageiro no veículo: frente, retaguarda ou desconhecida.", "categoria", "M F2 p.45; B p.2"),
    "Acessórios Passageiro": definition("Uso/ausência de capacete, cinto ou sistema de retenção de crianças.", "categoria", "M F2 p.45; B p.2", "Interpretação depende da idade e do veículo; não confundir ausência de dado com ausência de proteção."),
    "Id. Peao": definition("Identificador do peão na exportação do acidente.", "texto / identificador", "Exportação; M F3 p.47", "Chave candidata: ano, Id. Acidente e Id. Peao; validar antes de contar pessoas únicas."),
    "Tipo Peão": definition("Forma de deslocação/situação do peão no acidente.", "categoria", "M F3 p.47; B p.2", "Inclui peão isolado, em grupo ou com meios de deslocação descritos no formulário; não é a ação de atravessamento."),
    "Acções Peão": definition("Ação ou posição do peão no momento do acidente.", "categoria", "M F3 p.48; B p.2"),
    "Material Reflector": definition("Utilização de material retrorrefletor pelo peão.", "categoria", "M F3 p.48; B p.2", "Distinguir sim/não de desconhecido, não definido ou não aplicável."),
    "ficheiro_origem": definition("Nome do Excel de onde foi extraído o registo.", "texto / metadado", "Projeto", "Rastreabilidade; não é uma variável explicativa do acidente."),
    "folha_origem": definition("Nome original da folha Excel.", "texto / metadado", "Projeto", "Rastreabilidade; diferenças de nome não representam categorias do acidente."),
    "linha_origem": definition("Número da linha na folha original, começando em 1.", "inteiro / metadado", "Projeto", "Localiza o registo com ficheiro_origem e folha_origem; não usar como preditor."),
}

# Opções do formulário fornecido, não um catálogo validado dos rótulos de todos
# os Excel. As variantes de escrita e opções posteriores continuam preservadas.
DOMAINS = {
    "Sexo": "Masculino; feminino.",
    "Lesões a 30 dias": "Morto; ferido grave; ferido leve/ligeiro; ileso quando aplicável. Ver definição a 30 dias no guia.",
    "Entidades Fiscalizadoras": "GNR; PSP (designações podem vir por extenso).",
    "Localizações": "Dentro das localidades; fora das localidades.",
    "Sentidos": "Crescente; decrescente, quando aplicável.",
    "Via Trânsito": "Esquerda; direita; central.",
    "Traçado 1": "Reta; curva.",
    "Traçado 2": "Em patamar; com inclinação; em lomba.",
    "Traçado 3": "Sem berma ou impraticável; berma não pavimentada; berma pavimentada.",
    "Traçado 4": "Em plena via; na berma; no passeio; em via/pista reservada; em parque de estacionamento.",
    "Obras Arte": "Túnel; viaduto/ponte; passagem estreita; não aplicável.",
    "Reg Circulação1": "Sentido único; dois sentidos; reversível.",
    "Tipo Piso": "Terra batida; betuminoso; betão de cimento; calçada.",
    "Estado Conservação": "Bom; regular; mau estado.",
    "Cond Aderência": "Seco/limpo; húmido; molhado; água acumulada; gelo/geada/neve; lama; gravilha/areia; óleo.",
    "Obstáculos": "Inexistentes; não sinalizados; insuficientemente sinalizados; corretamente sinalizados.",
    "Marca Via": "Sem marcas/pouco visíveis; separadoras de sentidos; separadoras de sentidos e vias.",
    "Sinais": "Stop; cedência de passagem; proibição de ultrapassagem; passagem de peões; outros; inexistência quando não aplicável.",
    "Sinais Luminosos": "Inexistente; funcionamento normal; intermitente; desligada.",
    "Luminosidade": "Pleno dia; sol encandeante; aurora/crepúsculo; noite sem iluminação; noite com iluminação.",
    "Factores Atmosféricos": "Bom tempo; chuva; vento forte; nevoeiro; neve; nuvem de fumo; granizo.",
    "Tipo Natureza": "Despiste; colisão; atropelamento.",
    "Natureza": "Modalidades de despiste (códigos BEAV 1–7), colisão (8–14) e atropelamento (15–17); consultar capítulo C.",
    "Intersecção Vias": "Fora da interseção; cruzamento; entroncamento; rotunda; passagem de nível; aceleração; desaceleração; ramo de ligação entrada/saída.",
    "Características Tecnicas1": "Autoestrada/outra via com separador; estrada sem separador, segundo B1.",
    "Licença Condução": "Adequada; não adequada; instrução/exame; caducada/suspensa; sem licença/carta; não necessária.",
    "Teste Alcool": "Submetido ao teste; não submetido por doença, lesão/morte, não contactado, fuga, recusa ou outro motivo (edição BEAV).",
    "Tempo Condução Continuada": "Menos de 1 h; 1–3 h; 3–5 h; mais de 5 h; ignorada.",
    "Nomeoutrosfactores": "Normal; rastreio de drogas; sono/sonolência; distração; doença súbita; fadiga. O formulário admite seleção múltipla.",
    "Acessórios Condutores": "Capacete; cinto; sem uso de cinto/capacete; isento.",
    "Tipo Veiculo": "Passageiros; mercadorias; misto; trator; veículo especial; não aplicável.",
    "Categoria Veículos": "Categorias D1: velocípedes, ciclomotor/triciclo/motociclos, automóveis ligeiros/pesados, agrícola, máquina industrial, carris, tração animal, quadriciclo, desconhecido.",
    "Reboque": "Com ou sem reboque/semirreboque.",
    "Tipo Serviço": "Particular; público.",
    "Inspecção Periódica": "Não obrigatória; válida; sem validade.",
    "Certificado Adr": "Válido; sem validade; inexistente; não aplicável, distinguindo o campo do veículo/condutor.",
    "Carga Lotação": "Sem carga; excesso de carga; carga bem/mal acondicionada; lotação excedida; não aplicável.",
    "Pneus": "Sem deficiência; com deficiência; não aplicável.",
    "Seguros": "Com seguro; sem seguro; isento.",
    "Posição Veiculo": "À frente; à retaguarda; desconhecida.",
    "Acessórios Passageiro": "Com/sem capacete ou cinto; com/sem sistema de retenção de crianças.",
    "Tipo Peão": "Peão isolado; peões em grupo; conduzindo meios à mão; sobre patins/trotinetes ou outros, segundo F3.",
    "Material Reflector": "Sim; não, quando aplicável.",
}


def domain_for(column, kind):
    """Distinguir opções históricas do BEAV de validações de tipos do projeto."""
    if column in DOMAINS:
        return DOMAINS[column]
    if "Gr.Etario(" in column or column.startswith("Num"):
        return "Inteiro ≥ 0 quando conhecido; vazio não é zero."
    if "identificador" in kind:
        return "Código textual da exportação; não converter em medida numérica."
    if column in {"ano", "Ano", "Ano matricula"}:
        return "Ano de calendário; validar com o acidente/ficheiro."
    if column in {"Velocidade geral", "Velocidade local"}:
        return "Limite em km/h; o manual fornecido usa o intervalo 0–120."
    return "Ver significado, tipo e referência; não impor um catálogo sem validação."


def describe(column, table):
    """Expandir famílias de colunas sem inventar um significado para campos novos."""
    if column in FIELDS:
        return FIELDS[column]
    match = re.fullmatch(r"(Condutor|Passageiro|Peao) Gr\.Etario\((.+)\) SUM", column)
    if match:
        group = match[2]
        population = {"Condutor": "condutor", "Passageiro": "passageiro", "Peao": "peão"}[match[1]]
        interval = {"<=5": "até 5 anos", ">=75": "75 ou mais anos", "Não Def.": "idade não definida"}.get(group, f"{group} anos")
        source = {"Condutor": "M A6 pp.19–20", "Passageiro": "M F2 pp.44–46", "Peao": "M F3 pp.47–48"}[match[1]]
        return definition(f"Indicador/contagem do grupo etário do {population}: {interval}.", "inteiro não negativo esperado", f"Exportação; {source}", "Agrupamento criado na exportação, não campo literal do BEAV. SUM não é idade individual. Vazio por ausência da coluna no ano não equivale a zero; validar exclusividade dos grupos antes de reconstruir idades.")
    if column.startswith("Num. ") and column.endswith(" a 30 dias"):
        victim = column.removeprefix("Num. ").removesuffix(" a 30 dias").lower()
        return definition(f"Número de {victim} no acidente, segundo a classificação a 30 dias.", "inteiro não negativo; pessoas", "Exportação a 30 dias; M conceitos pp.6–7 e A3 p.17", "Contagem de pessoas, não de acidentes. A referência temporal é a da exportação a 30 dias.")
    vehicles = {
        "Num veículos envolvidos": "Total de veículos intervenientes no acidente.",
        "Num veículos ligeiros": "Número de automóveis ligeiros intervenientes.",
        "Num veículos pesados": "Número de automóveis pesados intervenientes.",
        "Num ciclomotores/motociclos": "Número de ciclomotores e motociclos intervenientes.",
        "Num outros veículos": "Número de veículos das restantes categorias intervenientes.",
    }
    if column in vehicles:
        return definition(vehicles[column], "inteiro não negativo; veículos", "M A5 pp.18–19; B p.1", "Campo disponível apenas em anos recentes; ausência histórica não é zero.")
    raise ValueError(f"Falta definição para {table}/{column}")


def source_link(text):
    """Ligar a fonte local mantendo também grupo e página por campo."""
    if "M " in text:
        return f"[{text}]({MANUAL})"
    return text


def generate(csv_dir, report_path, output_dir):
    """Garantir cobertura exata do cabeçalho e gerar documentação sem ler registos."""
    audit = json.loads(report_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    units = {
        "acidentes": "Uma linha representa um acidente. Chave candidata: `(ano, Id. Acidente)`; a auditoria mede a repetição do ID por ano.",
        "condutores_veiculos": "Uma linha representa um registo de condutor/veículo da exportação. Um acidente pode ter vários registos. Não existe ID de condutor explícito e Id. Veículo falta nos anos antigos.",
        "passageiros": "Uma linha representa um registo de passageiro. Um acidente pode envolver vários passageiros e veículos. Os identificadores são locais ao acidente, não pessoas acompanhadas ao longo do tempo.",
        "peoes": "Uma linha representa um registo de peão. Um acidente pode ter vários peões. Validar `(ano, Id. Acidente, Id. Peao)` antes de contar pessoas únicas.",
    }
    for table, info in audit["tabelas"].items():
        with (csv_dir / f"{table}.csv").open(encoding="utf-8-sig", newline="") as handle:
            header = next(csv.reader(handle))
        if header != info["colunas"]:
            raise ValueError(f"Cabeçalho diferente da auditoria: {table}")
        sources = [s for s in audit["fontes"] if s["tabela"] == table]
        lines = [f"# Dicionário — {table}.csv", "", units[table], "",
                 f"Cobertura: {len(header)} colunas, na mesma ordem do CSV. [Regras comuns e fontes](README.md).", "",
                 "As definições são paráfrases do manual. A associação dos nomes da exportação aos campos BEAV é interpretação do projeto; campos não especificados pelo manual e correspondências incertas são assinalados.", "",
                 "Os valores BEAV são opções da edição fornecida, não uma lista validada/exaustiva das categorias dos Excel de todos os anos. Não recodificar os dados nem impor códigos numéricos com base apenas nesta referência.", "",
                 "## Variáveis", "",
                 "| Coluna | Significado | Tipo de leitura / unidade | Valores BEAV / regra de leitura | Anos com a coluna na fonte | Referência | Observações |",
                 "| --- | --- | --- | --- | --- | --- | --- |"]
        for column in header:
            description, kind, source, note = describe(column, table)
            years = [str(s["ano"]) for s in sources if column not in s["colunas_ausentes"]]
            # A disponibilidade decorre do esquema, não da existência de valores não nulos.
            lines.append("| " + " | ".join([f"`{column}`", description, kind, domain_for(column, kind), ", ".join(years), source_link(source), note or "—"]) + " |")
        lines += ["", "## Utilização", "",
                  "Ler IDs como texto, ano como inteiro e os restantes tipos após validação. Um CSV não guarda tipos. As variáveis de proveniência servem para auditoria, não como preditores.", "",
                  "Uma coluna ausente num ano fica vazia no CSV unido; não preencher com zero. A existência da coluna também não garante preenchimento de todas as linhas. Consultar a auditoria local para nulos e tipos observados.", ""]
        (output_dir / f"{table}.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"{table}: {len(header)} colunas documentadas")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-dir", type=Path, default=ROOT / "data_agregada")
    parser.add_argument("--audit", type=Path, default=ROOT / "outputs" / "fase1" / "auditoria.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "dicionarios")
    args = parser.parse_args()
    generate(args.csv_dir, args.audit, args.output_dir)
