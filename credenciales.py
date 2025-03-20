import pyodbc
import streamlit as st

def conexion():
    try:
        conn = pyodbc.connect(
            f"DRIVER={st.secrets['sql_server']['driver']};"
            f"SERVER={st.secrets['sql_server']['server']};"
            f"DATABASE={st.secrets['sql_server']['database']};"
            f"UID={st.secrets['sql_server']['uid']};"
            f"PWD={st.secrets['sql_server']['pwd']};"
        )
        return conn
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None
    
