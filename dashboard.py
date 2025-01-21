import streamlit as st
import pyodbc
import pandas as pd
import requests
from azure.identity import ClientSecretCredential
from azure.mgmt.sql import SqlManagementClient


credential = ClientSecretCredential(
    tenant_id=st.secrets["AZURE_TENANT_ID"],
    client_id=st.secrets["AZURE_CLIENT_ID"],
    client_secret=st.secrets["AZURE_CLIENT_SECRET"],
)

token = credential.get_token("https://database.windows.net/.default")

access_token = token.token


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except Exception as e:
        st.error(f"Erro ao obter IP público: {e}")
        return None

def update_firewall():
    try:
        ip = get_public_ip()
        if not ip:
            return False
        
        sql_client = SqlManagementClient(
            credential=credential,
            subscription_id=st.secrets["AZURE_SUBSCRIPTION_ID"]
        )
        
        # Create or update firewall rule
        sql_client.firewall_rules.create_or_update(
            resource_group_name=st.secrets["RESOURCE_GROUP_NAME"],
            server_name=st.secrets["SQL_SERVER_NAME"],
            firewall_rule_name="StreamlitAppRule",
            parameters={
                "properties": {
                    "startIpAddress": ip,
                    "endIpAddress": ip
                }
            }
        )
        st.success(f"Regra de firewall atualizada para IP: {ip}")
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar regra de firewall: {e}")
        return False

def make_df(query, cache_duration_seconds=14400, Entries_max=1000):

    @st.cache_resource(ttl=cache_duration_seconds, max_entries=Entries_max)
    def init_connection():

        # Try to update firewall before connecting
        update_firewall()

        return pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={st.secrets['SQL_SERVER_NAME']};"
            f"DATABASE={st.secrets['RESOURCE_GROUP_NAME']};"
            "Trusted_Connection=No;",
            attrs_before={1256: access_token.encode("utf-16-le")},
        )

    @st.cache_data(ttl=cache_duration_seconds,max_entries=Entries_max,experimental_allow_widgets=True,)
    def run_query(query):

        try:

            conn = init_connection()

        except Exception as e:

            st.error(f"Erro ao conectar: {e}")

        try:

            df = pd.read_sql_query(query, conn)

        except Exception as e:

            st.error(f"Erro com a query: {e}")

            st.write("Deseja limpar o cache e recarregar?")

            if st.button("Sim"):

                st.cache_data.clear()

                st.cache_resource.clear()

                st.success("Cache limpo!")

                st.rerun()

        return df

    return run_query(query)

query = st.text_input(label='Query')
make_df(query)