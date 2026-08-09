import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Educação Infantil - Viçosa/MG", layout="wide")

DB_PATH = "vicosa_educacao_infantil.db"
FONTE = ("Fonte: Murilo Sousa Ferreira com base no INEP/MEC — Censo Escolar da Educação "
         "Básica (2007–2024). Disponível em https://www.gov.br/inep/pt-br/acesso-a-informacao/"
         "dados-abertos/microdados/censo-escolar.")


@st.cache_resource
def conectar():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data
def carregar_matriculas_ano():
    conn = conectar()
    return pd.read_sql("SELECT * FROM matriculas_ano", conn)


@st.cache_data
def carregar_instituicoes():
    conn = conectar()
    return pd.read_sql("SELECT * FROM instituicoes", conn)


@st.cache_data
def carregar_convenio_tipo_ano():
    conn = conectar()
    return pd.read_sql("SELECT * FROM convenio_tipo_ano", conn)


def adicionar_fonte(fig):
    fig.update_layout(
        annotations=[dict(
            text=FONTE, x=0, y=-0.22, xref="paper", yref="paper",
            showarrow=False, xanchor="left", yanchor="top",
            font=dict(size=11, color="#666666")
        )],
        margin=dict(b=90)
    )
    return fig


matriculas = carregar_matriculas_ano()
instituicoes = carregar_instituicoes()
convenio_ano = carregar_convenio_tipo_ano()

st.title("Educação Infantil em Viçosa/MG (2007–2024)")
st.caption("Painel de exploração dos microdados do Censo Escolar, já reconciliados por CO_ENTIDADE.")

# FILTROS
st.sidebar.header("Filtros")

anos_disponiveis = sorted(matriculas["ano"].unique())
ano_inicio, ano_fim = st.sidebar.select_slider(
    "Intervalo de anos",
    options=anos_disponiveis,
    value=(anos_disponiveis[0], anos_disponiveis[-1])
)

dependencias = sorted(matriculas["dependencia"].dropna().unique())
f_dependencia = st.sidebar.multiselect("Dependência administrativa", dependencias, default=dependencias)

categorias = sorted(matriculas["categoria_privada"].dropna().unique())
categorias = [c for c in categorias if c != "—" and c != "-"]
f_categoria = st.sidebar.multiselect("Categoria da escola privada", categorias, default=categorias)

convenios = sorted(matriculas["convenio"].dropna().unique())
f_convenio = st.sidebar.multiselect("Convênio com o poder público", convenios, default=convenios)

localizacoes = sorted(matriculas["localizacao"].dropna().unique())
f_localizacao = st.sidebar.multiselect("Localização", localizacoes, default=localizacoes)

# Aplica os filtros. Escolas publicas nao tem categoria_privada valida,
# entao elas passam no filtro de categoria automaticamente.
mask = (
    matriculas["ano"].between(ano_inicio, ano_fim)
    & matriculas["dependencia"].isin(f_dependencia)
    & matriculas["convenio"].isin(f_convenio)
    & matriculas["localizacao"].isin(f_localizacao)
    & (matriculas["categoria_privada"].isin(f_categoria) | matriculas["dependencia"].isin(["Municipal", "Federal", "Estadual"]))
)
dados_filtrados = matriculas[mask]

if dados_filtrados.empty:
    st.warning("Nenhum dado encontrado para essa combinação de filtros. Ajuste os filtros na barra lateral.")
    st.stop()

ultimo_ano_filtro = dados_filtrados["ano"].max()
dados_ultimo_ano = dados_filtrados[dados_filtrados["ano"] == ultimo_ano_filtro]

# METRICAS
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"Instituições ativas em {ultimo_ano_filtro}", dados_ultimo_ano["co_entidade"].nunique())
col2.metric(f"Matrículas totais em {ultimo_ano_filtro}", int(dados_ultimo_ano["total_ei"].sum()))
col3.metric(f"Matrículas creche em {ultimo_ano_filtro}", int(dados_ultimo_ano["matriculas_creche"].sum()))
col4.metric(f"Matrículas pré-escola em {ultimo_ano_filtro}", int(dados_ultimo_ano["matriculas_pre"].sum()))

st.divider()

# EVOLUCAO TEMPORAL
st.subheader("Evolução das matrículas no período filtrado")

evolucao = dados_filtrados.groupby("ano").agg(
    Total=("total_ei", "sum"),
    Creche=("matriculas_creche", "sum"),
    **{"Pré-Escola": ("matriculas_pre", "sum")}
).reset_index()

