import streamlit as st
import pyodbc
import pandas as pd

def make_df(query):
    @st.cache_resource(ttl=86400)
    def init_connection():
        return pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
            + st.secrets["server"]
            + ";DATABASE="
            + st.secrets["database"]
            + ";UID="
            + st.secrets["username"]
            + ";PWD="
            + st.secrets["password"]
        )

    @st.cache_data(ttl=86400)
    def run_query(query):
        try:
            conn = init_connection()
        except Exception as e:
            st.error(f'Erro ao conectar: {e}')

        df = pd.read_sql_query(query, conn)
        return df
    return run_query(query)

query = st.text_input('SQL query')

if query:
    try:
        df = make_df(query)
    except Exception as e:
        st.error(f'Erro com a query: {e}')
    
    # Print results.
    st.dataframe(df)

else: st.warning('Coloque a query na caixa')

st.button("rerun")
if st.button("Clean Cach",):
    st.cache_resource.clear()