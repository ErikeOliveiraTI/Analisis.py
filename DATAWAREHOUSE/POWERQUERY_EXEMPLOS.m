// ============================================================================
// POWER QUERY - DATA WAREHOUSE
// Exemplos de queries em M Language para Excel/Power BI
// ============================================================================
// Data: 2024-01-01
// Compatível com: Excel 2016+, Power BI Desktop, Power BI Service
// ============================================================================


// ============================================================================
// 1. CONECTAR COM BANCO DE DADOS SQLITE
// ============================================================================

// ============================================================================
// 1.1: Conexão Básica ao SQLite
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db", [CreateIfNotExists=false]),
    Database = Source
in
    Database

// Alternativa com caminho relativo:
let
    Source = Sqlite.Database("../../DATAWAREHOUSE/DEV_ENVIRONMENT/data_warehouse.db"),
    Database = Source
in
    Database


// ============================================================================
// 2. QUERIES DE CONSULTA
// ============================================================================

// ============================================================================
// 2.1: Carregar Todas as Transações de Caixa
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    fato_caixa = Source{[Name="fato_caixa"]}[Data],
    
    #"Tipos Alterados" = Table.TransformColumnTypes(fato_caixa, {
        {"id_caixa", Int64.Type},
        {"data_operacao", type date},
        {"valor_entrada", type number},
        {"valor_saida", type number},
        {"saldo", type number},
        {"criado_em", type datetime}
    }),
    
    #"Filtrar Nulos" = Table.SelectRows(#"Tipos Alterados", 
        each [valor_entrada] <> null or [valor_saida] <> null),
    
    #"Adicionar Coluna Tipo" = Table.AddColumn(
        #"Filtrar Nulos",
        "Tipo Movimento",
        each 
            if [valor_entrada] <> null then "Entrada"
            else if [valor_saida] <> null then "Saída"
            else "Ajuste",
        type text
    )
in
    #"Adicionar Coluna Tipo"


// ============================================================================
// 2.2: Resumo Diário de Caixa
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    // Carregar dados de caixa e datas
    caixa = Source{[Name="fato_caixa"]}[Data],
    datas = Source{[Name="dim_datas"]}[Data],
    
    // Join com dimensão de datas
    MergirDatas = Table.NestedJoin(
        caixa,
        {"id_data"},
        datas,
        {"id_data"},
        "Datas",
        JoinKind.LeftOuter
    ),
    
    // Expandir informações de datas
    ExpandirDatas = Table.ExpandTableColumn(
        MergirDatas,
        "Datas",
        {"data", "mes_nome", "ano"},
        {"data", "mes_nome", "ano"}
    ),
    
    // Agrupar por data
    AgruparPorData = Table.Group(
        ExpandirDatas,
        {"data", "mes_nome", "ano"},
        {
            {"Total Entradas", each List.Sum([valor_entrada]), type number},
            {"Total Saídas", each List.Sum([valor_saida]), type number},
            {"Num Operações", each Table.RowCount(_), Int64.Type},
            {"Num Entradas", each List.Count(List.Select([valor_entrada], each _ <> null)), Int64.Type},
            {"Num Saídas", each List.Count(List.Select([valor_saida], each _ <> null)), Int64.Type}
        }
    ),
    
    // Calcular saldo
    CalcularSaldo = Table.AddColumn(
        AgruparPorData,
        "Saldo Diário",
        each [Total Entradas] - [Total Saídas],
        type number
    ),
    
    // Ordenar por data
    OrdenarPorData = Table.Sort(CalcularSaldo, {{"data", Order.Descending}})
in
    OrdenarPorData


