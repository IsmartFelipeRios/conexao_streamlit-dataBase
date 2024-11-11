import streamlit as st
import pyodbc
import pandas as pd

def make_df(query, cache_duration_seconds=14400, Entries_max=1000):
    @st.cache_resource(ttl=cache_duration_seconds, max_entries=Entries_max)
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

    @st.cache_data(ttl=cache_duration_seconds, max_entries=Entries_max, experimental_allow_widgets=True)
    def run_query(query):
        try:
            conn = init_connection()
        except Exception as e:
            st.error(f'Erro ao conectar: {e}')
        try:
            df = pd.read_sql_query(query, conn)
        except Exception as e:
            st.error(f'Erro com a query: {e}')
            st.write("Deseja limpar o cache e recarregar?")
            if st.button("Sim"):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("Cache limpo!")
                st.rerun()
        return df
    return run_query(query)
