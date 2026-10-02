import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import shutil
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
    initial_sidebar_state="collapsed"
)

if "logado" not in st.session_state:
    st.session_state.logado = False

st.markdown("""
<style>

/* Fundo principal */
.stApp {
    background-color: #f5f7fb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}

/* Cards */
[data-testid="stMetric"] {
    background-color: white;
    border-radius: 16px;
    padding: 15px;
}

/* Tabelas */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 15px;
}

/* Botões */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    background-color: #22c55e;
    color: white;
    border: none;
    height: 45px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #16a34a;
    color: white;
}

</style>
""", unsafe_allow_html=True)

if st.session_state.get("logado", False):

    st.markdown("""
    <div style="
    background: linear-gradient(90deg, #16a34a, #22c55e);
    padding: 25px;
    border-radius: 20px;
    color: white;
    margin-bottom: 20px;
    ">

    <h1>💰 Finanças do Casal</h1>

    <p style="font-size:18px;">
    Controle financeiro de Guilherme e Isabelle
    </p>

    </div>
    """, unsafe_allow_html=True)

if st.session_state.logado:

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Dashboard",
            "Nova Movimentação",
            "Editar Movimentação",
            "Metas",
            "Cartões",
            "Usuários",
            "Backup"
        ]
    )
    
    st.sidebar.success(
        f"✅ {st.session_state.usuario}"
    )

    if st.sidebar.button("🚪 Sair"):

        st.session_state.logado = False

        if "usuario" in st.session_state:
            del st.session_state.usuario

        st.rerun()

