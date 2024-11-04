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
consultaSQL = "SELECT TOP 10 Nome, RA, Projeto FROM dbo.Aluno WHERE Projeto LIKE 'Ensino Superior'"

# Função para converter a query em um arquivo Parquet usando Streamlit connection
def query_to_parquet(query, connection_name, file_name="resultado.parquet"):
    try:
        # Conectar ao banco de dados usando a conexão do Streamlit
        conn = st.connection(connection_name, type="sql")

        # Executar a consulta e armazenar o resultado em um DataFrame
        df = conn.query(query)

        # Salvar o DataFrame como arquivo parquet
        df.to_parquet(file_name, index=False)
        st.success(f"Arquivo salvo como {file_name}")

        return file_name

    except Exception as e:
        st.error(f"Erro ao executar a consulta: {e}")
        return None

# Lógica para o botão "Atualizar"
if st.button("Atualizar"):
    if usuario_sql and senha_sql and github_token:
        # Criar uma conexão SQL usando o nome "db_connection" definido em secrets
        file_path = query_to_parquet(consultaSQL, "db_connection")

        if file_path:
            try:
                # Conectar ao GitHub e ao repositório
                g = Github(github_token)
                repo = g.get_repo("IsmartFelipeRios/conexao_streamlit-dataBase")

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
                    st.balloons()

                except:
                    repo.create_file(repo_path, "Criando o arquivo parquet", content)
                    st.success("Arquivo criado com sucesso!")
                    st.balloons()

            except Exception as e:
                st.error(f"Erro ao conectar ao GitHub: {e}")
    else:
        st.warning("Por favor, preencha todos os campos antes de atualizar.")
