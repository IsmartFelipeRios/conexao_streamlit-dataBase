import streamlit as st
import pyodbc
import pandas as pd

# Initialize connection.
# Uses st.cache_resource to only run once.
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

conn = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

Query = st.text_input('SQL query')

if Query:
    rows = run_query(Query)

    # Print results.
    try:
        df = pd.read_sql_table(rows)
        st.dataframe(df)
        st.write('Leitura com read_sql_table funcionou')
    except:
        st.error('Leitura com read_sql_table não funcionou')
    try:
        df = pd.read_sql(rows)
        st.dataframe(df)
        st.write('Leitura com read_sql funcionou') 
    except:
        st.error('Leitura com read_sql não funcionou')
    try:
        df = pd.read_sql_query(rows)
        st.dataframe(df)
        st.write('Leitura com read_sql_query funcionou') 
    except:
        st.write('Leitura com read_sql_query Não funcionou')

else: st.warning('Coloque a query na caixa')


    