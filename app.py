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
VALUES ('guilherme', '291060')
""")

cursor.execute("""
INSERT OR IGNORE INTO usuarios
(usuario, senha)
VALUES ('isabelle', '302742')
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

    /* Fundo */
    .stApp{
        background-color:#f3f4f6;
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
        padding:20px;
        border-radius:18px;
        box-shadow:0 6px 18px rgba(0,0,0,.08);
        margin-bottom:12px;
    }

    [data-testid="stMetricValue"]{
        color:#111827 !important;
        font-size:40px !important;
        font-weight:700 !important;
    }

    [data-testid="stMetricLabel"]{
        color:#374151 !important;
        font-size:18px !important;
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

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

menu = "🏠 Início"

if st.session_state.logado:

    menu = st.segmented_control(
        "",
        ["🏠 Início", "➕ Movimentação", "📊 Dashboard", "🎯 Metas", "💳 Cartões"],
        default="🏠 Início",
    )

    col1, col2 = st.columns([5, 1])

    with col2:
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

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
    padding:18px;
    border-radius:20px;
    color:white;
    box-shadow:0 8px 20px rgba(0,200,83,.30);
    margin-bottom:20px;
    ">

    <p style="
    margin:0;
    font-size:16px;
    opacity:.9;
    ">
    {saudacao}
    </p>

    <h2 style="
    margin-top:10px;
    margin-bottom:5px;
    ">
    {st.session_state.usuario}
    </h2>

    <h1 style="
    font-size:50px;
    margin-top:15px;
    margin-bottom:0;
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

    col1, col2 = st.columns(2)

    with col1:
        st.metric("📈 Receitas", f"R$ {receitas:,.2f}")

    with col2:
        st.metric("📉 Despesas", f"R$ {despesas:,.2f}")

    st.markdown(
        "<h3 style='color:#111827;'>⚡ Ações Rápidas</h3>", unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("➕ Nova")

    with col2:
        st.button("🎯 Metas")

    with col3:
        st.button("💳 Cartões")

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
        "<h3 style='color:#111827;'>🕒 Últimas Movimentações</h3>",
        unsafe_allow_html=True,
    )

    ultimas = df_inicio.sort_values("data", ascending=False).head(5)

    for _, mov in ultimas.iterrows():

        if mov["tipo"] == "Despesa":
            cor = "#dc2626"
            emoji = "🔴"
        else:
            cor = "#16a34a"
            emoji = "🟢"

        st.markdown(
            f"""
            <div style="background:white;
                    padding:25px;
                    border-radius:20px;
                    margin-bottom:15px;
                    border-left:8px solid {cor};
                    box-shadow:0 4px 12px rgba(0,0,0,.08);">

            <h3 style="margin:0;color:#111827;">
                {emoji} {mov['descricao']}
            </h3>

            <p style="color:#6b7280;">
                {mov['categoria']}
            </p>

            <h2 style="color:{cor};margin-top:10px;">
                R$ {mov['valor']:,.2f}
            </h2>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ====================================================
# DASHBOARD
# ====================================================

elif menu == "📊 Dashboard":

    st.header("📊 Dashboard")

    df = pd.read_sql("SELECT * FROM movimentacoes", conn)

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

    <h2>👋 Olá, Guilherme e Isabelle!</h2>

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
            <div style="font-size:18px;">📈 Receitas</div>
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
            <div style="font-size:18px;">📉 Despesas</div>
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

    st.subheader("📈 Evolução Financeira")

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
        paper_bgcolor="white", plot_bgcolor="white", font=dict(size=14), title_x=0.5
    )

    st.plotly_chart(fig_fluxo, use_container_width=True)

    st.divider()

    st.subheader("🏆 Evolução Patrimonial")

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
        paper_bgcolor="white", plot_bgcolor="white", font=dict(size=14), title_x=0.5
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

            <div style="font-size:24px;font-weight:bold;">
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

        if st.button(
            f"🗑️ Excluir",
            key=f"mov_{mov['id']}"
        ):

            cursor.execute(
                "DELETE FROM movimentacoes WHERE id = ?",
                (mov["id"],)
            )

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

            st.write(f"Segmento: {meta['segmento']}")

            st.progress(min(progresso, 1.0))

            st.write(f"💰 Guardado: R$ {meta['valor_atual']:,.2f}")

            st.write(f"🎯 Meta: R$ {meta['valor_objetivo']:,.2f}")

            st.write(f"📌 Faltam: R$ {faltante:,.2f}")

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
