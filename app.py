import streamlit as st
import pyodbc
import pandas as pd
from credenciales import conexion
from datetime import datetime
import time

# Ajustes de estilo para Streamlit
css_Margenes = """
    <style>
        .block-container {
            padding-top: 1cm;
            margin: 0;
            max-width: 100%;
            padding-left: 2cm;
            padding-right: 2cm;
        }
    </style>
"""
st.markdown(css_Margenes, unsafe_allow_html=True)

# Conexión a la base de datos
conn = conexion()
cursor = conn.cursor()

def plantilla():
    try:
        cursor.execute("""
            SELECT DISTINCT [c_DESCRIPCION] 
            FROM [VAD10_SCORP].[dbo].[MA_ODC] 
            ORDER BY [c_DESCRIPCION] ASC
        """)
        proveedores = [row[0] for row in cursor.fetchall()]
        return proveedores
    except Exception as e:
        st.write(f"Error en la consulta SQL: {e}")
        return []

# Verificar si hay que limpiar la sesión
if "limpiar" in st.session_state and st.session_state["limpiar"]:
    st.session_state.clear()  # Limpia todos los estados
    st.rerun()  # Recarga la página

# Inicializar estado
if "Lista_Proveedores" not in st.session_state:
    st.session_state["Lista_Proveedores"] = "Seleccione el proveedor"
if "filtro" not in st.session_state:
    st.session_state["filtro"] = "Seleccione una opción"
if "fecha_inicial" not in st.session_state:
    st.session_state["fecha_inicial"] = None
if "fecha_final" not in st.session_state:
    st.session_state["fecha_final"] = None
if "mes_filtro" not in st.session_state:
    st.session_state["mes_filtro"] = "Seleccione mes"

# Ruta de la imagen
ruta_imagen = "images/Suministros Logo.png"

# Mostrar la imagen
st.image(ruta_imagen, caption=" ", width=200)
st.title(" CONTROL DE ÓRDENES DE COMPRA")

proveedores = plantilla()

# Selección de proveedor
col1, col2 = st.columns(2)
with col1:
    Lista = st.selectbox(
        "Lista de Proveedores",
        ["Seleccione el proveedor"] + proveedores,
        key="Lista_Proveedores"
    )

# Selección de filtro por fechas
with col2:
    filtro = st.selectbox(
        "Filtrar por:",
        ["Seleccione una opción", "Rango de fechas", "Mes"],
        key="filtro"
    )

# Crear columnas de fecha y mes
col1, col2, col3, col4, col5, col6 = st.columns(6)
fecha_inicial = None
fecha_final = None
if filtro == "Rango de fechas":
    with col4:
        fecha_inicial = st.date_input("Fecha Inicial:")
    with col5:
        fecha_final = st.date_input("Fecha Final:")

# Botones de acción
col1, col2, col3, col4 = st.columns(4)
with col2:
    buscar = st.button("Buscar ODC")
with col4:
    limpiar = st.button("Limpiar Campos")

# Ejecución de la búsqueda
if buscar:
    try:
        # Construir la consulta dinámica
        consulta_datos = "SELECT [c_DOCUMENTO] FROM [VAD10_SCORP].[dbo].[MA_ODC] WHERE 1=1"
        if Lista != "Seleccione el proveedor":
            consulta_datos += f" AND [c_DESCRIPCION] = '{Lista}'"
        if filtro == "Rango de fechas" and fecha_inicial and fecha_final:
            consulta_datos += f" AND [d_FECHA] BETWEEN '{fecha_inicial}' AND '{fecha_final}'"

        st.divider()

        # Ejecutar la consulta SQL
        df = pd.read_sql(consulta_datos, conn)

        # Mostrar resultados como botones en filas y columnas ajustadas automáticamente
        if not df.empty:
            cols = st.columns(min(len(df), 6))  # Ajustar a un máximo de 6 columnas
            for index, row in df.iterrows():
                c_documento = row['c_DOCUMENTO']
                col_idx = index % len(cols)  # Ciclar entre las columnas
                with cols[col_idx]:
                    if st.button(str(c_documento)):
                        st.write(f"Has seleccionado el documento: {c_documento}")
        else:
            st.warning("No se encontraron documentos para los filtros seleccionados.")
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")

# Botón para limpiar la sesión
if limpiar:
    st.session_state.clear()
    st.rerun()  # Recargar la página

# Cerrar la conexión
conn.close()

