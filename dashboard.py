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

@st.cache_resource(ttl=3600)
def init_connection(_cred): # <-- MUDANÇA AQUI
    """Inicializa a conexão com o banco de dados. Fica em cache por 1 hora."""
    if not _cred: # <-- MUDANÇA AQUI
        st.error("Credencial do Azure não está disponível. Conexão abortada.")
        return None

    # 1. Atualiza o firewall
    if not update_firewall(_cred): # <-- MUDANÇA AQUI
        st.warning("A atualização do firewall falhou. A conexão pode não funcionar se o IP não estiver permitido.")
    
    # 2. Obtém o token de acesso para o banco de dados
    try:
        token_credential = _cred.get_token("https://database.windows.net/.default") # <-- MUDANÇA AQUI
        access_token = token_credential.token
    except Exception as e:
        st.error(f"Erro ao obter token de acesso: {e}")
        return None

    # 3. Conecta-se ao banco de dados
    try:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={st.secrets['SQL_SERVER_NAME']}.database.windows.net;"
            f"DATABASE={st.secrets['SQL_DATABASE_NAME']};"
            "LoginTimeout=30;"
        )
        
        conn = pyodbc.connect(
            conn_str,
            attrs_before={1256: bytes(access_token, "utf-16-le")}
        )
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar com pyodbc: {e}")
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
