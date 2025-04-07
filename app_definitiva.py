import streamlit as st
import pandas as pd
from datetime import datetime
from credenciales import conexion
import io
import locale

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
def detalle(documento):
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        query = f"""
            SELECT [FECHAODC] AS [Fecha ODC],
                [Barra] AS [SKU],
                [Producto] AS [Descripción de Producto],
                [CantODC] AS [Cant ODC],
                [RECDOC] AS [Nº REC],
                [FECHAREC] AS [Fecha RECEP],
                [CantREC] AS [Cant REC],
                [FALTANTE] AS [Cant Faltante]
            FROM [VAD10_SCORP].[dbo].[REP_ODCxREC]
            WHERE [ODCDOC] = '{documento}' ORDER BY [Nº REC] ASC
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error en la consulta SQL: {e}")
        return []

def convertir_a_entero(documento):
    return str(int(float(documento)))

def datos_resumen(documento, engine):
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        # Convertir a entero, si es necesario
        odc_doc = int(float(st.session_state["documento_seleccionado"]))
        datos = f"""
            SELECT DISTINCT CONVERT(INT, FLOOR(CONVERT(DECIMAL(10, 0), [RECDOC]))) AS [Nº REC], [RIF], [PROV], [Deposito] AS [Almacén ODC], [ALM_ORIG] AS [Almacén de Recepción], [RECEPTOR] AS [Receptor], [COMPRADOR] AS [Comprador]
            FROM [VAD10_SCORP].[dbo].[REP_ODCxREC]
            WHERE [ODCDOC] = {odc_doc} ORDER BY [Nº REC] ASC
        """
        df2 = pd.read_sql(datos, engine)

        if not df2.empty:
            proveedor = df2['PROV'].iloc[0]
            rif = df2['RIF'].iloc[0]
            rec = " - ".join(map(str, df2['Nº REC'].tolist()))
            destino = df2['Almacén ODC'].iloc[0]
            recepcion = df2['Almacén de Recepción'].iloc[0]
            comprador = df2['Comprador'].iloc[0]
            receptor = df2['Receptor'].iloc[0]

            return df2, proveedor, rif, rec, destino, recepcion, comprador, receptor  # retornar todos los valores
        else:
            return pd.DataFrame(), None, None, None, None, None  # retornar todos los valores

    except Exception as e:
        st.error(f"Error en la consulta SQL: {e}")
        return pd.DataFrame(), None, None, None, None, None  # retornar todos los valores

# Filtrar por fecha
def ordenes_fecha(proveedor):
    if not proveedor:
        return []
    try:
        query = f"""
            SELECT DISTINCT FLOOR(CONVERT(DECIMAL, [ODCDOC])) AS [ODCDOC] 
            FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] 
            WHERE [PROV] = '{proveedor}' and [FECHAODC]
            ORDER BY FLOOR(CONVERT(DECIMAL, [ODCDOC])) DESC
        """
        df = pd.read_sql(query, engine)
        df['ODCDOC'] = round(df['ODCDOC'], 0)
        return df['ODCDOC'].to_list()
    except Exception as e:
        st.error(f"Error en la consulta SQL: {e}")
        return []


# Ruta de la imagen
st.image("images/Suministros Logo.png", caption=" ", width=200)
st.title("CONTROL DE ÓRDENES DE COMPRA")

# Crear pestañas
tab1, tab2 = st.tabs(["### Detalle ODC", "### Efectividad Proveedor"])

with tab1:
    st.write("En esta sección encontrarán el detalle de cada Orden de Compra buscada (Cantidades e Indicadores del Proveedor).")
    
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

    # Limpiar campos si cambia el proveedor
    if "proveedor_anterior" in st.session_state and st.session_state["proveedor_anterior"] != proveedor:
        if "documento_seleccionado" in st.session_state:
            del st.session_state["documento_seleccionado"]
        if "df_detalle" in st.session_state:
            del st.session_state["df_detalle"]

    # Actualizar el proveedor anterior
    st.session_state["proveedor_anterior"] = proveedor

    # Mostrar órdenes solo si se seleccionó un proveedor
    if proveedor:
        ordenes_lista = ordenes(proveedor)

        if ordenes_lista:
            st.markdown(" Selecciona una orden de compra:")
            cols = st.columns(15)

            for index, documento in enumerate(ordenes_lista):
                col = cols[index % 15]
                with col:
                    documento_entero= convertir_a_entero(documento)    
                    if st.button(documento_entero, key=f"doc_{documento}"):
                        st.session_state["documento_seleccionado"] = documento_entero
                        st.rerun()
                        
            # Mostrar mensaje de selección
            if "documento_seleccionado" in st.session_state:
                st.success(f'Has seleccionado la Orden de Compra Nº: {st.session_state["documento_seleccionado"]}')
                df_detalle = detalle(st.session_state["documento_seleccionado"])
                
                # Verificar y manejar valores NaN
                df_detalle['Cant ODC'] = df_detalle['Cant ODC'].fillna(0)
                df_detalle['Cant REC'] = df_detalle['Cant REC'].fillna(0)

                # Eliminar espacios en blanco
                df_detalle['Cant ODC'] = df_detalle['Cant ODC'].str.strip()
                df_detalle['Cant REC'] = df_detalle['Cant REC'].str.strip()

                # Convertir a números
                df_detalle['Cant ODC'] = pd.to_numeric(df_detalle['Cant ODC'], errors="coerce")
                df_detalle['Cant REC'] = pd.to_numeric(df_detalle['Cant REC'], errors="coerce")
                
                CANTIDADES = df_detalle['Cant ODC'].sum()
                CANTIDADES_REC = df_detalle['Cant REC'].sum()
                FALTANTE = CANTIDADES - CANTIDADES_REC
                EFECTIVIDAD = round((CANTIDADES_REC / CANTIDADES) * 100, 2)
                INCUMPLIMIENTO_PONDERADO = 0 if round((FALTANTE / CANTIDADES) * 100, 2) < 0 else round((FALTANTE / CANTIDADES) * 100, 2)

                CANTIDADES_FORMAT = locale.format_string("%.2f", CANTIDADES, grouping=True)
                CANTIDADES_REC_FORMAT = locale.format_string("%.2f", CANTIDADES_REC, grouping=True)
                FALTANTE_FORMAT = locale.format_string("%.2f", FALTANTE, grouping=True)  # Formatear FALTANTE

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric(label="### Cantidades en ODC", value=CANTIDADES_FORMAT, border=True)
                with col2:
                    st.metric(label="### Cantidad Recibida", value=CANTIDADES_REC_FORMAT, border=True)
                with col3:
                    st.metric(label="### Cantidad Faltante", value=FALTANTE_FORMAT, border=True)
                with col4:
                    st.metric(label="### Efectividad %", value=f'{EFECTIVIDAD}%', border=True)
                with col5:
                    st.metric(label="### Incumplimiento %", value=f'{INCUMPLIMIENTO_PONDERADO}%', border=True)
                    
                formato = {
                    'Cant ODC': '{:,.2f}',
                    'Cant REC': '{:,.2f}',
                    'Cant Faltante': '{:,.2f}',
                    'Nº REC': '{:.0f}'
                }

                df_result, proveedor, rif, rec, destino, recepcion, comprador, receptor = datos_resumen(st.session_state["documento_seleccionado"], engine)

                if proveedor: #verificar que el proveedor no sea None
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f'<span style="font-size: 24px; color: white;">Nº ODC:</span> <span style="font-size: 24px; color: #fd6214;">**{st.session_state["documento_seleccionado"]}**</span>', unsafe_allow_html=True)

                        container1 = st.container()
                        
                        with container1:
                            st.markdown(f"**RIF:** {rif}")
                            
                        container2 = st.container()
                        with container2:
                            st.markdown(f"**PROVEEDOR:** {proveedor}")
                            
                        container3 = st.container()  
                        with container3:
                            st.markdown(f"**COMPRADOR:** {comprador}")

                    with col2:
                        st.markdown(f'<span style="font-size: 24px; color: white;">Nº REC:</span> <span style="font-size: 24px; color: #fd6214;">**{rec}**</span>', unsafe_allow_html=True)

                        container4 = st.container()
                        with container4:
                            st.markdown(f"**DESTINO (ODC):** {destino}")

                        container5 = st.container()
                        with container5:
                            st.markdown(f"**RECEPCIÓN:** {recepcion}")
                            
                        container6 = st.container()
                        with container6:
                            st.markdown(f"**RECEPTOR:** {receptor}")
                            
                else:
                    st.warning("No se encontraron datos para el documento especificado.") #manejo de error, en caso de que no se encuentren datos
    
                df_detalle_centrado = df_detalle.style.format(formato).set_properties(**{'text-align': 'center'})
                st.dataframe(df_detalle_centrado, height=350, width=1700)

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

with tab2:
    st.write("PÁGINA EN CONSTRUCCIÓN")
    #st.write("En esta sección encontrarán la Efectividad por Proveedor de Forma Mensual.")

    # Selección de proveedor
    #col1, col2 = st.columns(2)
    #with col1:
    #    proveedor2 = st.selectbox(
    #        "Lista de Proveedores:",
    #        proveedores,
    #        key="Lista_Proveedores2",
    #        index=None,
    #        placeholder="Selecciona un proveedor")

    #with col2:
    #    filtro_fecha= st.selectbox(label="Filtro Fecha:", options="Año",  placeholder="Selecciona el año")
 
    
    