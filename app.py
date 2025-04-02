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
            SELECT DISTINCT [PROV] 
            FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] 
            ORDER BY [PROV] ASC
        """)
        proveedores = [row[0] for row in cursor.fetchall()]
        return proveedores
    except Exception as e:
        st.write(f"Error en la consulta SQL: {e}")
        return []

def obtener_ordenes_compra(proveedor=None):
    if cursor is not None:
        try:
            cursor.execute("""
                SELECT DISTINCT [ODCDOC])) AS [ODCDOC] 
                FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] 
                WHERE [PROV]<>'' 
                ORDER BY FLOOR(CONVERT(DECIMAL, [ODCDOC])) DESC
            """)
            resultados = cursor.fetchall()
            ordenes_compra = [str(fila[0]) for fila in resultados]
            return ordenes_compra
        except pyodbc.Error as e:
            sqlstate = e.args[0]
            if sqlstate == '42S02':
                st.error(f"Error: La tabla o vista no existe. {e}")
            elif sqlstate == '42S22':
                st.error(f"Error: La columna no existe. {e}")
            else:
                st.error(f"Error al obtener órdenes de compra: {e}")
            return []
    else:
        return []

# Inicializar estado
if "Lista_Proveedores" not in st.session_state:
    st.session_state["Lista_Proveedores"] = "Seleccione el proveedor"
if "filtro2" not in st.session_state:
    st.session_state["filtro2"] = None
if "fecha_inicial" not in st.session_state:
    st.session_state["fecha_inicial"] = None
if "orden_compra" not in st.session_state:  # Clave corregida
    st.session_state["orden_compra"] = "Nº ODC"
if "fecha_final" not in st.session_state:
    st.session_state["fecha_final"] = None
if "anio" not in st.session_state:
    st.session_state["anio"] = None
if "mes" not in st.session_state:
    st.session_state["mes"] = None
if "limpiar" not in st.session_state:
    st.session_state["limpiar"] = False
if "orden_compra_seleccionada_boton" not in st.session_state:
    st.session_state["orden_compra_seleccionada_boton"] = None

# Simular clic en el botón "Limpiar Campos" al inicio para que no muestre selección en filtro por fecha:
if "limpiar_inicio" not in st.session_state:
    st.session_state["limpiar_inicio"] = True
    st.session_state["limpiar"] = True
    st.rerun()

# Botón para limpiar campos:
if st.session_state["limpiar"]:
    st.session_state["limpiar"] = False
    st.session_state["Lista_Proveedores"] = "Seleccione el proveedor"
    st.session_state["orden_compra"] = "Nº ODC"  # Clave corregida
    st.session_state["filtro2"] = None
    st.session_state["fecha_inicial"] = None
    st.session_state["fecha_final"] = None
    st.session_state["anio"] = None
    st.session_state["mes"] = None
    st.rerun()  # Recargar la página

# Ruta de la imagen
ruta_imagen = "images/Suministros Logo.png"

# Mostrar la imagen
st.image(ruta_imagen, caption=" ", width=200)
st.title("CONTROL DE ÓRDENES DE COMPRA")

proveedores = plantilla()
ordenes_compra = obtener_ordenes_compra()

def actualizar_seleccion1():  # Cuando selecciono Nº ODC - Se borran las demás opciones
    st.session_state["Lista_Proveedores"] = "Seleccione el proveedor"
    st.session_state["filtro2"] = None

# Selección de orden de compra
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    orden_compra_seleccionada = st.selectbox(
        "Si conoce el Nº de la Orden:", ["Nº ODC"] + ordenes_compra, key="orden_compra", on_change=actualizar_seleccion1
    )

st.divider()

def buscar_mes(cursor):  # CONSULTA AÑO - MES
    if cursor is not None:
        try:
            cursor.execute("""
                SELECT DISTINCT YEAR([FECHAODC]) AS AÑO, MONTH([FECHAODC]) AS NUMERO_MES 
                FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] 
                ORDER BY AÑO, NUMERO_MES;
            """)
            resultados = cursor.fetchall()

            # Convertir los números de mes a nombres en español
            meses_nombres = []
            for fila in resultados:
                año = fila.AÑO
                numero_mes = fila.NUMERO_MES
                nombre_mes = obtener_nombre_mes(numero_mes)  # Función auxiliar para obtener el nombre del mes
                meses_nombres.append({"año": año, "mes": nombre_mes, "numero_mes": numero_mes})  # Incluir numero_mes

            return meses_nombres
        except pyodbc.Error as e:
            sqlstate = e.args[0]
            if sqlstate == '42S02':
                st.error(f"Error: La tabla o vista no existe. {e}")
            elif sqlstate == '42S22':
                st.error(f"Error: La columna no existe. {e}")
            else:
                st.error(f"Error al obtener meses: {e}")
            return []
    else:
        return []

def obtener_nombre_mes(numero_mes):  # CAMBIO DE MES (NUMÉRICO A DESCRIPCIÓN EN LETRAS)
    nombres_meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    return nombres_meses.get(numero_mes, 'Mes Inválido')

def actualizar_seleccion2():  # Cuando selecciono Proveedor - Se borra el Nº ODC
    st.session_state["orden_compra"] = "Nº ODC"

# SELECCIÓN DE PROVEEDOR (LISTADO)
col1, col2, col3 = st.columns([4, 1, 2])
with col1:
    Lista = st.selectbox(
        "Lista de Proveedores:",
        ["Seleccione el proveedor"] + proveedores,
        key="Lista_Proveedores", on_change=actualizar_seleccion2
    )

def actualizar_seleccion3():  # Cuando selecciono fecha - Se borra Nº ODC
    st.session_state["orden_compra"] = "Nº ODC"

# SELECCIÓN DE BOTÓN: RANGO DE FECHA - MES
with col2:
    filtro2 = st.radio("Filtrar por:", ("Rango de fechas", "Mes"), key="filtro2", on_change=actualizar_seleccion3)
    fecha_inicial = None
    fecha_final = None
    anio = None

# SELECCIÓN DE RANGO DE FECHAS O MES
with col3:
    if filtro2 == "Rango de fechas":
        sub_col1, sub_col2 = st.columns(2)  # Crear subcolumnas dentro de col3
        with sub_col1:
            fecha_inicial = st.date_input("Fecha Inicial:", key="fecha_inicial")
        with sub_col2:
            fecha_final = st.date_input("Fecha Final:", key="fecha_final")

    if filtro2 == "Mes":
        meses_disponibles = buscar_mes(cursor)  # Obtener los meses disponibles
        # Obtener años únicos y ordenarlos
        anios_unicos = sorted(list(set(mes["año"] for mes in meses_disponibles)))

        # Obtener meses únicos para el año seleccionado y ordenarlos
        meses_unicos = sorted(list(set(mes["mes"] for mes in meses_disponibles)))

        sub_col1, sub_col2 = st.columns(2)  # Crear subcolumnas dentro de col3

        with sub_col1:
            anio = st.selectbox("Año:", options=anios_unicos, key="anio")

        with sub_col2:
            # Filtrar los meses disponibles for el año seleccionado
            meses_filtrados = [mes["mes"] for mes in meses_disponibles if mes["año"] == anio]
            mes = st.selectbox("Mes:", options=meses_filtrados, key="mes")

            # Filtrar los datos según el año y mes seleccionados
        datos_filtrados = [mes for mes in meses_disponibles if mes["año"] == anio and mes["mes"] == mes]

    else:
        # Mostrar todos los datos (si no se aplica el filtro)
        meses_disponibles = buscar_mes(cursor)

# Botones de acción
col1, col2, col3, col4 = st.columns(4)
with col2:
    buscar = st.button("Buscar ODC")
with col4:
    limpiar = st.button("Limpiar Campos")

def ordenes_compra_prov():
    if cursor is not None:
        try:
            consulta = f"""
                SELECT DISTINCT FLOOR(CONVERT(DECIMAL, [ODCDOC])) AS [ODCDOC] 
                FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] 
                WHERE [PROV] = '{st.session_state["Lista_Proveedores"]}' 
                ORDER BY FLOOR(CONVERT(DECIMAL, [ODCDOC])) DESC
            """
            print(f"Consulta SQL: {consulta}")  # Imprimir la consulta
            cursor.execute(consulta)
            resultados2 = cursor.fetchall()
            ordenes_compra_proveedor = [str(fila[0]) for fila in resultados2]
            print(f"Ordenes de compra encontradas: {ordenes_compra_proveedor}") #imprimo los resultados.
            return ordenes_compra_proveedor
        except pyodbc.Error as e:
            sqlstate = e.args[0]
            if sqlstate == '42S02':
                st.error(f"Error: La tabla o vista no existe. {e}")
            elif sqlstate == '42S22':
                st.error(f"Error: La columna no existe. {e}")
            else:
                st.error(f"Error al obtener órdenes de compra: {e}")
            return []
    else:
        return []

def odc_seleccionada2():
    if cursor is not None:
        try:
            consulta2 = f"""
                SELECT [FECHAODC] AS [Fecha ODC],
                [Barra] AS [SKU],
                [Producto] AS [Descripción de Producto],
                FORMAT([CantODC], 'N2', 'es-ES') AS [Cant ODC],
                [RECDOC] AS [Nº REC],[FECHAREC] AS [Fecha RECEP],
                FORMAT([CantREC], 'N2', 'es-ES') AS [Cant REC],
                FORMAT([FALTANTE], 'N2', 'es-ES') AS [Cant Faltante]
                FROM [VAD10_SCORP].[dbo].[REP_ODCxREC]
                WHERE [ODCDOC] = '{odc}' ORDER BY [Nº REC] ASC
            """
            print(f"Consulta SQL: {consulta2}")  # Imprimir la consulta
            cursor.execute(consulta2)
            resultados3 = cursor.fetchall()
            odc_selec2 = [str(fila[0]) for fila in resultados3]
            print(f"Orden de compra seleccionada: {odc_selec2}") #imprimo los resultados.
            return odc_selec2
        except pyodbc.Error as e:
            sqlstate = e.args[0]
            if sqlstate == '42S02':
                st.error(f"Error: La tabla o vista no existe. {e}")
            elif sqlstate == '42S22':
                st.error(f"Error: La columna no existe. {e}")
            else:
                st.error(f"Error al obtener órdenes de compra: {e}")
            return []
    else:
        return []

ordenes_compra_proveedor = ordenes_compra_prov()

if buscar:
    try:
        # Construir la consulta dinámica
        consulta_datos = "SELECT [ODCDOC] FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] WHERE [ODCDOC]<>''"
        if Lista != "Seleccione el proveedor":
            consulta_datos += f" AND [PROV] = '{Lista}'"
        if filtro2 == "Rango de fechas":
            consulta_datos += f" AND [FECHAODC] BETWEEN '{fecha_inicial}' AND '{fecha_final}'"

        anio = None  # Inicializar anio
        mes = None

        if filtro2 == "Mes":
            # Aquí es donde debes hacer el cambio
            numero_mes = [item["numero_mes"] for item in meses_disponibles if item["año"] == anio and item["mes"] == mes][0]
            consulta_datos += f" AND YEAR([FECHAODC]) = '{anio}' AND MONTH([FECHAODC]) = '{numero_mes}'"

        st.divider()

        # Ejecutar la consulta SQL
        df = pd.read_sql(consulta_datos, conn)

        # SI NO TENGO ODC SELECCIONADA EN LISTADO ENTONCES: 

        if orden_compra_seleccionada == "Nº ODC":
            # Mostrar botones si no se ha seleccionado una orden
            num_botones = len(ordenes_compra_proveedor)

            if num_botones > 0:
                num_columnas = min(num_botones, 15)  # Máximo 15 columnas

                # Verificar que num_columnas sea positivo antes de llamar a st.columns()
                if num_columnas > 0:
                    columnas = st.columns(num_columnas)

                    columna_seleccionada = None  # Variable para almacenar el índice de la columna seleccionada
                    odc_seleccionada = None # Variable para almacenar el valor de la ODC seleccionada.

                    for i, odc in enumerate(ordenes_compra_proveedor):
                        with columnas[i % num_columnas]:

                            if st.button(odc, key=f"btn_{i}"):  # odc almacena los números de órdenes y st.button los muestra en botones, se agrega una key unica.
                                columna_seleccionada = i % num_columnas  # Almacena el índice de la columna seleccionada
                                odc_seleccionada = odc # Almacena el valor de la ODC seleccionada.
                                st.session_state['odc_seleccionada_boton'] = odc_seleccionada # Guarda el valor en el estado de la sesión
                                st.rerun() #para que se actualice la pagina.
                    if 'odc_seleccionada_boton' in st.session_state and st.session_state['odc_seleccionada_boton']:
                        st.write(f"ODC Nº{st.session_state['odc_seleccionada_boton']} seleccionada.") #Muestra el mensaje.
                    
                    if columna_seleccionada is not None:
                        st.write(f"Índice de la columna seleccionada: {columna_seleccionada}")
                        # Aquí puedes usar la variable 'columna_seleccionada' para realizar otras acciones

        # SINO EJECUTA LO SIGUIENTE:

        else:
            try:
                consulta_n_ODC = f"SELECT [FECHAODC] AS [Fecha ODC], [Barra] AS [SKU], [Producto] AS [Descripción de Producto],FORMAT([CantODC], 'N2', 'es-ES') AS [Cant ODC],[RECDOC] AS [Nº REC],[FECHAREC] AS [Fecha RECEP],FORMAT([CantREC], 'N2', 'es-ES') AS [Cant REC],FORMAT([FALTANTE], 'N2', 'es-ES') AS [Cant Faltante] FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] WHERE [ODCDOC] = '{orden_compra_seleccionada}'ORDER BY [Nº REC] ASC"
                df_n_ODC = pd.read_sql(consulta_n_ODC, conn)

                if not df_n_ODC.empty:
                    # Crear resumen
                    consulta_PROVEEDOR = (f"SELECT DISTINCT [PROV] AS [Proveedor] FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] WHERE [ODCDOC] = '{orden_compra_seleccionada}'")
                    df_proveedor = pd.read_sql(consulta_PROVEEDOR, conn)
                    if not df_proveedor.empty:
                        proveedor = df_proveedor["Proveedor"].iloc[0]  # Obtienen el primer valor del df

                    consulta_RIF = (f"SELECT DISTINCT [RIF] FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] WHERE [ODCDOC] = '{orden_compra_seleccionada}'")
                    df_rif = pd.read_sql(consulta_RIF, conn)
                    if not df_rif.empty:
                        rif = df_rif["RIF"].iloc[0]  # Obtienen el primer valor del df

                    consulta_DESTINO = (f"SELECT DISTINCT [Deposito] AS [Destino ODC] FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] WHERE [ODCDOC] = '{orden_compra_seleccionada}'")
                    df_destino = pd.read_sql(consulta_DESTINO, conn)
                    if not df_destino.empty:
                        destino = df_destino["Destino ODC"].iloc[0]  # Obtienen el primer valor del df

                    consulta_RECEPCION = (f"SELECT DISTINCT [ALM_ORIG] AS [Lugar RECEP] FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] WHERE [ODCDOC] = '{orden_compra_seleccionada}'")
                    df_recepcion = pd.read_sql(consulta_RECEPCION, conn)
                    if not df_recepcion.empty:
                        recepcion = df_recepcion["Lugar RECEP"].iloc[0]  # Obtienen el primer valor del df

                    consulta_REC = (f"SELECT DISTINCT CONVERT(INT, FLOOR(CONVERT(DECIMAL(10, 0), [RECDOC]))) AS [Nº REC] FROM [VAD10_SCORP].[dbo].[REP_ODCxREC] WHERE [ODCDOC] = '{orden_compra_seleccionada}'")
                    df_rec = pd.read_sql(consulta_REC, conn)
                    # Extraer los valores de la columna 'Nº REC' y formatearlos como una cadena separada por comas.
                    rec = " - ".join(map(str, df_rec['Nº REC'].tolist()))

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f'<span style="font-size: 24px; color: white;">Nº ODC:</span> <span style="font-size: 24px; color: #fd6214;">**{orden_compra_seleccionada}**</span>', unsafe_allow_html=True)

                        container1 = st.container()
                        with container1:
                            st.markdown(f"**RIF:** {rif}")
                        container2 = st.container()
                        with container2:
                            st.markdown(f"**PROVEEDOR:** {proveedor}")

                    with col2:
                        st.markdown(f'<span style="font-size: 24px; color: white;">Nº REC:</span> <span style="font-size: 24px; color: #fd6214;">**{rec}**</span>', unsafe_allow_html=True)

                        container3 = st.container()
                        with container3:
                            st.markdown(f"**DESTINO (ODC):** {destino}")
                        container4 = st.container()
                        with container4:
                            st.markdown(f"**RECEPCIÓN:** {recepcion}")

                    st.dataframe(df_n_ODC)

            except Exception as e:
                st.error(f"Error al obtener detalles de la orden de compra: {e}")

    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")

    finally:
        # Cerrar la conexión siempre
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

# Botón para limpiar la sesión
if limpiar:
    st.session_state["limpiar"] = True
    st.rerun()