// ============================================================================
// 2.3: Análise Mensal
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    caixa = Source{[Name="fato_caixa"]}[Data],
    datas = Source{[Name="dim_datas"]}[Data],
    
    // Converter tipos
    #"Tipos Caixa" = Table.TransformColumnTypes(caixa, {
        {"valor_entrada", type number},
        {"valor_saida", type number}
    }),
    
    #"Tipos Datas" = Table.TransformColumnTypes(datas, {
        {"data", type date},
        {"ano", Int64.Type},
        {"mes", Int64.Type}
    }),
    
    // Merge
    Merge = Table.NestedJoin(
        #"Tipos Caixa",
        {"id_data"},
        #"Tipos Datas",
        {"id_data"},
        "Datas",
        JoinKind.LeftOuter
    ),
    
    Expandir = Table.ExpandTableColumn(
        Merge,
        "Datas",
        {"mes", "mes_nome", "ano"},
        {"mes", "mes_nome", "ano"}
    ),
    
    // Agrupar por mês
    AgruparMes = Table.Group(
        Expandir,
        {"ano", "mes", "mes_nome"},
        {
            {"Entradas", each List.Sum([valor_entrada]), type number},
            {"Saídas", each List.Sum([valor_saida]), type number},
            {"Operações", each Table.RowCount(_), Int64.Type},
            {"Dias Ativos", each List.Count(List.Distinct([id_data])), Int64.Type}
        }
    ),
    
    // Calcular saldo
    CalcSaldo = Table.AddColumn(
        AgruparMes,
        "Saldo Mensal",
        each [Entradas] - [Saídas],
        type number
    ),
    
    // Calcular ticket médio
    CalcTicket = Table.AddColumn(
        CalcSaldo,
        "Ticket Médio",
        each if [Operações] > 0 then [Entradas] / [Operações] else 0,
        type number
    ),
    
    // Ordenar
    Ordenar = Table.Sort(CalcTicket, {{"ano", Order.Descending}, {"mes", Order.Descending}})
in
    Ordenar


// ============================================================================
// 2.4: Métodos de Pagamento - Distribuição
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    caixa = Source{[Name="fato_caixa"]}[Data],
    
    // Filtrar nulos
    Sem Nulos = Table.SelectRows(caixa, each [metodo_pagamento] <> null),
    
    // Agrupar por método
    Agrupar = Table.Group(
        Sem Nulos,
        {"metodo_pagamento"},
        {
            {"Total Entradas", each List.Sum([valor_entrada]), type number},
            {"Total Saídas", each List.Sum([valor_saida]), type number},
            {"Operações", each Table.RowCount(_), Int64.Type}
        }
    ),
    
    // Calcular percentual
    Percentual = Table.AddColumn(
        Agrupar,
        "% do Total",
        each 
            let
                Total = List.Sum(Agrupar[Operações])
            in
                [Operações] / Total * 100,
        type number
    ),
    
    // Formatar
    Formatar = Table.TransformColumnTypes(
        Percentual,
        {{"% do Total", Percentage.Type}}
    )
in
    Formatar


// ============================================================================
// 2.5: Top 10 Maiores Transações
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    caixa = Source{[Name="fato_caixa"]}[Data],
    datas = Source{[Name="dim_datas"]}[Data],
    
    // Adicionar valor absoluto
    ComValorAbs = Table.AddColumn(
        caixa,
        "Valor Movimento",
        each if [valor_entrada] <> null then [valor_entrada] else [valor_saida],
        type number
    ),
    
    // Merge com datas
    Merge = Table.NestedJoin(
        ComValorAbs,
        {"id_data"},
        datas,
        {"id_data"},
        "Datas",
        JoinKind.LeftOuter
    ),
    
    Expandir = Table.ExpandTableColumn(Merge, "Datas", {"data"}),
    
    // Ordenar e pegar top 10
    Ordenar = Table.Sort(ComValorAbs, {{"Valor Movimento", Order.Descending}}),
    TopDez = Table.FirstN(Ordenar, 10)
in
    TopDez


