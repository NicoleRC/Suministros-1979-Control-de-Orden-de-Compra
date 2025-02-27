import streamlit as st
import pyodbc
from credenciales import conexion
from datetime import datetime



# Parámetros para la conexión
conn = conexion()
cursor = conn.cursor()
def plantilla():
    try:
        cursor.execute("""
        SELECT [c_descripcio] FROM [VAD10_SCORP].[dbo].[MA_PROVEEDORES] ORDER BY [c_descripcio] ASC
        """)
        proveedores = [row[0] for row in cursor.fetchall()]
        
        return proveedores
    except Exception as e:
        print(f"Error en la consulta SQL: {e}")
        return "Error al obtener proveedores"

st.title("CONTROL ÓRDENES DE COMPRA")

proveedores = plantilla()

st.selectbox("Lista de proveedores:", proveedores)

col1, col2 = st.columns(2)
with col1:
    inicial_fecha = st.write("Filtrar por fecha")
with col2:
    final_fecha = st.write("HOLA")

col1, col2 = st.columns(2)
with col1:
    inicial_fecha = st.date_input("Fecha inicial:", datetime.today())
with col2:
    final_fecha = st.date_input("Fecha final:", datetime.today())
    subcol1, subcol2 = st.columns(2)
    with subcol1:
        st.write("HOLA")
    with subcol2:
        st.write("HOLA")

col1, col2, col3, col = st.columns(4)