if not st.session_state.logado:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown("""
        <div style="
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
        text-align:center;
        ">
            <h1>💰 Finanças do Casal</h1>
            <p>Bem-vindos Guilherme e Isabelle</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        usuario = st.text_input(
            "👤 Usuário"
        )

        senha = st.text_input(
            "🔒 Senha",
            type="password"
        )

        if st.button("🚀 Entrar"):

            consulta = pd.read_sql(
                """
                SELECT *
                FROM usuarios
                WHERE usuario = ?
                AND senha = ?
                """,
                conn,
                params=(usuario, senha)
            )

            if not consulta.empty:

                st.session_state.logado = True
                st.session_state.usuario = usuario

                st.success(
                    "✅ Login realizado com sucesso!"
                )

                st.rerun()

            else:

                st.error(
                    "❌ Usuário ou senha inválidos"
                )

    st.stop()

# ====================================================
# NOVA MOVIMENTAÇÃO
# ====================================================

if menu == "Nova Movimentação":

    st.header("➕ Nova Movimentação")

    tipo = st.selectbox(
        "Tipo",
        ["Receita", "Despesa"]
    )

    pessoa = st.selectbox(
        "Pessoa",
        ["Guilherme", "Isabelle", "Compartilhado"]
    )

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
            "Outros"
        ]
    )

    forma_pagamento = st.selectbox(
        "Forma de Pagamento",
        [
            "PIX",
            "Dinheiro",
            "Débito",
            "Cartão de Crédito"
        ]
    )

    cartao_utilizado = ""

    if forma_pagamento == "Cartão de Crédito":

        lista_cartoes = pd.read_sql(
            "SELECT nome FROM cartoes",
            conn
        )

        if not lista_cartoes.empty:

            cartao_utilizado = st.selectbox(
                "Cartão Utilizado",
                lista_cartoes["nome"].tolist()
            )

    descricao = st.text_input("Descrição")

    data = st.date_input("Data")

    valor = st.number_input(
        "Valor",
        min_value=0.0,
        step=1.0
    )

    if st.button("Salvar Movimentação"):

        cursor.execute("""
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
        """, (
            str(data),
            tipo,
            pessoa,
            categoria,
            forma_pagamento,
            cartao_utilizado,
            descricao,
            valor
        ))

        conn.commit()

        st.success("✅ Movimentação salva com sucesso!")
        
# ====================================================
# EDITAR MOVIMENTAÇÃO
# ====================================================

elif menu == "Editar Movimentação":

    st.header("✏️ Editar Movimentação")

    df_mov = pd.read_sql(
        "SELECT * FROM movimentacoes",
        conn
    )

    if df_mov.empty:

        st.info("Nenhuma movimentação cadastrada.")

    else:

        movimentacao_id = st.selectbox(
            "Selecione a movimentação",
            df_mov["id"]
        )

        registro = df_mov[
            df_mov["id"] == movimentacao_id
        ].iloc[0]

        data = st.date_input(
            "Data",
            pd.to_datetime(registro["data"])
        )

        tipo = st.selectbox(
            "Tipo",
            ["Receita", "Despesa"],
            index=0 if registro["tipo"] == "Receita" else 1
        )

        pessoa = st.selectbox(
            "Pessoa",
            ["Guilherme", "Isabelle", "Compartilhado"],
            index=[
                "Guilherme",
                "Isabelle",
                "Compartilhado"
            ].index(registro["pessoa"])
        )

        categoria = st.text_input(
            "Categoria",
            registro["categoria"]
        )

        descricao = st.text_input(
            "Descrição",
            registro["descricao"]
        )

        valor = st.number_input(
            "Valor",
            value=float(registro["valor"])
        )
        
        opcoes_pagamento = [
            "PIX",
            "Dinheiro",
            "Débito",
            "Cartão de Crédito"
        ]

        forma_pagamento = st.selectbox(
            "Forma de Pagamento",
            opcoes_pagamento,
            index=opcoes_pagamento.index(
                registro["forma_pagamento"]
            ) if registro["forma_pagamento"] in opcoes_pagamento else 0
        )
        
        cartao_utilizado = ""
        
        if forma_pagamento == "Cartão de Crédito":

            lista_cartoes = pd.read_sql(
                "SELECT nome FROM cartoes",
                conn
            )

            if not lista_cartoes.empty:

                cartoes = lista_cartoes["nome"].tolist()

                cartao_utilizado = st.selectbox(
                    "Cartão",
                    cartoes,
                    index=cartoes.index(registro["cartao"])
                    if registro["cartao"] in cartoes
                    else 0
                )

        if st.button("Salvar Alterações"):

            cursor.execute(
                """
                UPDATE movimentacoes
                SET
                    data = ?,
                    tipo = ?,
                    pessoa = ?,
                    categoria = ?,
                    forma_pagamento = ?,
                    cartao = ?,
                    descricao = ?,
                    valor = ?
                WHERE id = ?
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
                    movimentacao_id
                )
            )

            conn.commit()

            st.success(
                "✅ Movimentação atualizada com sucesso!"
            )

            st.rerun()

# ====================================================
# DASHBOARD
# ====================================================

