from sqlalchemy import create_engine
import streamlit as st
import pandas as pd

def conexion():
    try:
        server = st.secrets['sql_server']['server']
        port = st.secrets['sql_server'].get('port', 1433) # Obtener el puerto, o usar 1433 por defecto
        database = st.secrets['sql_server']['database']
        uid = st.secrets['sql_server']['uid']
        pwd = st.secrets['sql_server']['pwd']

        engine = create_engine(
            f"mssql+pymssql://{uid}:{pwd}@{server}:{port}/{database}"
        )
        return engine
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None