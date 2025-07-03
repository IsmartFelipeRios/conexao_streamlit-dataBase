# Projeto: Conector Streamlit para Azure SQL

## 1. Visão Geral do Projeto

Esta aplicação Streamlit foi desenvolvida para conectar-se de forma segura a um Banco de Dados SQL no Azure. O objetivo é permitir que usuários executem queries SQL diretamente pela interface web e visualizem os resultados.

A arquitetura utiliza as melhores práticas de segurança da Microsoft, autenticando a aplicação através de um **Principal de Serviço (Service Principal)** do Microsoft Entra ID, evitando o uso de senhas de banco de dados no código.

---

## 2. O Ponto de Partida

Este documento serve como um guia para continuar o desenvolvimento a partir do ponto em que ele foi pausado (Julho de 2025). O código no repositório está em um estado funcional, mas a configuração do ambiente no Azure está incompleta.

O guia a seguir irá levá-lo passo a passo através da configuração, fazendo você encontrar os mesmos erros que foram encontrados durante o desenvolvimento inicial. Isso garantirá que você entenda a razão por trás de cada etapa de configuração.

**Seu objetivo é seguir este guia até o final para fazer a aplicação funcionar.**

---

## 3. Guia de Configuração e Diagnóstico

### Passo 1: Configuração Inicial do Ambiente

Antes de tudo, vamos preparar seu ambiente local e conectar com os segredos do Azure.

1.  **Clone o Repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO]
    cd [NOME_DA_PASTA_DO_PROJETO]
    ```

2.  **Crie e Ative um Ambiente Virtual Python:**
    ```bash
    # Crie o ambiente
    python -m venv venv
    # Ative o ambiente (Windows)
    venv\Scripts\activate
    # Ative o ambiente (macOS/Linux)
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure os Segredos:** Crie uma pasta `.streamlit` e, dentro dela, um arquivo `secrets.toml`. Preencha-o com as credenciais corretas do Azure. **É crucial que estes valores sejam verificados no Portal do Azure.**

    ```toml
    # .streamlit/secrets.toml

    # Credenciais do Service Principal
    AZURE_CLIENT_ID = "COLE_O_ID_DO_CLIENTE_AQUI"
    AZURE_TENANT_ID = "COLE_O_ID_DO_DIRETORIO_AQUI"
    AZURE_CLIENT_SECRET = "COLE_O_SEGREDO_DO_CLIENTE_AQUI"

    # Detalhes da Subscrição e Recursos do Azure
    AZURE_SUBSCRIPTION_ID = "COLE_O_ID_DA_ASSINATURA_AQUI"
    RESOURCE_GROUP_NAME = "IsmartDataBase"
    SQL_SERVER_NAME = "ismart-sql-server" # Apenas o nome curto!
    SQL_DATABASE_NAME = "dev-ismart-sql-db" # Nome exato do banco de dados
    ```

### Passo 2: Primeira Execução e o Erro de Autorização (`AuthorizationFailed`)

Agora que tudo está configurado, vamos rodar a aplicação pela primeira vez.

```bash
streamlit run dashboard.py
```

A aplicação irá carregar, mas ao tentar executar uma query, você deve encontrar um erro nos logs do Streamlit parecido com este:

> `Erro ao atualizar regra de firewall: (AuthorizationFailed) The client '...' does not have authorization to perform action 'Microsoft.Sql/servers/firewallRules/write'...`

**Diagnóstico:** Este erro é esperado. Ele nos diz que o nosso Service Principal, embora válido, não tem permissão para gerenciar o firewall do Servidor SQL.

**Solução:**
1.  Vá para o **Portal do Azure** e navegue até o servidor SQL `ismart-sql-server`.
2.  No menu esquerdo, vá para **Controle de Acesso (IAM)**.
3.  Clique em **+ Adicionar** -> **Adicionar atribuição de função**.
4.  Selecione a função **"Colaborador do SQL Server" (SQL Server Contributor)**.
5.  Na aba "Membros", procure e adicione o Service Principal correspondente ao `AZURE_CLIENT_ID` dos seus segredos.
6.  Salve a atribuição de função.

