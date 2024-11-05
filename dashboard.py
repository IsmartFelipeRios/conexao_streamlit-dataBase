import streamlit as st
import pyodbc
import pandas as pd

@st.cache_data()
def run_query(query):
    # Conexão e execução da query em uma única função
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
            + st.secrets["server"]
            + ";DATABASE="
            + st.secrets["database"]
            + ";UID="
            + st.secrets["username"]
            + ";PWD="
            + st.secrets["password"]
        )
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f'Erro ao conectar ou executar a query: {e}')
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

query = st.text_input('SQL query')

if query:
    df = run_query(query)
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning('A consulta não retornou resultados.')
else:
    st.warning('Coloque a query na caixa')

st.button("Rerun")