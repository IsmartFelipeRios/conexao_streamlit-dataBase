import streamlit as st
import pyodbc
import pandas as pd


@st.cache_resource
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

try:
    conn = init_connection()
except Exception as e:
    st.error(f'Erro ao conectar: {e}')

@st.cache_data()
def run_query(query):
    df = pd.read_sql_query(query, conn)
    return df

query = st.text_input('SQL query')

if query:
    try:
        df = run_query(query)
    except Exception as e:
        st.error(f'Erro com a query: {e}')
    
    # Print results.
    st.dataframe(df)

else: st.warning('Coloque a query na caixa')


    