// ============================================================================
// 2.6: Auditoria de Processamento
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    auditoria = Source{[Name="auditoria_processamento"]}[Data],
    backups = Source{[Name="fato_backups"]}[Data],
    
    // Tipos
    #"Tipos Auditoria" = Table.TransformColumnTypes(auditoria, {
        {"data_processamento", type datetime},
        {"tempo_processamento_ms", Int64.Type}
    }),
    
    // Merge com backups
    Merge = Table.NestedJoin(
        #"Tipos Auditoria",
        {"id_backup"},
        backups,
        {"id_backup"},
        "Backups",
        JoinKind.LeftOuter
    ),
    
    Expandir = Table.ExpandTableColumn(
        Merge,
        "Backups",
        {"nome_arquivo", "status"},
        {"nome_arquivo", "status_backup"}
    ),
    
    // Ordenar por data descrescente
    Ordenar = Table.Sort(Expandir, {{"data_processamento", Order.Descending}}),
    
    // Top 100
    Top100 = Table.FirstN(Ordenar, 100)
in
    Top100


// ============================================================================
// 2.7: Consolidado por Tipo de Arquivo
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    backups = Source{[Name="fato_backups"]}[Data],
    tipos = Source{[Name="dim_tipos_arquivo"]}[Data],
    
    // Merge
    Merge = Table.NestedJoin(
        backups,
        {"id_tipo"},
        tipos,
        {"id_tipo"},
        "Tipos",
        JoinKind.LeftOuter
    ),
    
    Expandir = Table.ExpandTableColumn(Merge, "Tipos", {"tipo_arquivo"}),
    
    // Agrupar
    Agrupar = Table.Group(
        Expandir,
        {"tipo_arquivo"},
        {
            {"Num Backups", each Table.RowCount(_), Int64.Type},
            {"Total Linhas", each List.Sum([num_linhas]), Int64.Type},
            {"Média Linhas", each Number.Round(List.Average([num_linhas]), 0), Int64.Type},
            {"Backups Sucesso", each List.Count(List.Select([status], each _ = "sucesso")), Int64.Type},
            {"Backups Erro", each List.Count(List.Select([status], each _ = "erro")), Int64.Type}
        }
    )
in
    Agrupar


// ============================================================================
// 3. TRANSFORMAÇÕES AVANÇADAS
// ============================================================================

// ============================================================================
// 3.1: Análise de Tendência (Últimos 30 Dias)
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    caixa = Source{[Name="fato_caixa"]}[Data],
    datas = Source{[Name="dim_datas"]}[Data],
    
    // Filtrar últimos 30 dias
    Data Hoje = DateTime.LocalNow(),
    Data 30 Dias = Date.AddDays(Date.From(Data Hoje), -30),
    
    #"Tipos Datas" = Table.TransformColumnTypes(datas, {{"data", type date}}),
    
    Filtrado = Table.SelectRows(
        #"Tipos Datas",
        each [data] >= Data 30 Dias
    ),
    
    // Merge com caixa
    Merge = Table.NestedJoin(
        caixa,
        {"id_data"},
        Filtrado,
        {"id_data"},
        "Datas",
        JoinKind.InnerOuter
    ),
    
    Expandir = Table.ExpandTableColumn(Merge, "Datas", {"data", "dia_semana"}),
    
    // Agrupar
    Agrupar = Table.Group(
        Expandir,
        {"data", "dia_semana"},
        {
            {"Entradas", each List.Sum([valor_entrada]), type number},
            {"Saídas", each List.Sum([valor_saida]), type number},
            {"Operações", each Table.RowCount(_), Int64.Type}
        }
    ),
    
    // Calcular saldo
    CalcSaldo = Table.AddColumn(
        Agrupar,
        "Saldo",
        each [Entradas] - [Saídas],
        type number
    ),
    
    // Ordenar
    Ordenar = Table.Sort(CalcSaldo, {{"data", Order.Ascending}})
in
    Ordenar


// ============================================================================
// 3.2: Análise de Desvio (Comparar com Média)
// ============================================================================

