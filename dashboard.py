import streamlit as st
import pandas as pd
from github import Github

# Título da aplicação
st.title("Atualizar DF")

# Entradas de usuário para autenticação
usuario_sql = st.text_input("Usuário SQL")
senha_sql = st.text_input("Senha SQL", type="password")
github_token = st.text_input("Token GitHub", type="password")

# Consulta SQL
consultaSQL = "SELECT TOP 11 Nome, RA, Projeto FROM dbo.Aluno WHERE Projeto LIKE 'Ensino Superior'"

# Lógica para o botão "Atualizar"
if st.button("Atualizar"):
    if usuario_sql and senha_sql and github_token:
        try:
            # Conectar ao banco de dados usando o Streamlit SQL connection
            conn = st.connection(
                "db_connection",
                type="sql",
                url=f"mssql+pyodbc://{usuario_sql}:{senha_sql}@ismart-server.database.windows.net:1433/ismart-db?driver=ODBC+Driver+17+for+SQL+Server"
            )
            df = conn.query(consultaSQL)

            # Salvar o DataFrame como arquivo parquet
            file_path = "resultado.parquet"
            df.to_parquet(file_path, index=False)
            st.success(f"Arquivo salvo como {file_path}")

            # Conectar ao GitHub e ao repositório
            try:
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

        except Exception as e:
            st.error(f"Erro ao executar a consulta: {e}")

    else:
        st.warning("Por favor, preencha todos os campos antes de atualizar.")
