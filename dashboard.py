import streamlit as st
import pyodbc
import pandas as pd
import requests
from azure.identity import ClientSecretCredential
from azure.mgmt.sql import SqlManagementClient

# -- Autenticação e Configuração Inicial --
# O st.cache_resource garante que isso só rode uma vez por sessão.
@st.cache_resource
def get_azure_credential():
    """Obtém a credencial do Azure a partir dos segredos."""
    try:
        return ClientSecretCredential(
            tenant_id=st.secrets["AZURE_TENANT_ID"],
            client_id=st.secrets["AZURE_CLIENT_ID"],
            client_secret=st.secrets["AZURE_CLIENT_SECRET"],
        )
    except Exception as e:
        st.error(f"Erro ao criar credencial do Azure: {e}")
        return None

credential = get_azure_credential()

# -- Funções de Conexão com o Banco de Dados --
def get_public_ip():
    """Obtém o IP público da instância do Streamlit."""
    try:
        return requests.get("https://api.ipify.org").text
    except Exception as e:
        st.error(f"Erro ao obter IP público: {e}")
        return None

def update_firewall(cred):
    """Atualiza a regra de firewall do Azure SQL para permitir o acesso do IP atual."""
    if not cred:
        return False
    try:
        ip = get_public_ip()
        if not ip:
            return False

        sql_client = SqlManagementClient(
            credential=cred,
            subscription_id=st.secrets["AZURE_SUBSCRIPTION_ID"]
        )

        # Cria ou atualiza a regra de firewall
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
        st.success(f"Regra de firewall atualizada para o IP: {ip}")
        return True
    except Exception as e:
        # Mostra o erro de autorização de forma clara
        st.error(f"Erro ao atualizar regra de firewall: {e}")
        return False

# Substitua sua função init_connection por esta versão de TESTE
@st.cache_resource(ttl=3600)
def init_connection(_cred): # Mantemos _cred para não quebrar a chamada, mas não o usamos
    """TENTA CONECTAR USANDO USUÁRIO E SENHA SQL PARA TESTE."""

    # A atualização do firewall ainda é necessária e usa o Service Principal
    if not update_firewall(_cred):
        st.warning("A atualização do firewall falhou. A conexão pode não funcionar.")

    try:
        # Nova string de conexão, usando UID (User ID) e PWD (Password)
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={st.secrets['SQL_SERVER_NAME']}.database.windows.net;"
            f"DATABASE={st.secrets['SQL_DATABASE_NAME']};"
            f"UID={st.secrets['SQL_TEST_USER']};"
            f"PWD={st.secrets['SQL_TEST_PASSWORD']};"
            "LoginTimeout=30;"
        )
        
        # Conexão direta, sem o 'attrs_before' do token
        conn = pyodbc.connect(conn_str)
        
        # Se chegar aqui, a conexão funcionou!
        st.success("SUCESSO! A conexão com usuário e senha SQL funcionou!")
        return conn

    except Exception as e:
        st.error(f"Erro no teste de conexão com usuário/senha: {e}")
        return None
    
@st.cache_data(ttl=600)
def run_query(query: str):
    """Executa uma query e retorna um DataFrame. Fica em cache por 10 minutos."""
    try:
        conn = init_connection(credential)
        if conn:
            df = pd.read_sql(query, conn)
            return df
        else:
            st.error("A conexão com o banco de dados não pôde ser estabelecida.")
            return pd.DataFrame() # Retorna um DataFrame vazio em caso de falha
    except Exception as e:
        st.error(f"Erro ao executar a query: {e}")
        return pd.DataFrame()

# -- Interface do Usuário no Streamlit --
st.title("Conector de Banco de Dados Azure SQL")

query = st.text_area("Digite sua query SQL aqui:")

if st.button("Executar Query"):
    if query:
        with st.spinner("Executando query..."):
            result_df = run_query(query)
            if not result_df.empty:
                st.dataframe(result_df)
    else:
        st.warning("Por favor, digite uma query.")
