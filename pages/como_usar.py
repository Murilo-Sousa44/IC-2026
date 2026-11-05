import streamlit as st

FONTE = ("Fonte: Murilo Sousa Ferreira com base no INEP/MEC — Censo Escolar da Educação "
         "Básica (2007–2024). Disponível em https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar.")

#--------------------------------------------------- SOBRE O SITE ------------------------------------------------

st.title("Sobre o painel")

st.write("""
Este painel apresenta informações sobre a Educação Infantil
no município de Viçosa-MG, utilizando os microdados do
Censo Escolar da Educação Básica (2007–2024). Os dados foram coletados no site do MEC https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar e sem seguida, tratados com matplotlib e pandas. As consultas e carregamento do banco de dados (educacao_infantil.db) foram feitas utilizando SQL para melhor otimização.
Este é um projeto de Iniciação Científica desenvolvido por Murilo Sousa / DPI UFV (murilo.sousa@ufv.br) com orientação da prof. Terezinha Duarte Vieira / DPE UFV
""")

st.divider()

st.header("Significado das colunas utilizadas para filtragem")

st.subheader("Identificação")

st.markdown("""
- **co_entidade:** código de identificação da instituição no INEP.
- **nome:** nome da instituição.
- **dependencia:** dependência administrativa (Municipal, Estadual, Federal ou Privada).
- **categoria_privada:** categoria da instituição privada.
- **convenio:** existência e tipo de convênio com o poder público.
- **localizacao:** localização da instituição (Urbana ou Rural).
""")

st.header("Como utilizar o painel?")

st.markdown("""
# 1. Consulta por ano
Selecione um ano para visualizar a quantidade de instituições
e matrículas na Educação Infantil.

# 2. Consulta avançada
Escolha o tipo de consulta, o segmento da Educação Infantil,
a dependência administrativa e a categoria da escola privada.

# 3. Filtros
Utilize os filtros da barra lateral para selecionar períodos,
dependências administrativas, categorias e localizações.

# 4. Buscar instituição
Digite o nome ou parte do nome de uma instituição para
consultar suas informações e sua trajetória de matrículas.
""")

st.divider()

st.subheader("Matrículas")

st.markdown("""
- **matriculas_creche:** quantidade de matrículas em creche.
- **matriculas_pre:** quantidade de matrículas em pré-escola.
- **total_ei:** total de matrículas na Educação Infantil.
""")

st.caption(FONTE)