metrica_evolucao = st.radio("Ver:", ["Total", "Creche", "Pré-Escola", "Todas"], horizontal=True)

if metrica_evolucao == "Todas":
    evolucao_long = evolucao.melt(id_vars="ano", value_vars=["Total", "Creche", "Pré-Escola"], var_name="Segmento", value_name="Matrículas")
    fig_evolucao = px.line(evolucao_long, x="ano", y="Matrículas", color="Segmento", markers=True, title="Evolução das matrículas por segmento")
else:
    fig_evolucao = px.line(evolucao, x="ano", y=metrica_evolucao, markers=True, title=f"Evolução das matrículas — {metrica_evolucao}")

fig_evolucao.update_layout(xaxis_title="Ano", yaxis_title="Nº de matrículas")
fig_evolucao = adicionar_fonte(fig_evolucao)
st.plotly_chart(fig_evolucao, use_container_width=True)

st.divider()

# INSTITUICOES POR DEPENDENCIA (ano mais recente do filtro)
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader(f"Instituições por dependência administrativa em {ultimo_ano_filtro}")
    contagem_dep = dados_ultimo_ano.groupby("dependencia")["co_entidade"].nunique().reset_index()
    contagem_dep.columns = ["Dependência", "Quantidade"]
    fig_dep = px.bar(contagem_dep, x="Dependência", y="Quantidade", text="Quantidade", title=f"Instituições por dependência — {ultimo_ano_filtro}")
    fig_dep = adicionar_fonte(fig_dep)
    st.plotly_chart(fig_dep, use_container_width=True)

with col_dir:
    st.subheader(f"Instituições privadas por categoria em {ultimo_ano_filtro}")
    privadas_ano = dados_ultimo_ano[dados_ultimo_ano["dependencia"] == "Privada"]
    contagem_cat = privadas_ano.groupby("categoria_privada")["co_entidade"].nunique().reset_index()
    contagem_cat.columns = ["Categoria", "Quantidade"]
    fig_cat = px.bar(contagem_cat, x="Categoria", y="Quantidade", text="Quantidade", title=f"Categoria de escola privada — {ultimo_ano_filtro}")
    fig_cat = adicionar_fonte(fig_cat)
    st.plotly_chart(fig_cat, use_container_width=True)

st.divider()

# CONVENIO POR TIPO E ANO
st.subheader("Instituições por tipo de convênio com o poder público")
convenio_filtrado = convenio_ano[convenio_ano["ano"].between(ano_inicio, ano_fim)]
fig_convenio = px.line(convenio_filtrado, x="ano", y="n_instituicoes", color="tipo_convenio", markers=True,
                        title="Número de instituições por tipo de convênio e ano")
fig_convenio.update_layout(xaxis_title="Ano", yaxis_title="Nº de instituições", legend_title="Tipo de convênio")
fig_convenio = adicionar_fonte(fig_convenio)
st.plotly_chart(fig_convenio, use_container_width=True)

st.divider()


# BUSCA DE INSTITUICOES
st.subheader("Buscar instituição")
termo_busca = st.text_input("Digite parte do nome da instituição:")

instituicoes_exibir = instituicoes.copy()
if termo_busca:
    instituicoes_exibir = instituicoes_exibir[
        instituicoes_exibir["nome"].str.contains(termo_busca, case=False, na=False)
    ]

colunas_exibir = [
    "nome", "dependencia", "categoria_privada", "convenio", "localizacao",
    "tipo_oferta", "primeiro_ano", "ultimo_ano", "anos_ativos",
    "matriculas_creche_total", "matriculas_pre_total", "total_ei", "situacao_2024"
]
st.dataframe(
    instituicoes_exibir[colunas_exibir].sort_values("total_ei", ascending=False),
    use_container_width=True,
    hide_index=True
)

if not instituicoes_exibir.empty and termo_busca:
    st.markdown("#### Trajetória da(s) instituição(ões) encontrada(s)")
    cos = instituicoes_exibir["co_entidade"].tolist()
    trajetoria = matriculas[matriculas["co_entidade"].isin(cos)].merge(
        instituicoes[["co_entidade", "nome"]], on="co_entidade"
    )
    fig_traj = px.line(trajetoria.sort_values("ano"), x="ano", y="total_ei", color="nome", markers=True, title="Matrículas por ano")
    fig_traj.update_layout(xaxis_title="Ano", yaxis_title="Matrículas")
    fig_traj = adicionar_fonte(fig_traj)
    st.plotly_chart(fig_traj, use_container_width=True)

st.caption(FONTE)