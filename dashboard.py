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
    df = pd.read_sql_query(query, conn)
    return df
query = st.text_input('SQL query')

if query:
    df = run_query(query)

    # Print results.
    try:
        st.dataframe(df)
        
    except:
        st.error('Leitura com read_sql_table não funcionou')

else: st.warning('Coloque a query na caixa')


    