elif menu == "Dashboard":

    st.header("📊 Dashboard")

    df = pd.read_sql(
        "SELECT * FROM movimentacoes",
        conn
    )

    if df.empty:

        st.info("Nenhuma movimentação cadastrada.")

    else:

        df["data"] = pd.to_datetime(df["data"])

        meses = sorted(
            df["data"].dt.strftime("%m/%Y").unique(),
            reverse=True
        )

        mes_selecionado = st.selectbox(
            "📅 Selecione o Mês",
            meses
        )

        df = df[
            df["data"].dt.strftime("%m/%Y")
            == mes_selecionado
        ]

        receitas = df[
            df["tipo"] == "Receita"
        ]["valor"].sum()

        despesas = df[
            df["tipo"] == "Despesa"
        ]["valor"].sum()

        saldo = receitas - despesas
        
        
        receitas_total = pd.read_sql(
            """
            SELECT SUM(valor) total
            FROM movimentacoes
            WHERE tipo='Receita'
            """,
            conn
        )["total"].iloc[0]

        despesas_total = pd.read_sql(
            """
            SELECT SUM(valor) total
            FROM movimentacoes
            WHERE tipo='Despesa'
            """,
            conn
        )["total"].iloc[0]

        if pd.isna(receitas_total):
            receitas_total = 0

        if pd.isna(despesas_total):
            despesas_total = 0

        saldo_total = receitas_total - despesas_total

    st.markdown(f"""
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
    """, unsafe_allow_html=True)

    st.metric("💰 Receitas", f"R$ {receitas:,.2f}")
    st.metric("💸 Despesas", f"R$ {despesas:,.2f}")
    st.metric("🏦 Saldo", f"R$ {saldo:,.2f}")
    st.metric("🏆 Patrimônio", f"R$ {saldo_total:,.2f}")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="
        background:linear-gradient(135deg,#16a34a,#22c55e);
        color:white;
        padding:20px;
        border-radius:15px;
        text-align:center;
        box-shadow:0px 2px 8px rgba(0,0,0,0.1);
        ">
            <h4>💰 Receitas</h4>
            <h2>R$ {receitas:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
        background:linear-gradient(135deg,#dc2626,#ef4444);
        color:white;
        padding:20px;
        border-radius:15px;
        text-align:center;
        box-shadow:0px 2px 8px rgba(0,0,0,0.1);
        ">
            <h4>💸 Despesas</h4>
            <h2>R$ {despesas:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="
        background:linear-gradient(135deg,#2563eb,#3b82f6);
        color:white;
        padding:20px;
        border-radius:15px;
        text-align:center;
        box-shadow:0px 2px 8px rgba(0,0,0,0.1);
        ">
            <h4>🏦 Saldo</h4>
            <h2>R$ {saldo:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="
        background:linear-gradient(135deg,#7c3aed,#9333ea);
        color:white;
        padding:20px;
        border-radius:15px;
        text-align:center;
        box-shadow:0px 2px 8px rgba(0,0,0,0.1);
        ">
            <h4>🏆 Patrimônio</h4>
            <h2>R$ {saldo_total:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    col_a, col_b, col_c = st.columns(3)

    taxa_economia = 0

    if receitas > 0:
        taxa_economia = (saldo / receitas) * 100

    with col_a:
        st.metric(
            "📈 Taxa de Economia",
            f"{taxa_economia:.1f}%"
        )

    with col_b:
        st.metric(
            "💸 Total de Despesas",
            f"R$ {despesas:,.2f}"
        )

    with col_c:
        st.metric(
            "🏆 Patrimônio Total",
            f"R$ {saldo_total:,.2f}"
        )

    st.divider()

    st.subheader("🎯 Meta Financeira do Casal")

    meta = st.number_input(
        "Meta do Casal",
        min_value=0.0,
        value=100000.0,
        step=1000.0
    )

    progresso = saldo / meta if meta > 0 else 0

    st.progress(
        min(progresso, 1.0)
    )

    faltante = max(
        meta - saldo,
        0
    )

    st.write(
        f"R$ {saldo:,.2f} acumulados de R$ {meta:,.2f}"
    )

    st.write(
        f"Faltam R$ {faltante:,.2f} para atingir a meta."
    )

    st.divider()

    st.subheader("👥 Resumo por Pessoa")

    for nome in ["Guilherme", "Isabelle"]:

        receitas_p = df[
            (df["tipo"] == "Receita") &
            (df["pessoa"] == nome)
        ]["valor"].sum()

        despesas_p = df[
            (df["tipo"] == "Despesa") &
            (df["pessoa"] == nome)
        ]["valor"].sum()

        saldo_p = receitas_p - despesas_p

        st.write(
            f"**{nome}** | "
            f"Receita: R$ {receitas_p:,.2f} | "
            f"Despesa: R$ {despesas_p:,.2f} | "
            f"Saldo: R$ {saldo_p:,.2f}"
        )

    st.divider()

    st.subheader("📊 Comparativo do Casal")

    comparativo = []

    for nome in ["Guilherme", "Isabelle"]:

        receitas_p = df[
            (df["tipo"] == "Receita") &
            (df["pessoa"] == nome)
        ]["valor"].sum()

        despesas_p = df[
            (df["tipo"] == "Despesa") &
            (df["pessoa"] == nome)
        ]["valor"].sum()

        comparativo.append({
            "Pessoa": nome,
            "Saldo": receitas_p - despesas_p
        })

    comparativo_df = pd.DataFrame(comparativo)

    fig = px.bar(
        comparativo_df,
        x="Pessoa",
        y="Saldo",
        color="Pessoa",
        text_auto=True,
        title="Saldo por Pessoa"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader("📈 Evolução Financeira")
    
    fluxo = pd.read_sql(
        """
        SELECT data, tipo, valor
        FROM movimentacoes
        """,
        conn
    )

    fluxo["data"] = pd.to_datetime(fluxo["data"])
    fluxo["mes"] = fluxo["data"].dt.strftime("%m/%Y")

    fluxo_mensal = (
        fluxo.groupby(["mes", "tipo"])["valor"]
        .sum()
        .reset_index()
    )

    fig_fluxo = px.bar(
        fluxo_mensal,
        x="mes",
        y="valor",
        color="tipo",
        barmode="group",
        title="Fluxo de Caixa Mensal"
    )

    st.plotly_chart(
        fig_fluxo,
        use_container_width=True
    )

    evolucao = pd.read_sql(
        "SELECT data, valor FROM movimentacoes",
        conn
    )

    evolucao["data"] = pd.to_datetime(
        evolucao["data"]
    )

    evolucao["mes"] = evolucao["data"].dt.strftime(
        "%m/%Y"
    )

    evolucao = (
        evolucao.groupby("mes")["valor"]
        .sum()
        .reset_index()
    )

    fig2 = px.line(
        evolucao,
        x="mes",
        y="valor",
        markers=True,
        title="Evolução dos Valores"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.divider()

    st.subheader("🏆 Evolução Patrimonial")

    mov = pd.read_sql(
        """
        SELECT data, tipo, valor
        FROM movimentacoes
        """,
        conn
    )

    mov["data"] = pd.to_datetime(mov["data"])

    mov["valor_real"] = mov.apply(
        lambda x: x["valor"]
        if x["tipo"] == "Receita"
        else -x["valor"],
        axis=1
    )

    mov = mov.sort_values("data")

    mov["patrimonio"] = mov["valor_real"].cumsum()

    fig_patrimonio = px.line(
        mov,
        x="data",
        y="patrimonio",
        markers=True,
        title="Evolução Patrimonial"
    )

    st.plotly_chart(
        fig_patrimonio,
        use_container_width=True
    )

    st.subheader("🔥 Top 10 Maiores Gastos")

    top_gastos = (
        df[df["tipo"] == "Despesa"]
        .sort_values("valor", ascending=False)
        .head(10)
    )

    if not top_gastos.empty:

        fig_top = px.bar(
            top_gastos,
            x="descricao",
            y="valor",
            color="valor",
            text_auto=True,
            title="Top 10 Maiores Gastos"
        )

        fig_top.update_layout(
            showlegend=False
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True
        )

    st.divider()

    st.subheader("👤 Participação dos Gastos por Pessoa")

    gastos_pessoa = (
        df[df["tipo"] == "Despesa"]
        .groupby("pessoa")["valor"]
        .sum()
        .reset_index()
    )

    if not gastos_pessoa.empty:

        fig_pessoa = px.pie(
            gastos_pessoa,
            values="valor",
            names="pessoa",
            hole=0.5,
            title="Participação dos Gastos"
        )

        st.plotly_chart(
            fig_pessoa,
            use_container_width=True
        )
        
    st.divider()

    st.subheader("💳 Gastos por Cartão")

    gastos_cartao = (
        df[
            (df["tipo"] == "Despesa")
            & (df["cartao"].notna())
            & (df["cartao"] != "")
        ]
        .groupby("cartao")["valor"]
        .sum()
        .reset_index()
    )

    if not gastos_cartao.empty:

        fig_cartao = px.bar(
            gastos_cartao,
            x="cartao",
            y="valor",
            color="valor",
            text_auto=True,
            title="Gastos por Cartão"
        )

        fig_cartao.update_layout(
            showlegend=False
        )

        st.plotly_chart(
            fig_cartao,
            use_container_width=True
        )

    st.subheader("🗑️ Excluir Movimentação")

    id_excluir = st.number_input(
        "Informe o ID",
        min_value=1,
        step=1
    )

    if st.button("Excluir Registro"):

        cursor.execute(
            "DELETE FROM movimentacoes WHERE id = ?",
            (id_excluir,)
        )

        conn.commit()

        st.success(
            "✅ Registro excluído com sucesso!"
        )

        st.rerun()

    st.divider()
    
    ranking = (
        df[df["tipo"] == "Despesa"]
        .groupby("categoria")["valor"]
        .sum()
        .reset_index()
        .sort_values("valor", ascending=False)
    )

    despesas_cat = (
        df[df["tipo"] == "Despesa"]
        .groupby("categoria")["valor"]
        .sum()
    )
    

    st.subheader("📊 Análise Financeira")

    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:

        if not despesas_cat.empty:

            grafico = px.pie(
                values=despesas_cat.values,
                names=despesas_cat.index,
                hole=0.6,
                title="Despesas por Categoria"
            )

            grafico.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white"
            )

            st.plotly_chart(
                grafico,
                use_container_width=True
            )

    with col_graf2:

        fig_ranking = px.bar(
            ranking,
            x="categoria",
            y="valor",
            color="valor",
            title="Maiores Gastos",
            text_auto=True
        )

        fig_ranking.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False
        )

        st.plotly_chart(
            fig_ranking,
            use_container_width=True
        )
    
    st.subheader("📋 Movimentações")
    
    st.write(f"Total de registros: {len(df)}")

    st.dataframe(
        df,
        use_container_width=True
    )
    
    excel = df.to_csv(
        index=False,
        sep=";",
        decimal=","
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Baixar Movimentações",
        data=excel,
        file_name="movimentacoes.csv",
        mime="text/csv"
    )

# ====================================================
# METAS
# ====================================================

elif menu == "Metas":

    st.header("🎯 Metas do Casal")

    nome_meta = st.text_input(
        "Nome da Meta"
    )

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
            "Outros"
        ]
    )

    valor_objetivo = st.number_input(
        "Valor Objetivo",
        min_value=0.0,
        step=1000.0
    )

    valor_atual = st.number_input(
        "Valor Já Guardado",
        min_value=0.0,
        step=100.0
    )

    if st.button("Salvar Meta"):

        cursor.execute("""
        INSERT INTO metas
        (nome, segmento, valor_objetivo, valor_atual)
        VALUES (?, ?, ?, ?)
        """, (
            nome_meta,
            segmento,
            valor_objetivo,
            valor_atual
        ))

        conn.commit()

        st.success(
            "✅ Meta cadastrada com sucesso!"
        )

    df_metas = pd.read_sql(
        "SELECT * FROM metas",
        conn
    )
    

    if not df_metas.empty:

        st.subheader("📌 Metas Cadastradas")

        for _, meta in df_metas.iterrows():

            st.divider()

            progresso = (
                meta["valor_atual"]
                / meta["valor_objetivo"]
                if meta["valor_objetivo"] > 0
                else 0
            )

            faltante = (
                meta["valor_objetivo"]
                - meta["valor_atual"]
            )

            st.subheader(
                f"🎯 {meta['nome']}"
            )

            st.write(
                f"Segmento: {meta['segmento']}"
            )

            st.progress(
                min(progresso, 1.0)
            )

            st.write(
                f"💰 Guardado: R$ {meta['valor_atual']:,.2f}"
            )

            st.write(
                f"🎯 Meta: R$ {meta['valor_objetivo']:,.2f}"
            )

            st.write(
                f"📌 Faltam: R$ {faltante:,.2f}"
            )
            
            if st.button(
            f"🗑️ Excluir {meta['nome']}",
            key=f"excluir_{meta['id']}"
            ):

                cursor.execute(
                    "DELETE FROM metas WHERE id = ?",
                    (meta["id"],)
                )

                conn.commit()

                st.success(
                    "✅ Meta excluída com sucesso!"
                )

                st.rerun()

# ====================================================
# CARTÕES
# ====================================================

elif menu == "Cartões":

    st.header("💳 Cartões de Crédito")

    nome = st.text_input("Nome do Cartão")

    limite = st.number_input(
        "Limite",
        min_value=0.0,
        step=100.0
    )

    fechamento = st.number_input(
        "Dia do Fechamento",
        min_value=1,
        max_value=31,
        step=1
    )

    vencimento = st.number_input(
        "Dia do Vencimento",
        min_value=1,
        max_value=31,
        step=1
    )

    if st.button("Salvar Cartão"):

        cursor.execute("""
        INSERT INTO cartoes
        (
            nome,
            limite,
            fechamento,
            vencimento
        )
        VALUES (?, ?, ?, ?)
        """, (
            nome,
            limite,
            fechamento,
            vencimento
        ))

        conn.commit()

        st.success("✅ Cartão cadastrado com sucesso!")

    st.divider()

    df_cartoes = pd.read_sql(
        "SELECT * FROM cartoes",
        conn
    )

    if not df_cartoes.empty:

        st.subheader("💳 Cartões Cadastrados")

        for _, cartao in df_cartoes.iterrows():

            st.write(
                f"**{cartao['nome']}**"
            )

            st.write(
                f"Limite: R$ {cartao['limite']:,.2f}"
            )

            st.write(
                f"Fechamento: Dia {cartao['fechamento']}"
            )

            st.write(
                f"Vencimento: Dia {cartao['vencimento']}"
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
                params=(cartao["nome"],)
            )
            
            valor_utilizado = utilizado["total"].iloc[0]

            if valor_utilizado is None or pd.isna(valor_utilizado):
                valor_utilizado = 0.0

            valor_utilizado = float(valor_utilizado)

            st.metric(
                "Fatura Atual",
                f"R$ {valor_utilizado:,.2f}"
            )

            if pd.isna(valor_utilizado):
                valor_utilizado = 0

            disponivel = cartao["limite"] - valor_utilizado

            st.write(
                f"Utilizado: R$ {valor_utilizado:,.2f}"
            )

            st.write(
                f"Disponível: R$ {disponivel:,.2f}"
            )

            percentual = 0

            if cartao["limite"] > 0:
                percentual = valor_utilizado / cartao["limite"]

            st.progress(
                min(percentual, 1.0)
            )

            st.write(
                f"Uso do limite: {percentual:.0%}"
            )

            if st.button(
                f"🗑️ Excluir {cartao['nome']}",
                key=f"cartao_{cartao['id']}"
            ):

                cursor.execute(
                    "DELETE FROM cartoes WHERE id = ?",
                    (cartao["id"],)
                )

                conn.commit()

                st.success("✅ Cartão excluído!")

                st.rerun()

            st.divider()

# ====================================================
# USUÁRIOS
# ====================================================

elif menu == "Usuários":

    st.header("👤 Gerenciar Usuários")

    novo_usuario = st.text_input("Usuário")

    nova_senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Cadastrar Usuário"):

        try:

            cursor.execute(
                """
                INSERT INTO usuarios
                (usuario, senha)
                VALUES (?, ?)
                """,
                (novo_usuario, nova_senha)
            )

            conn.commit()

            st.success(
                "✅ Usuário cadastrado!"
            )

        except:

            st.error(
                "❌ Usuário já existe."
            )

    st.divider()

    usuarios = pd.read_sql(
        "SELECT id, usuario FROM usuarios",
        conn
    )

    st.dataframe(
        usuarios,
        use_container_width=True
    )
    
# ====================================================
# BACKUP
# ====================================================

elif menu == "Backup":

    st.header("💾 Backup do Banco")

    if st.button("Gerar Backup"):

        nome_backup = (
            f"backup_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )

        shutil.copy(
            "financas.db",
            nome_backup
        )

        st.success(
            f"✅ Backup criado: {nome_backup}"
        )