import pyodbc
from azure import identity
import struct
import pandas as pd

connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:ismart-sql-server.database.windows.net,1433;Database=ismart-sql-db;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

def get_conn():
    credential = identity.DefaultAzureCredential(
        exclude_interactive_browser_credential=False
    )
    token_bytes = credential.get_token(
        "https://database.windows.net/.default"
    ).token.encode("UTF-16-LE")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    conn = pyodbc.connect(
        connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}
    )
    return conn

def test_connection():
    try:
        conn = get_conn()
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        conn.close()
        
        if result and result[0] == 1:
            print("Connection successful!")
            return True
        else:
            print("Connection failed!")
            return False
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

test_connection()
