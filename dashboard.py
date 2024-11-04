import streamlit as st
import pandas as pd
from github import Github
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Título da aplicação
st.title("Atualizar DF")

# Entradas de usuário para autenticação
usuario_sql = st.text_input("Usuário SQL")
senha_sql = st.text_input("Senha SQL", type="password")
github_token = st.text_input("Token GitHub", type="password")

# Função para converter a query em um arquivo Parquet
def query_to_parquet(query, usuario, senha, file_name="resultado.parquet"):
    try:
        # String de conexão usando SQLAlchemy e pyodbc com ODBC Driver 17
        connection_string = f'mssql+pyodbc://{usuario}:{senha}@ismart-server.database.windows.net:1433/ismart-db?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(connection_string, connect_args={"timeout": 30})

        # Executar a consulta e armazenar o resultado em um DataFrame
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)

        # Salvar o DataFrame como arquivo parquet
        df.to_parquet(file_name, index=False)
        st.success(f"Arquivo salvo como {file_name}")

        return file_name

    except OperationalError as e:
        st.error("Erro ao conectar ao banco de dados. Verifique as credenciais e tente novamente.")
        st.error(f"Detalhes do erro: {e}")
        return None
    except Exception as e:
        st.error(f"Erro ao executar a consulta: {e}")
        return None

# Consulta SQL
consultaSQL = "SELECT TOP 11 Nome, RA, Projeto FROM dbo.Aluno WHERE Projeto LIKE 'Ensino Superior'"

# Lógica para o botão "Atualizar"
if st.button("Atualizar"):
    if usuario_sql and senha_sql and github_token:
        file_path = query_to_parquet(consultaSQL, usuario_sql, senha_sql)

        if file_path:
            try:
                # Conectar ao GitHub e ao repositório
                g = Github(github_token)
                repo = g.get_repo("IsmartFelipeRios/conex-o_banco_de_dados_para_streamlit")

                # Caminho no repositório e mensagem de commit
                repo_path = "resultado.parquet"  # Caminho do arquivo no repositório

                # Ler o arquivo parquet em modo binário
                with open(file_path, "rb") as file:
                    content = file.read()

                # Cria ou atualiza o arquivo no repositório
                try:
                    contents = repo.get_contents(repo_path)
                    repo.update_file(contents.path, "Atualizando o arquivo parquet", content, contents.sha)
                    st.success("Arquivo atualizado com sucesso!")
                except:
                    repo.create_file(repo_path, "Criando o arquivo parquet", content)
                    st.success("Arquivo criado com sucesso!")

            except Exception as e:
                st.error(f"Erro ao conectar ao GitHub: {e}")
    else:
        st.warning("Por favor, preencha todos os campos antes de atualizar.")
