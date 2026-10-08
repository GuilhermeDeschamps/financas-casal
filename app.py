import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# ====================================================
# BANCO DE DADOS
# ====================================================

conn = sqlite3.connect("financas.db", check_same_thread=False)
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE movimentacoes
    ADD COLUMN cartao TEXT
    """)
    conn.commit()
except:
    pass

try:
    cursor.execute("""
    ALTER TABLE movimentacoes
    ADD COLUMN forma_pagamento TEXT
    """)
    conn.commit()
except:
    pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    tipo TEXT,
    pessoa TEXT,
    categoria TEXT,
    forma_pagamento TEXT,
    cartao TEXT,
    descricao TEXT,
    valor REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    segmento TEXT,
    valor_objetivo REAL,
    valor_atual REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cartoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    limite REAL,
    fechamento INTEGER,
    vencimento INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    senha TEXT
)
""")

conn.commit()

cursor.execute("""
INSERT OR IGNORE INTO usuarios
(usuario, senha)
VALUES ('Guilherme', '291060')
""")

cursor.execute("""
INSERT OR IGNORE INTO usuarios
(usuario, senha)
VALUES ('Isabelle', '302742')
""")

conn.commit()

# ====================================================
# CONFIGURAÇÃO
# ====================================================

st.set_page_config(
    page_title="Finanças do Casal",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>

.stButton > button{
    background:#111827;
    color:white;
    border:none;
    border-radius:16px;
    height:42px;

    transition:all .3s ease;
    font-weight:600;
}

.stButton > button:hover{
    transform:translateY(-3px);
    background:#00C853;
    box-shadow:0 10px 25px rgba(0,200,83,.35);
}

.stButton > button:focus{
    border:none !important;
    box-shadow:0 10px 25px rgba(0,200,83,.35);
}

</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>

[data-baseweb="segmented-control"]{
    background:linear-gradient(
        135deg,
        #111827,
        #1f2937
    ) !important;

    border-radius:18px !important;
    padding:6px !important;

    box-shadow:
        0 10px 25px rgba(0,0,0,.15);

    animation:fadeMenu .6s ease;
}

[data-baseweb="segmented-control"] button{
    transition:all .3s ease !important;
    border-radius:12px !important;
}

[data-baseweb="segmented-control"] button:hover{
    transform:translateY(-4px) scale(1.04);
}

[data-baseweb="segmented-control"] button[aria-selected="true"]{
    background:linear-gradient(
        135deg,
        #00c853,
        #00e676
    ) !important;

    color:white !important;

    box-shadow:
        0 8px 18px rgba(0,200,83,.35);

    transform:translateY(-2px);
}

@keyframes fadeMenu{
    from{
        opacity:0;
        transform:translateY(-20px);
    }

    to{
        opacity:1;
        transform:translateY(0);
    }
}

</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>

    .block-container{
        padding-top:1rem;
        padding-bottom:1rem;
    }

    </style>    
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """

    <style>

    /* Fundo */
    .stApp{
        background:linear-gradient(
            180deg,
            #f8fafc 0%,
            #eef2f7 100%
        );
    }

    /* Remove cabeçalho */
    header{
        visibility:hidden;
    }

    /* Remove rodapé */
    footer{
        visibility:hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>

    [data-testid="stMetric"]{
        background:white;
        padding:18px;
        border-radius:24px;
        box-shadow:0 4px 12px rgba(0,0,0,.08);
        margin-bottom:12px;
        border:none;

        transition:all 0.3s ease;
        animation:fadeUp 0.6s ease;
    }

    [data-testid="stMetric"]:hover{
        transform:translateY(-8px);
        box-shadow:0 15px 30px rgba(0,0,0,.15);
    }

    [data-testid="stMetricValue"]{
        color:#111827 !important;
        font-size:26px !important;
        font-weight:700 !important;
    }

    [data-testid="stMetricLabel"]{
        color:#6b7280 !important;
        font-size:14px !important;
        font-weight:500 !important;
    }

    @keyframes fadeUp{
        from{
            opacity:0;
            transform:translateY(20px);
        }
        to{
            opacity:1;
            transform:translateY(0);
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>

    div[role="radiogroup"] label {
        font-size:18px !important;
        font-weight:700 !important;
        color:#111827 !important;
        opacity:1 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>

    /* Apenas títulos do Streamlit */
    [data-testid="stHeading"] {
        color:#111827 !important;
    }

    /* Labels */
    label {
        color:#111827 !important;
    }

    /* Selectbox */
    [data-baseweb="select"] {
        color:#111827 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>

.stButton > button{
    background:#111827;
    color:white;
    border:none;
    border-radius:14px;
    height:42px;
    transition:.3s;
    font-weight:600;
}

.stButton > button:hover{
    transform:translateY(-3px);
    background:#00C853;
    box-shadow:0 8px 20px rgba(0,200,83,.25);
}

</style>
""",
    unsafe_allow_html=True,
)

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