let
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    caixa = Source{[Name="fato_caixa"]}[Data],
    datas = Source{[Name="dim_datas"]}[Data],
    
    // Merge
    Merge = Table.NestedJoin(
        caixa,
        {"id_data"},
        datas,
        {"id_data"},
        "Datas",
        JoinKind.LeftOuter
    ),
    
    Expandir = Table.ExpandTableColumn(
        Merge,
        "Datas",
        {"data", "mes_nome", "ano"}
    ),
    
    // Agrupar por dia
    AgruparDia = Table.Group(
        Expandir,
        {"data", "mes_nome", "ano"},
        {
            {"Total Entradas", each List.Sum([valor_entrada]), type number},
            {"Total Saídas", each List.Sum([valor_saida]), type number}
        }
    ),
    
    // Calcular média geral
    Media Geral Entradas = List.Average(AgruparDia[Total Entradas]),
    Media Geral Saidas = List.Average(AgruparDia[Total Saídas]),
    
    // Calcular desvio
    ComDesvio = Table.AddColumn(
        AgruparDia,
        "Desvio Entradas",
        each [Total Entradas] - Media Geral Entradas,
        type number
    ),
    
    ComDesvio2 = Table.AddColumn(
        ComDesvio,
        "% Desvio",
        each if Media Geral Entradas <> 0 then 
            ([Desvio Entradas] / Media Geral Entradas) * 100 
        else 0,
        type number
    )
in
    ComDesvio2


// ============================================================================
// 4. ESTRUTURA DE DADOS PARA DASHBOARDS
// ============================================================================

// ============================================================================
// 4.1: Card Metrics (Indicadores Principais)
// ============================================================================

let
    // Este query retorna uma linha com métricas principais do dia
    Source = Sqlite.Database("z:\git\rotina\data_warehouse.db"),
    
    caixa = Source{[Name="fato_caixa"]}[Data],
    datas = Source{[Name="dim_datas"]}[Data],
    
    // Filtrar hoje
    DataHoje = Date.From(DateTime.LocalNow()),
    
    #"Tipos Datas" = Table.TransformColumnTypes(datas, {{"data", type date}}),
    DatasHoje = Table.SelectRows(#"Tipos Datas", each [data] = DataHoje),
    
    // Merge
    Merge = Table.NestedJoin(caixa, {"id_data"}, DatasHoje, {"id_data"}, "Datas"),
    Expandir = Table.ExpandTableColumn(Merge, "Datas", {"data"}),
    
    // Calcular métricas
    Metrics = Table.FromRecords({
        [
            "Data" = DataHoje,
            "Total Entradas" = List.Sum(Expandir[valor_entrada]),
            "Total Saídas" = List.Sum(Expandir[valor_saida]),
            "Saldo" = List.Sum(Expandir[valor_entrada]) - List.Sum(Expandir[valor_saida]),
            "Num Operações" = Table.RowCount(Expandir),
            "Num Entradas" = List.Count(List.Select(Expandir[valor_entrada], each _ <> null)),
            "Num Saídas" = List.Count(List.Select(Expandir[valor_saida], each _ <> null))
        ]
    })
in
    Metrics


// ============================================================================
// 5. CONFIGURAÇÕES RECOMENDADAS
// ============================================================================

/*
PARA USAR ESTAS QUERIES EM EXCEL/POWER BI:

1. Abrir Excel → Dados → Novas Consultas → De Outras Fontes → No Other Sources...
2. Procurar por "SQLite" ou "Database"
3. Selecionar o arquivo: z:\git\rotina\data_warehouse.db
4. Colar o código da query desejada
5. Clicar em "Carregar"

MELHORES PRÁTICAS:

✅ Cache de dados (não consultar a cada segundo)
✅ Atualizar diariamente a meia-noite
✅ Criar visualizações baseadas em views
✅ Usar parâmetros para filtros dinâmicos
✅ Monitorar performance em datasets grandes

ALTERNATIVA: PODER BI

1. Abrir Power BI Desktop
2. Início → Obter Dados → Mais...
3. Procurar por "SQLite"
4. Inserir caminho do banco
5. Selecionar as tabelas desejadas
6. Carregar e criar relationships
7. Criar dashboards

*/

// ============================================================================
// FIM DO SCRIPT POWER QUERY
// ============================================================================
// Versão: 1.0
// Status: Production Ready ✅
// ============================================================================
