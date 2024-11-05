
## conexao banco streamlit com cash

import streamlit as st
import pyodbc
#import pandas as pd

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

rows = run_query("SELECT TOP 10 Nome, RA, Projeto FROM dbo.Aluno WHERE Projeto LIKE 'Ensino Superior'")

# Print results.



for row in rows:
    st.write(f"{row[0]} has a :{row[1]}:")


## código antigo

# import streamlit as st
# import pyodbc
# import pandas as pd
# from github import Github


# # Título da aplicação
# st.title("Atualizar DF")

# # Entradas de usuário para autenticação
# usuario_sql = st.text_input("Usuário SQL")
# senha_sql = st.text_input("Senha SQL", type="password")
# github_token = st.text_input("Token GitHub", type="password")

# # Função para converter a query em um arquivo Parquet
# def query_to_parquet(query, usuario, senha, file_name="resultado.parquet"):
#     try:
#         # String de conexão usando as entradas do usuário
#         connection_string = f'Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:ismart-server.database.windows.net,1433;Database=ismart-db;Uid={usuario};Pwd={senha};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        
#         # Conectar ao banco de dados
#         conn = pyodbc.connect(connection_string)
        
#         # Executar a consulta e armazenar o resultado em um DataFrame
#         df = pd.read_sql_query(query, conn)
        
#         # Salvar o DataFrame como arquivo parquet
#         df.to_parquet(file_name, index=False)
#         st.success(f"Arquivo salvo como {file_name}")
        
#         # Fechar a conexão
#         conn.close()
        
#         return file_name
        
#     except Exception as e:
#         st.error(f"Erro ao executar a consulta: {e}")
#         return None

# # Consulta SQL
# consultaSQL = "SELECT TOP 11 Nome, RA, Projeto FROM dbo.Aluno WHERE Projeto LIKE 'Ensino Superior'"

# def upload_github():
#     if usuario_sql and senha_sql and github_token:
#         file_path = query_to_parquet(consultaSQL, usuario_sql, senha_sql)
#         if file_path:
#             try:
#                 # Conectar ao GitHub e ao repositório
#                 g = Github(github_token)
#                 repo = g.get_repo("IsmartFelipeRios/conexao_streamlit-dataBase")
                
#                 # Caminho no repositório e mensagem de commit
#                 repo_path = "resultado.parquet"  
                
#                 # Ler o arquivo parquet em modo binário
#                 with open(file_path, "rb") as file:
#                     content = file.read()
                
#                 # Cria ou atualiza o arquivo no repositório
#                 try:
#                     contents = repo.get_contents(repo_path)
#                     repo.update_file(contents.path, "Atualizando o arquivo parquet", content, contents.sha)
#                     st.success("Arquivo atualizado com sucesso!")
#                     st.balloons()
#                 except:
#                     repo.create_file(repo_path, "Criando o arquivo parquet", content)
#                     st.success("Arquivo criado com sucesso!")
#                     st.balloons()
#             except Exception as e:
#                 st.error(f"Erro ao conectar ao GitHub: {e}")
#     else:
#         st.warning("Por favor, preencha todos os campos antes de atualizar.")

# # Lógica para o botão "Atualizar"
# if st.button("Atualizar"):
#     upload_github()