menu = "🏠 Início"

if st.session_state.logado:

    if "menu" not in st.session_state:
        st.session_state.menu = "🏠 Início"
        
    menu_atual = st.session_state.menu    

    c1, c2, c3, c4, c5, c6 = st.columns([1.6, 1.8, 1.8, 1.4, 1.6, 0.6])

    with c1:
        if st.button(
            "🏠 Início" + (" ✅" if menu_atual == "🏠 Início" else ""),
            use_container_width=True
        ):
            st.session_state.menu = "🏠 Início"

    with c2:
        if st.button("➕ Movimentação", use_container_width=True):
            st.session_state.menu = "➕ Movimentação"

    with c3:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.menu = "📊 Dashboard"

    with c4:
        if st.button("🎯 Metas", use_container_width=True):
            st.session_state.menu = "🎯 Metas"

    with c5:
        if st.button("💳 Cartões", use_container_width=True):
            st.session_state.menu = "💳 Cartões"

    with c6:
        if st.button("🚪", use_container_width=True):
            st.session_state.logado = False
            st.rerun()

    menu = st.session_state.menu

if not st.session_state.logado:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            """
        <div style="
            background:white;
            padding:35px;
            border-radius:25px;
            box-shadow:0 8px 25px rgba(0,0,0,.08);
            text-align:center;
            margin-bottom:20px;
        ">

        <div style="
            font-size:60px;
            margin-bottom:15px;
        ">
            💰
        </div>

        <h1 style="
            color:#111827;
            margin:0;
            font-size:38px;
            font-weight:700;
        ">
            Finanças do Casal
        </h1>

        <p style="
            color:#6b7280;
            margin-top:10px;
            font-size:16px;
        ">
            Controle financeiro de Guilherme e Isabelle
        </p>

        </div>
        """,
            unsafe_allow_html=True,
        )

        usuario = st.text_input("", placeholder="👤 Usuário")

        senha = st.text_input("", type="password", placeholder="🔒 Senha")

        if st.button("🚀 Entrar"):

            consulta = pd.read_sql(
                """
                SELECT *
                FROM usuarios
                WHERE usuario = ?
                AND senha = ?
                """,
                conn,
                params=(usuario, senha),
            )

            if not consulta.empty:

                st.session_state.logado = True
                st.session_state.usuario = usuario

                st.success("✅ Login realizado com sucesso!")
                st.rerun()

            else:

                st.error("❌ Usuário ou senha inválidos")

    st.stop()

# ====================================================
# NOVA MOVIMENTAÇÃO
# ====================================================