### Passo 3: Segunda Execução e o Erro do `pyodbc` (`08S01`)

Depois de conceder a permissão de firewall, aguarde alguns minutos e reinicie a aplicação Streamlit (`Ctrl+C` no terminal e rode `streamlit run app.py` novamente).

Tente executar a query. O erro de autorização deve ter desaparecido, e a mensagem "Regra de firewall atualizada" deve aparecer. No entanto, um novo erro surgirá:

> `Erro ao conectar com pyodbc: ('08S01', '[08S01] [Microsoft][ODBC Driver 17 for SQL Server]TCP Provider: Error code 0x68 (104) (SQLDriverConnect)')`

**Diagnóstico:** Este é o erro de **"Connection reset by peer"**. Ele indica que chegamos com sucesso até o servidor, mas ele ativamente recusou nossa conexão. A causa mais comum neste cenário é que o Service Principal tem permissão no *servidor*, mas ainda não existe como um *usuário* **dentro do banco de dados**.

**Solução:** Precisamos criar um usuário no banco de dados para o nosso Service Principal.

1.  Vá para o **Portal do Azure**, navegue até o banco de dados `dev-ismart-sql-db` e abra o **Editor de Consultas**.
2.  Faça login com uma conta administrativa (ex: `admin_TechWise@ismart.org.br`).
3.  Tente executar o seguinte comando SQL (substituindo `[NomeDeExibicaoDoServicePrincipal]` pelo nome correto):

    ```sql
    CREATE USER [NomeDeExibicaoDoServicePrincipal] FROM EXTERNAL PROVIDER;
    ALTER ROLE db_datareader ADD MEMBER [NomeDeExibicaoDoServicePrincipal];
    ```

### Passo 4: Onde Paramos - O Erro Final de Permissão SQL

Ao tentar executar o comando do Passo 3, você encontrará o erro final, que é exatamente o ponto onde o desenvolvimento parou:

> `Msg 15151, Level 16, State 2, Line 4`
> `Cannot alter the role 'db_datareader', because it does not exist or you do not have permission.`

**Diagnóstico Final:** A conta que estamos usando para administrar (`admin_TechWise@ismart.org.br`) **não tem permissão para gerenciar outras funções e usuários dentro do banco de dados**. Chegamos a um problema de permissão na conta do administrador.

---

## 4. Conclusão e Próximos Passos (Sua Missão)

Você chegou exatamente ao ponto em que o projeto precisa de sua ajuda. Para finalizar a configuração e fazer a aplicação funcionar, você precisa resolver este último problema de permissão.

**Ação Necessária:**

1.  **Peça ao Administrador principal da Assinatura Azure** (ou quem criou o servidor SQL originalmente) para executar o seguinte comando SQL. Ele deve se conectar ao banco `dev-ismart-sql-db` com a conta de "Administrador do Servidor SQL" original:

    ```sql
    -- Este comando dará à sua conta admin os poderes de dono do banco.
    ALTER ROLE db_owner ADD MEMBER [admin_TechWise@ismart.org.br];
    ```

2.  **Depois que o passo acima for concluído**, faça login no Editor de Consultas com a sua conta `admin_TechWise@ismart.org.br`. Agora ela terá as permissões necessárias. Execute o comando que estava falhando antes:

    ```sql
    -- Este comando dará ao seu aplicativo a permissão de leitura de dados.
    -- (Verifique se o usuário já não foi criado na tentativa anterior)
    IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'NomeDeExibicaoDoServicePrincipal')
    BEGIN
        CREATE USER [NomeDeExibicaoDoServicePrincipal] FROM EXTERNAL PROVIDER;
    END

    ALTER ROLE db_datareader ADD MEMBER [NomeDeExibicaoDoServicePrincipal];
    ```

Após a execução bem-sucedida desses comandos, todos os bloqueios de permissão terão sido resolvidos. **Reinicie a aplicação Streamlit uma última vez, e a conexão com o banco de dados deverá funcionar completamente.**

Boa sorte!
