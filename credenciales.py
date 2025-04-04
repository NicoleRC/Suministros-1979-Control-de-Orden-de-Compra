from sqlalchemy import create_engine
import streamlit as st
import pandas as pd

def conexion():
    try:
        engine = create_engine(
            f"mssql+pymssql://{st.secrets['sql_server']['uid']}:{st.secrets['sql_server']['pwd']}@{st.secrets['sql_server']['server']}/{st.secrets['sql_server']['database']}"
        )
        return engine
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None