if menu == "➕ Movimentação":

    st.header("➕ Nova Movimentação")

    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])

    pessoa = st.selectbox("Pessoa", ["Guilherme", "Isabelle", "Compartilhado"])

    categoria = st.selectbox(
        "Categoria",
        [
            "Salário",
            "Mercado",
            "Moradia",
            "Transporte",
            "Lazer",
            "Saúde",
            "Investimentos",
            "Outros",
        ],
    )

    forma_pagamento = st.selectbox(
        "Forma de Pagamento", ["PIX", "Dinheiro", "Débito", "Cartão de Crédito"]
    )

    cartao_utilizado = ""

    if forma_pagamento == "Cartão de Crédito":

        lista_cartoes = pd.read_sql("SELECT nome FROM cartoes", conn)

        if not lista_cartoes.empty:

            cartoes = lista_cartoes["nome"].tolist()

            cartao_utilizado = st.selectbox(
                "Cartão Utilizado", lista_cartoes["nome"].tolist()
            )

    descricao = st.text_input("Descrição")

    data = st.date_input("Data")

    valor = st.number_input("Valor", min_value=0.0, step=1.0)

    if st.button("Salvar Movimentação"):

        cursor.execute(
            """
        INSERT INTO movimentacoes
        (
            data,
            tipo,
            pessoa,
            categoria,
            forma_pagamento,
            cartao,
            descricao,
            valor
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                str(data),
                tipo,
                pessoa,
                categoria,
                forma_pagamento,
                cartao_utilizado,
                descricao,
                valor,
            ),
        )

        conn.commit()

        st.success("✅ Movimentação salva com sucesso!")

# ====================================================
# INÍCIO
# ====================================================

elif menu == "🏠 Início":

    df_inicio = pd.read_sql("SELECT * FROM movimentacoes", conn)

    receitas = float(df_inicio[df_inicio["tipo"] == "Receita"]["valor"].sum())

    despesas = float(df_inicio[df_inicio["tipo"] == "Despesa"]["valor"].sum())

    saldo = receitas - despesas

    hora = datetime.now().hour

    if hora < 12:
        saudacao = "☀️ Bom dia"
    elif hora < 18:
        saudacao = "🌤️ Boa tarde"
    else:
        saudacao = "🌙 Boa noite"

    st.markdown(
        f"""
    <div style="
    background:linear-gradient(135deg,#00C853,#00E676);
    padding:24px;
    border-radius:24px;
    color:white;
    box-shadow:0 15px 35px rgba(0,200,83,.25),0 0 40px rgba(0,200,83,.15);
    margin-bottom:20px;
    ">


    <p style="
    font-size:18px;
    margin-top:8px;
    margin-bottom:0;
    font-weight:600;
    ">
    {saudacao}, {st.session_state.usuario.title()}
    </p>

    <h1 style="
    font-size:46px;
    font-weight:800;
    margin-top:20px;
    margin-bottom:0;
    line-height:1;
    ">
    R$ {saldo:,.2f}
    </h1>

    <p style="
    opacity:.9;
    margin-top:8px;
    ">
    Saldo disponível
    </p>

    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📈 Receitas",
            f"R$ {receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )

    with col2:
        st.metric(
            "📉 Despesas",
            f"R$ {despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        )

    with col3:
        resultado_mes = receitas - despesas
        st.metric("💵 Resultado", f"R$ {resultado_mes:,.2f}")

    if receitas > 0:

        percentual_gasto = despesas / receitas

        st.markdown(
            "<h3 style='color:#111827;'>💳 Uso da renda</h3>",
            unsafe_allow_html=True,
        )

        st.progress(min(percentual_gasto, 1.0))

        st.markdown(
            f"""
            <div style="
                color:#6b7280;
                font-size:14px;
                margin-top:5px;
            ">
                {percentual_gasto:.0%} da renda já foi utilizada
            </div>
            """,
            unsafe_allow_html=True,
        )

    resultado_mes = receitas - despesas

    if resultado_mes > 0:

        st.success(f"📈 Sobrou R$ {resultado_mes:,.2f} este mês")

    elif resultado_mes < 0:

        st.error(f"📉 Você gastou R$ {abs(resultado_mes):,.2f} acima das receitas")

    else:

        st.info("💰 Receitas e despesas estão equilibradas")

    st.markdown("<h3 style='color:#111827;'>📢 Insights</h3>", unsafe_allow_html=True)

    if despesas > receitas:
        st.warning("⚠️ Você está gastando mais do que recebe.")
    else:
        st.success("✅ Suas finanças estão positivas.")

    categoria_top = (
        df_inicio[df_inicio["tipo"] == "Despesa"].groupby("categoria")["valor"].sum()
    )

    if not categoria_top.empty:

        maior_categoria = categoria_top.idxmax()

        st.info(f"💸 Maior gasto: {maior_categoria}")

    st.markdown(
        "<h3 style='color:#111827;'>💸 Últimas Atividades</h3>",
        unsafe_allow_html=True,
    )

    ultimas = df_inicio.sort_values("data", ascending=False).head(5)

    for _, item in ultimas.iterrows():

        if item["tipo"] == "Despesa":
            emoji = "🔴"
            valor_cor = "#dc2626"
            sinal = "-"
        else:
            emoji = "🟢"
            valor_cor = "#16a34a"
            sinal = "+"

        col1, col2 = st.columns([4, 2])

        icone_categoria = {
            "Mercado": "🛒",
            "Moradia": "🏠",
            "Transporte": "🚗",
            "Lazer": "🎮",
            "Saúde": "❤️",
            "Salário": "💰",
            "Investimentos": "📈",
            "Outros": "📋",
        }

        icone = icone_categoria.get(item["categoria"], "📋")

        cores_categoria = {
            "Mercado": "#DBEAFE",
            "Moradia": "#DCFCE7",
            "Transporte": "#FEF3C7",
            "Lazer": "#F3E8FF",
            "Saúde": "#FEE2E2",
            "Salário": "#DCFCE7",
            "Investimentos": "#D1FAE5",
            "Outros": "#E5E7EB",
        }

        icone = icone_categoria.get(item["categoria"], "📋")
        cor_fundo = cores_categoria.get(item["categoria"], "#E5E7EB")

        with col1:

            ico_col, txt_col = st.columns([1, 6])

            with ico_col:
                st.markdown(
                    f"""
                    <div style="
                        width:38px;
                        height:38px;
                        border-radius:50%;
                        background:{cor_fundo};
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:18px;
                    ">
                        {icone}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with txt_col:
                st.markdown(
                    f"""
                    <div style="font-weight:600;color:black;">
                        {item['descricao'].title()}
                    </div>
                    <div style="font-size:13px;color:#6b7280;">
                        {item['categoria']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col2:

            valor_formatado = f"{item['valor']:,.2f}"
            data_formatada = pd.to_datetime(item["data"]).strftime("%d/%m/%Y")

            st.markdown(
                f"""
                <div style="
                    text-align:right;
                    font-weight:700;
                    color:{valor_cor};
                    font-size:16px;
                ">
                    {sinal} R$ {valor_formatado}
                </div>

                <div style="
                    text-align:right;
                    color:#6b7280;
                    font-size:12px;
                ">
                    {data_formatada}
                </div>
                """,
                unsafe_allow_html=True,
            )

# ====================================================
# DASHBOARD
# ====================================================

elif menu == "📊 Dashboard":

    st.markdown(
        """
        <h1 style="color:#111827;">
            📊 Dashboard
        </h1>
        """,
        unsafe_allow_html=True,
    )

    df = pd.read_sql("SELECT * FROM movimentacoes", conn)

    pessoa_filtro = st.selectbox(
        "👤 Pessoa", ["Todos", "Guilherme", "Isabelle", "Compartilhado"]
    )

    if pessoa_filtro != "Todos":
        df = df[df["pessoa"] == pessoa_filtro]

    saldo_total = 0
    saldo = 0
    receitas = 0
    despesas = 0

    if df.empty:

        st.info("Nenhuma movimentação cadastrada.")

    else:

        df["data"] = pd.to_datetime(df["data"])

        meses = sorted(df["data"].dt.strftime("%m/%Y").unique(), reverse=True)

        mes_selecionado = st.selectbox("📅 Selecione o Mês", meses)

        df = df[df["data"].dt.strftime("%m/%Y") == mes_selecionado]

        receitas = df[df["tipo"] == "Receita"]["valor"].sum()

        despesas = df[df["tipo"] == "Despesa"]["valor"].sum()

        saldo = receitas - despesas

        receitas_total = pd.read_sql(
            """
            SELECT SUM(valor) total
            FROM movimentacoes
            WHERE tipo='Receita'
            """,
            conn,
        )["total"].iloc[0]

        despesas_total = pd.read_sql(
            """
            SELECT SUM(valor) total
            FROM movimentacoes
            WHERE tipo='Despesa'
            """,
            conn,
        )["total"].iloc[0]

        if pd.isna(receitas_total):
            receitas_total = 0

        if pd.isna(despesas_total):
            despesas_total = 0

        saldo_total = receitas_total - despesas_total

    st.markdown(
        f"""
    <div style="
    background: linear-gradient(135deg,#1e293b,#334155);
    padding:30px;
    border-radius:20px;
    color:white;
    margin-bottom:20px;
    ">

    <div style="
    font-size:20px;
    font-weight:600;
    margin-top:8px;
    ">
        {st.session_state.usuario.title()}
    </div>

    <p style="font-size:18px;">
    Bem-vindos ao painel financeiro do casal
    </p>

    <hr style="border:1px solid rgba(255,255,255,0.2);">

    <h3>💰 Saldo Atual: R$ {saldo:,.2f}</h3>

    <h3>🏆 Patrimônio: R$ {saldo_total:,.2f}</h3>

    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
        <div style="
            background:white;
            padding:20px;
            border-radius:20px;
            text-align:center;
            box-shadow:0 4px 12px rgba(0,0,0,.08);
        ">
            <div style="font-size:18px;color:#111827;font-weight:600;">
            📈 Receitas
            </div>
            <div style="
                font-size:32px;
                font-weight:bold;
                color:#16a34a;
                margin-top:10px;
            ">
                R$ {receitas:,.2f}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div style="
            background:white;
            padding:20px;
            border-radius:20px;
            text-align:center;
            box-shadow:0 4px 12px rgba(0,0,0,.08);
        ">
            <div style="font-size:18px;color:#111827;font-weight:600;">
            📉 Despesas
            </div>
            <div style="
                font-size:32px;
                font-weight:bold;
                color:#dc2626;
                margin-top:10px;
            ">
                R$ {despesas:,.2f}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        """
    <h2 style='color:#111827'>
    📈 Evolução Financeira
    </h2>
    """,
        unsafe_allow_html=True,
    )

    fluxo = pd.read_sql(
        """
        SELECT data, tipo, valor
        FROM movimentacoes
        """,
        conn,
    )

    fluxo["data"] = pd.to_datetime(fluxo["data"])
    fluxo["mes"] = fluxo["data"].dt.strftime("%m/%Y")

    fluxo_mensal = fluxo.groupby(["mes", "tipo"])["valor"].sum().reset_index()

    fig_fluxo = px.bar(
        fluxo_mensal,
        x="mes",
        y="valor",
        color="tipo",
        barmode="group",
        title="Fluxo de Caixa Mensal",
    )

    fig_fluxo.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_x=0.5,
        font=dict(size=14, color="#111827"),
        xaxis=dict(title_font=dict(color="#111827"), tickfont=dict(color="#111827")),
        yaxis=dict(title_font=dict(color="#111827"), tickfont=dict(color="#111827")),
        legend=dict(font=dict(color="#111827")),
    )

    st.plotly_chart(fig_fluxo, use_container_width=True)

    st.divider()

    st.markdown(
        """
    <h2 style='color:#111827'>
    🏆 Evolução Patrimonial
    </h2>
    """,
        unsafe_allow_html=True,
    )

    mov = pd.read_sql(
        """
        SELECT data, tipo, valor
        FROM movimentacoes
        """,
        conn,
    )

    mov["data"] = pd.to_datetime(mov["data"])

    mov["valor_real"] = mov.apply(
        lambda x: x["valor"] if x["tipo"] == "Receita" else -x["valor"], axis=1
    )

    mov = mov.sort_values("data")

    mov["patrimonio"] = mov["valor_real"].cumsum()

    fig_patrimonio = px.line(
        mov, x="data", y="patrimonio", markers=True, title="Evolução Patrimonial"
    )

    fig_patrimonio.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_x=0.5,
        font=dict(size=14, color="#111827"),
        xaxis=dict(tickfont=dict(color="#111827")),
        yaxis=dict(tickfont=dict(color="#111827")),
    )

    st.plotly_chart(fig_patrimonio, use_container_width=True)

    st.divider()

    despesas_cat = df[df["tipo"] == "Despesa"].groupby("categoria")["valor"].sum()

    st.subheader("🥧 Gastos por Categoria")

    if not despesas_cat.empty:

        grafico = px.pie(
            values=despesas_cat.values,
            names=despesas_cat.index,
            hole=0.6,
            title="Despesas por Categoria",
        )

        grafico.update_traces(textposition="inside", textinfo="percent+label")

        grafico.update_layout(paper_bgcolor="white", plot_bgcolor="white")

        st.plotly_chart(grafico, use_container_width=True)

    ranking = (
        df[df["tipo"] == "Despesa"]
        .groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=False)
    )

    if not ranking.empty:

        st.divider()

        st.subheader("🏆 Ranking de Gastos")

        ranking_df = ranking.reset_index()
        ranking_df.columns = ["Categoria", "Valor"]

        st.dataframe(ranking_df, use_container_width=True, hide_index=True)

    st.subheader("📋 Movimentações")

    for _, mov in df.sort_values("data", ascending=False).iterrows():

        if mov["tipo"] == "Despesa":
            cor = "#dc2626"
            emoji = "🔴"
        else:
            cor = "#16a34a"
            emoji = "🟢"

        st.markdown(
            f"""
            <div style="
                background:white;
                padding:15px;
                border-radius:15px;
                margin-bottom:10px;
                border-left:6px solid {cor};
                box-shadow:0 2px 8px rgba(0,0,0,.08);
            ">

            <div style="
                font-size:24px;
                font-weight:bold;
                color:#111827;
            ">
                {emoji} {mov['descricao']}
            </div>

            <div style="color:gray;">
                {mov['categoria']}
            </div>

            <div style="
                color:{cor};
                font-size:28px;
                font-weight:bold;
                margin-top:10px;">
                R$ {mov['valor']:,.2f}
            </div>

            <div style="color:#666;">
                {mov['data'].strftime('%d/%m/%Y')}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(f"🗑️ Excluir", key=f"mov_{mov['id']}"):

            cursor.execute("DELETE FROM movimentacoes WHERE id = ?", (mov["id"],))

            conn.commit()

            st.success("✅ Movimentação excluída!")

            st.rerun()

# ====================================================
# METAS
# ====================================================

elif menu == "🎯 Metas":

    st.header("🎯 Metas do Casal")

    nome_meta = st.text_input("Nome da Meta")

    segmento = st.selectbox(
        "Segmento",
        [
            "Moradia",
            "Viagem",
            "Veículo",
            "Investimentos",
            "Casamento",
            "Educação",
            "Reserva de Emergência",
            "Outros",
        ],
    )

    valor_objetivo = st.number_input(
        "Valor Objetivo",
        min_value=0.0,
        step=1000.0,
    )

    valor_atual = st.number_input(
        "Valor Já Guardado",
        min_value=0.0,
        step=100.0,
    )

    if st.button("Salvar Meta"):

        cursor.execute(
            """
            INSERT INTO metas
            (nome, segmento, valor_objetivo, valor_atual)
            VALUES (?, ?, ?, ?)
            """,
            (nome_meta, segmento, valor_objetivo, valor_atual),
        )

        conn.commit()

        st.success("✅ Meta cadastrada com sucesso!")

    df_metas = pd.read_sql("SELECT * FROM metas", conn)

    if not df_metas.empty:

        st.subheader("📌 Metas Cadastradas")

        for _, meta in df_metas.iterrows():

            st.divider()

            progresso = (
                meta["valor_atual"] / meta["valor_objetivo"]
                if meta["valor_objetivo"] > 0
                else 0
            )

            faltante = meta["valor_objetivo"] - meta["valor_atual"]

            st.subheader(f"🎯 {meta['nome']}")

            st.markdown(
                f"<p style='color:#111827'>Segmento: {meta['segmento']}</p>",
                unsafe_allow_html=True,
            )

            st.progress(min(progresso, 1.0))

            st.markdown(
                f"<p style='color:#111827'>💰 Guardado: R$ {meta['valor_atual']:,.2f}</p>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"<p style='color:#111827'>🎯 Meta: R$ {meta['valor_objetivo']:,.2f}</p>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"<p style='color:#111827'>📌 Faltam: R$ {faltante:,.2f}</p>",
                unsafe_allow_html=True,
            )

            if st.button(
                f"🗑️ Excluir {meta['nome']}",
                key=f"excluir_{meta['id']}",
            ):

                cursor.execute(
                    "DELETE FROM metas WHERE id = ?",
                    (meta["id"],),
                )

                conn.commit()

                st.success("✅ Meta excluída com sucesso!")

                st.rerun()

# ====================================================
# CARTÕES
# ====================================================

elif menu == "💳 Cartões":

    st.header("💳 Cartões de Crédito")

    nome = st.text_input("Nome do Cartão")

    limite = st.number_input(
        "Limite",
        min_value=0.0,
        step=100.0,
    )

    fechamento = st.number_input(
        "Dia do Fechamento",
        min_value=1,
        max_value=31,
        step=1,
    )

    vencimento = st.number_input(
        "Dia do Vencimento",
        min_value=1,
        max_value=31,
        step=1,
    )

    if st.button("Salvar Cartão"):

        cursor.execute(
            """
            INSERT INTO cartoes
            (
                nome,
                limite,
                fechamento,
                vencimento
            )
            VALUES (?, ?, ?, ?)
            """,
            (nome, limite, fechamento, vencimento),
        )

        conn.commit()

        st.success("✅ Cartão cadastrado com sucesso!")

    st.divider()

    df_cartoes = pd.read_sql(
        "SELECT * FROM cartoes",
        conn,
    )

    if not df_cartoes.empty:

        st.subheader("💳 Cartões Cadastrados")

        for _, cartao in df_cartoes.iterrows():

            st.markdown(
                f"""
            <div style="
            background:white;
            padding:20px;
            border-radius:20px;
            box-shadow:0 4px 12px rgba(0,0,0,.08);
            margin-bottom:15px;
            ">

            <h3>💳 {cartao['nome']}</h3>

            <b>Limite:</b> R$ {cartao['limite']:,.2f}<br>
            <b>Fechamento:</b> Dia {cartao['fechamento']}<br>
            <b>Vencimento:</b> Dia {cartao['vencimento']}

            </div>
            """,
                unsafe_allow_html=True,
            )

            utilizado = pd.read_sql(
                """
                SELECT SUM(valor) total
                FROM movimentacoes
                WHERE forma_pagamento = 'Cartão de Crédito'
                AND cartao = ?
                AND tipo = 'Despesa'
                """,
                conn,
                params=(cartao["nome"],),
            )

            valor_utilizado = utilizado["total"].iloc[0]

            if pd.isna(valor_utilizado):
                valor_utilizado = 0

            st.metric(
                "Fatura Atual",
                f"R$ {valor_utilizado:,.2f}",
            )

            disponivel = cartao["limite"] - valor_utilizado

            st.write(f"Disponível: R$ {disponivel:,.2f}")

            percentual = 0

            if cartao["limite"] > 0:
                percentual = valor_utilizado / cartao["limite"]

            st.progress(min(percentual, 1.0))

            st.write(f"Uso do limite: {percentual:.0%}")

            if st.button(
                f"🗑️ Excluir {cartao['nome']}",
                key=f"cartao_{cartao['id']}",
            ):

                cursor.execute(
                    "DELETE FROM cartoes WHERE id = ?",
                    (cartao["id"],),
                )

                conn.commit()

                st.success("✅ Cartão excluído!")

                st.rerun()

            st.divider()
