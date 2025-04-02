import streamlit as st
import pandas as pd
from datetime import datetime
from credenciales import conexion
import io

# Conexión a la base de datos
engine = conexion()

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

# Función para obtener proveedores
def plantilla():
    try:
        query = """
            SELECT DISTINCT [c_DESCRIPCION] 
            FROM [VAD10_SCORP].[dbo].[MA_ODC] 
            ORDER BY [c_DESCRIPCION] ASC
        """
        df = pd.read_sql(query, engine)
        return df['c_DESCRIPCION'].to_list()
    except Exception as e:
        st.error(f"Error en la consulta SQL: {e}")
        return []

# Función para obtener órdenes de un proveedor
def ordenes(proveedor):
    if not proveedor:
        return []
    try:
        query = f"""
            SELECT DISTINCT FLOOR(CONVERT(DECIMAL, [ODCDOC])) AS [ODCDOC] 
            FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] 
            WHERE [PROV] = '{proveedor}' 
            ORDER BY FLOOR(CONVERT(DECIMAL, [ODCDOC])) DESC
        """
        df = pd.read_sql(query, engine)
        df['ODCDOC'] = round(df['ODCDOC'], 0)
        return df['ODCDOC'].to_list()
    except Exception as e:
        st.error(f"Error en la consulta SQL: {e}")
        return []

# Función para mostrar detalle de una orden
def detalle(odc):
    try:
        query = f"""
            SELECT [FECHAODC] AS [Fecha ODC],
                [Barra] AS [SKU],
                [Producto] AS [Descripción de Producto],
                [CantODC] AS [Cant ODC],
                [RECDOC] AS [Nº REC],
                [FECHAREC] AS [Fecha RECEP],
                [CantREC] AS[Cant REC],
                [FALTANTE] AS [Cant Faltante]
            FROM [VAD10_SCORP].[dbo].[REP_ODCxREC]
            WHERE [ODCDOC] = '{odc}' ORDER BY [Nº REC] ASC
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error en la consulta SQL: {e}")
        return []

# Ruta de la imagen
st.image("images/Suministros Logo.png", caption=" ", width=200)
st.title("CONTROL DE ÓRDENES DE COMPRA")

# Lista de proveedores
proveedores = plantilla()

# Selección de proveedor
col1, col2 = st.columns(2)
with col1:
    proveedor = st.selectbox(
        "Lista de Proveedores:",
        proveedores,
        key="Lista_Proveedores",
        index=None,
        placeholder="Selecciona un proveedor"
    )

# Mostrar órdenes solo si se seleccionó un proveedor
if proveedor:
    ordenes_lista = ordenes(proveedor)

    if ordenes_lista:
        st.markdown("### Selecciona una orden de compra:")
        cols = st.columns(6)

        for index, documento in enumerate(ordenes_lista):
            col = cols[index % 6]
            with col:
                if st.button(str(documento), key=f"doc_{documento}"):
                    st.session_state["documento_seleccionado"] = documento
                    st.rerun()

        # Mostrar mensaje de selección
        if "documento_seleccionado" in st.session_state:
            st.success(f'Has seleccionado la nota: {st.session_state["documento_seleccionado"]}')
            df_detalle = detalle(st.session_state["documento_seleccionado"])
            df_detalle['Cant ODC'] = pd.to_numeric(df_detalle['Cant ODC'],errors="coerce")
            df_detalle['Cant REC'] = pd.to_numeric(df_detalle['Cant REC'],errors="coerce")
            CANTIDADES = df_detalle['Cant ODC'].sum()
            CANTIDADES_REC = df_detalle['Cant REC'].sum()
            FALTANTE = CANTIDADES - CANTIDADES_REC
            EFECTIVIDAD = round((CANTIDADES_REC/CANTIDADES)*100,2)
            INCUMPLIMIENTO_PONDERADO = round((FALTANTE / CANTIDADES)* 100,2)
            a, b = st.columns(2)
            c, d = st.columns(2)
            st.expander("Metricas").write('Esto es un expander')
            a.metric(label="Cantidades en odc", value= CANTIDADES, border=True)
            b.metric(label = "Cantidad recibida", value=CANTIDADES_REC, border=True)
            a.metric(label="Cantidad faltante", value= FALTANTE, border=True)
            b.metric(label = "Efectividad", value=f'{EFECTIVIDAD}%', border=True)
        
            st.dataframe(df_detalle, height=500, width=1500,)
           
            st.markdown(f"#### {len(df_detalle)} productos encontrados")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_detalle.to_excel(writer, index=False, sheet_name=f'Orden de compra {st.session_state["documento_seleccionado"]}')
                writer.close()
            st.download_button("Descargar Excel", output.getvalue(), f'ODC {st.session_state["documento_seleccionado"]}.xlsx',
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Selecciona una orden de compra para ver su detalle.")
    else:
        st.warning("No se encontraron órdenes de compra para este proveedor.")
else:
    st.info("Por favor, selecciona un proveedor para continuar.")

