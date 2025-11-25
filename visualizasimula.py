import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import requests
from io import StringIO

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Metas Sanitarias",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Monitoreo Metas Sanitarias Ley 20.707")
st.markdown("---")

# Función para cargar y limpiar datos desde Google Sheets
@st.cache_data
def cargar_datos():
    try:
        # URL de Google Sheets
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7yKDhmdK-Hz4Qcr_wpQo9u4Vf6arzrcTEhqujrJUD59Lu9haFKyLQQDdUfgBijB7clgYHpp5x28SZ/pub?gid=304183817&single=true&output=csv"
        
        # Descargar datos
        response = requests.get(url)
        response.encoding = 'utf-8'
        
        # Leer CSV
        df = pd.read_csv(StringIO(response.text))
        
        # Renombrar columnas (basado en la estructura esperada)
        if len(df.columns) >= 20:
            df.columns = ['Unidad_Desempeno', 'Indicador', 'Descripcion', 'Formula', 
                          'Tipo', 'Periodicidad', 'Meta_Anual', 'Ponderacion',
                          'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        else:
            st.error("El archivo CSV no tiene la estructura esperada")
            return pd.DataFrame()

        # Eliminar filas vacías
        df = df.dropna(subset=['Unidad_Desempeno'])

        # Convertir Descripcion a string y corregir encoding
        df['Descripcion'] = df['Descripcion'].fillna('Sin descripción').astype(str)
        
        # Corregir problemas de encoding en todas las columnas de texto
        text_columns = ['Unidad_Desempeno', 'Descripcion', 'Formula', 'Tipo', 'Periodicidad', 'Meta_Anual']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
                # Corregir encoding común
                df[col] = df[col].str.replace('Ã¡', 'á').str.replace('Ã©', 'é').str.replace('Ã­', 'í')\
                                .str.replace('Ã³', 'ó').str.replace('Ãº', 'ú').str.replace('Ã±', 'ñ')\
                                .str.replace('Ã', 'Í').str.replace('Ã“', 'Ó')\
                                .str.replace('â‰¥', '≥').str.replace('â‰¤', '≤')\
                                .str.replace('Ã', 'í').str.replace('Â', '')

        # Convertir Indicador a numérico
        df['Indicador'] = pd.to_numeric(df['Indicador'], errors='coerce')

        # Eliminar filas donde Indicador sea NaN
        df = df.dropna(subset=['Indicador'])

        # Convertir Ponderacion a numérico - manejar diferentes formatos
        df['Ponderacion'] = df['Ponderacion'].astype(str)
        df['Ponderacion'] = df['Ponderacion'].str.replace(',', '.')  # Reemplazar comas por puntos
        df['Ponderacion_Num'] = pd.to_numeric(df['Ponderacion'], errors='coerce')
        
        # Formatear ponderación como porcentaje
        df['Ponderacion_Display'] = df['Ponderacion_Num'].apply(
            lambda x: f"{(x * 100):.1f}%" if pd.notna(x) else "N/A"
        )

        # Convertir Meta_Anual a string
        df['Meta_Anual_Original'] = df['Meta_Anual'].astype(str)

        # Función mejorada para procesar metas anuales - maneja decimales con coma
        def procesar_meta_anual(meta_str):
            meta_str = str(meta_str).strip()
            
            # Corregir encoding específico para símbolos
            meta_str = meta_str.replace('â‰¥', '≥')
            
            # Reemplazar comas por puntos para conversión numérica
            meta_str_para_conversion = meta_str.replace(',', '.')
            
            # Determinar si tiene símbolo ≥
            tiene_mayor_igual = '≥' in meta_str
            meta_limpia = meta_str_para_conversion.replace('≥', '').strip()
            
            # Verificar si ya es un porcentaje (contiene %)
            if '%' in meta_limpia:
                # Ya es porcentaje, extraer el número
                patron_porcentaje = r'(\d+\.?\d*)%'
                match = re.search(patron_porcentaje, meta_limpia)
                if match:
                    valor_numerico = float(match.group(1))
                    # Ya está en porcentaje, no multiplicar
                    valor_porcentaje = valor_numerico
                else:
                    # No se pudo extraer, mantener como texto
                    return pd.Series([meta_str, None, False])
            else:
                # Es un decimal, convertir a porcentaje
                try:
                    # Intentar convertir directamente a número
                    valor_numerico = float(meta_limpia)
                    # Si es decimal (menor que 1 y mayor que 0), convertir a porcentaje
                    if 0 < valor_numerico <= 1:
                        valor_porcentaje = valor_numerico * 100
                    else:
                        # Ya está en porcentaje o es un número entero
                        valor_porcentaje = valor_numerico
                except:
                    # No es numérico, es una glosa
                    return pd.Series([meta_str, None, False])
            
            # Formatear para display
            if tiene_mayor_igual:
                display = f"≥{valor_porcentaje:.1f}%"
            else:
                display = f"{valor_porcentaje:.1f}%"
                
            return pd.Series([display, valor_porcentaje, True])  # True = es comparable

        # Aplicar la función a la columna Meta_Anual
        df[['Meta_Anual_Display', 'Meta_Anual_Valor', 'Meta_Anual_Comparable']] = df['Meta_Anual'].apply(procesar_meta_anual)

        # Convertir columnas de meses a numérico y manejar formato decimal
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        
        for mes in meses:
            if mes in df.columns:
                # Convertir a string primero para manejar formatos
                df[mes] = df[mes].astype(str)
                
                # Reemplazar comas por puntos para conversión numérica
                df[mes] = df[mes].str.replace(',', '.')
                
                # Convertir a numérico y multiplicar por 100 para convertir a porcentaje
                df[mes] = pd.to_numeric(df[mes], errors='coerce') * 100

        return df

    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

# El resto del código permanece igual...
# Cargar datos
df_original = cargar_datos()

# Verificar si se cargaron datos correctamente
if df_original.empty:
    st.error("No se pudieron cargar los datos. Verifique la conexión o la estructura del archivo.")
    st.stop()

# Inicializar session state
if 'unidad_anterior' not in st.session_state:
    st.session_state.unidad_anterior = None

# ============== SELECTOR DE UNIDAD DE DESEMPEÑO ==============
st.header("🎯 Selección de Unidad de Desempeño")

unidades = df_original['Unidad_Desempeno'].unique().tolist()
unidad_seleccionada = st.selectbox(
    "Selecciona una Unidad de Desempeño para ver su detalle:",
    options=unidades,
    index=0
)

st.markdown("---")

# Filtrar datos por la unidad seleccionada
df_filtrado = df_original[df_original['Unidad_Desempeno'] == unidad_seleccionada].copy()
df_filtrado = df_filtrado.reset_index(drop=True)

# Crear clave única para session_state basada en unidad
session_key = f'df_editado_{unidad_seleccionada}'

# Si cambió la unidad, limpiar session state de la unidad anterior
if st.session_state.unidad_anterior != unidad_seleccionada:
    st.session_state.unidad_anterior = unidad_seleccionada

# Inicializar datos originales para la unidad si no existen
if session_key not in st.session_state:
    st.session_state[session_key] = df_filtrado[['Indicador', 'Descripcion', 'Meta_Anual_Display', 
                                                   'Meta_Anual_Valor', 'Meta_Anual_Comparable', 'Ponderacion_Display'] + 
                                                  ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                                                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']].copy()

# ============== DETALLE DE LA UNIDAD SELECCIONADA ==============
st.header(f"📋 Detalle: {unidad_seleccionada}")

# Métricas generales
col1, col2, col3 = st.columns(3)

meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

with col1:
    st.metric("Total Indicadores", len(df_filtrado))

with col2:
    registros_totales = df_filtrado[meses].notna().sum().sum()
    st.metric("Registros Mensuales", int(registros_totales))

with col3:
    promedio_general = df_filtrado[meses].mean().mean()
    st.metric("Cumplimiento Promedio", f"{promedio_general:.1f}%" if pd.notna(promedio_general) else "N/A")

st.markdown("---")

# Mostrar información de cada indicador
st.subheader("📊 Indicadores de la Unidad")

for idx in range(len(df_filtrado)):
    fila = df_filtrado.iloc[idx]

    # Manejar el número de indicador de forma segura
    try:
        num_indicador = int(fila['Indicador'])
        titulo_indicador = f"Indicador {num_indicador} - {fila['Descripcion']}"
    except:
        titulo_indicador = f"Indicador - {fila['Descripcion']}"

    with st.expander(titulo_indicador, expanded=(idx==0)):

        # Información del indicador
        col_info1, col_info2, col_info3, col_info4 = st.columns(4)

        with col_info1:
            st.markdown(f"**Tipo:** {fila['Tipo']}")
        with col_info2:
            st.markdown(f"**Periodicidad:** {fila['Periodicidad']}")
        with col_info3:
            st.markdown(f"**Meta Anual:** {fila['Meta_Anual_Display']}")
        with col_info4:
            st.markdown(f"**Ponderación:** {fila['Ponderacion_Display']}")

        st.markdown(f"**Fórmula:** {fila['Formula']}")

        # Gráfico de evolución mensual usando datos editados actuales
        datos_grafico = st.session_state[session_key].iloc[idx]
        valores_mensuales = [datos_grafico[mes] if pd.notna(datos_grafico[mes]) else None for mes in meses]

        if any(v is not None for v in valores_mensuales):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=meses,
                y=valores_mensuales,
                mode='lines+markers',
                name='Cumplimiento',
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=10, color='#A23B72'),
                fill='tozeroy',
                fillcolor='rgba(46, 134, 171, 0.2)'
            ))

            fig.update_layout(
                title=f"Evolución Mensual",
                xaxis_title="Mes",
                yaxis_title="Cumplimiento (%)",
                hovermode='x unified',
                height=350,
                showlegend=False,
                yaxis=dict(
                    ticksuffix="%",
                    range=[0, 100]  # Escala de 0% a 100%
                )
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos disponibles para este indicador.")

st.markdown("---")

# ============== SIMULACIÓN - TABLA EDITABLE ==============
st.header("🔬 Simulación de Escenarios")

st.markdown("""
En esta sección puedes modificar los valores mensuales para simular diferentes escenarios de cumplimiento.
**Instrucciones:** Haz doble clic en cualquier celda de los meses para editarla y presiona Enter para confirmar.
""")

# Crear pestañas
tab1, tab2, tab3 = st.tabs(["📝 Editar Valores", "📈 Comparación Visual", "📊 Estadísticas"])

with tab1:
    # Botón de reset
    col_titulo, col_reset = st.columns([3, 1])
    with col_titulo:
        st.subheader("Tabla Editable de Cumplimiento Mensual")
    with col_reset:
        if st.button("🔄 Resetear Valores", type="secondary", use_container_width=True, key=f"reset_{unidad_seleccionada}"):
            st.session_state[session_key] = df_filtrado[['Indicador', 'Descripcion', 'Meta_Anual_Display', 
                                                           'Meta_Anual_Valor', 'Meta_Anual_Comparable', 'Ponderacion_Display'] + meses].copy()
            st.success("✅ Valores reseteados a originales")
            st.rerun()

    # SOLUCIÓN 2: Enfoque robusto con manejo de errores
    # Crear una copia para editar
    df_para_editar = st.session_state[session_key].copy()
    
    # Editor de datos con key más estable
    editor_key = f"editor_{unidad_seleccionada}"
    
    try:
        df_editado = st.data_editor(
            df_para_editar,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "Indicador": st.column_config.NumberColumn("Ind.", width="small", disabled=True),
                "Descripcion": st.column_config.TextColumn("Descripción", width="large", disabled=True),
                "Meta_Anual_Display": st.column_config.TextColumn("Meta Anual", width="small", disabled=True),
                "Meta_Anual_Valor": None,
                "Meta_Anual_Comparable": None,
                "Ponderacion_Display": st.column_config.TextColumn("Pond.", width="small", disabled=True),
                **{mes: st.column_config.NumberColumn(mes, width="small", format="%.1f%%") for mes in meses}
            },
            hide_index=True,
            key=editor_key
        )
        
        # Verificar si hubo cambios y actualizar session_state
        if not df_para_editar.equals(df_editado):
            st.session_state[session_key] = df_editado.copy()
            st.success("✅ Cambios guardados automáticamente")
            # Pequeña pausa para mostrar el mensaje
            st.rerun()
            
    except Exception as e:
        st.error(f"Error al editar la tabla: {e}")
        # En caso de error, usar los datos del session_state
        df_editado = st.session_state[session_key].copy()

    # ============== NUEVA SECCIÓN: SIMULACIÓN POR PORCENTAJE ==============
    st.markdown("---")
    st.subheader("🧮 Simulación por Porcentaje Referencial")
    
    st.markdown("**Calcula un porcentaje a partir de numerador y denominador:**")
    
    # Crear columnas para los inputs
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    
    with col_sim1:
        numerador = st.number_input(
            "Numerador",
            min_value=0,
            value=0,
            step=1,
            format="%d",  # Formato entero
            key="numerador_sim"
        )
    
    with col_sim2:
        denominador = st.number_input(
            "Denominador", 
            min_value=1,
            value=1,
            step=1,
            format="%d",  # Formato entero
            key="denominador_sim"
        )
    
    with col_sim3:
        # Mostrar porcentaje calculado
        if denominador > 0:
            porcentaje_calculado = (numerador / denominador) * 100
            st.metric(
                "Porcentaje Simulado", 
                f"{porcentaje_calculado:.1f}%",
                delta=None
            )
        else:
            st.metric("Porcentaje Simulado", "0.0%")

    # ============== META PROYECTADA VS META ANUAL ==============
    st.markdown("---")
    st.subheader("📊 Meta Proyectada vs Meta Anual")

    # Calcular Meta Proyectada (ya está en porcentaje)
    df_temp = df_editado[meses].copy()
    for mes in meses:
        df_temp[mes] = pd.to_numeric(df_temp[mes], errors='coerce')

    df_editado['Promedio_Mensual'] = df_temp.mean(axis=1, skipna=True).round(1)

    # Crear DataFrame para mostrar con promedio y colores
    df_display = df_editado[['Indicador', 'Descripcion', 'Meta_Anual_Display', 'Promedio_Mensual']].copy()
    df_display.rename(columns={'Promedio_Mensual': 'Meta Proyectada'}, inplace=True)
    
    # Convertir Meta Proyectada a formato porcentual para mostrar
    df_display['Meta Proyectada'] = df_display['Meta Proyectada'].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
    )
    
    # Determinar estado solo para metas comparables
    df_display['Estado'] = df_display.apply(
        lambda row: 'Cumple ✅' if (df_editado.loc[row.name, 'Meta_Anual_Comparable'] and 
                                   pd.notna(df_editado.loc[row.name, 'Promedio_Mensual']) and 
                                   pd.notna(df_editado.loc[row.name, 'Meta_Anual_Valor']) and
                                   df_editado.loc[row.name, 'Promedio_Mensual'] >= df_editado.loc[row.name, 'Meta_Anual_Valor'])
                    else ('No Cumple ❌' if (df_editado.loc[row.name, 'Meta_Anual_Comparable'] and 
                                           pd.notna(df_editado.loc[row.name, 'Promedio_Mensual']) and 
                                           pd.notna(df_editado.loc[row.name, 'Meta_Anual_Valor']))
                    else 'No Aplica 🔄'),  # Para glosas o datos faltantes
        axis=1
    )

    # Función para aplicar estilos
    def highlight_proyeccion(row):
        try:
            meta_proyectada_val = float(row['Meta Proyectada'].replace('%', '')) if row['Meta Proyectada'] != 'N/A' else None
        except:
            meta_proyectada_val = None
            
        meta_anual = df_editado.loc[row.name, 'Meta_Anual_Valor']
        es_comparable = df_editado.loc[row.name, 'Meta_Anual_Comparable']

        styles = [''] * len(row)

        # Encontrar índice de la columna Meta Proyectada
        meta_idx = row.index.get_loc('Meta Proyectada')

        if es_comparable and pd.notna(meta_proyectada_val) and pd.notna(meta_anual):
            if meta_proyectada_val >= meta_anual:
                styles[meta_idx] = 'background-color: #d4edda; color: #155724; font-weight: bold'  # Verde
            else:
                styles[meta_idx] = 'background-color: #f8d7da; color: #721c24; font-weight: bold'  # Rojo
        else:
            styles[meta_idx] = 'background-color: #f8f9fa; color: #6c757d'  # Gris

        return styles

    # Mostrar tabla con estilos
    styled_df = df_display.style.apply(highlight_proyeccion, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # Leyenda
    col_leyenda1, col_leyenda2, col_leyenda3 = st.columns(3)
    with col_leyenda1:
        st.caption("✅ **Verde:** Meta proyectada ≥ Meta anual")
    with col_leyenda2:
        st.caption("❌ **Rojo:** Meta proyectada < Meta anual")
    with col_leyenda3:
        st.caption("🔄 **Gris:** No aplica comparación")

with tab2:
    st.subheader("Comparación de Indicadores")

    # Usar datos actuales del session_state
    df_comparacion = st.session_state[session_key].copy()

    # Convertir a numérico
    for mes in meses:
        df_comparacion[mes] = pd.to_numeric(df_comparacion[mes], errors='coerce')

    df_comparacion['Promedio'] = df_comparacion[meses].mean(axis=1, skipna=True)

    # Gráfico de barras
    fig_barras = px.bar(
        df_comparacion,
        x='Indicador',
        y='Promedio',
        title='Promedio de Cumplimiento por Indicador',
        labels={'Promedio': 'Cumplimiento Promedio (%)', 'Indicador': 'Indicador'},
        color='Promedio',
        color_continuous_scale='RdYlGn',
        height=450
    )

    fig_barras.update_layout(
        showlegend=False,
        yaxis=dict(
            ticksuffix="%",
            range=[0, 100]
        )
    )
    st.plotly_chart(fig_barras, use_container_width=True)

    # Gráfico de líneas múltiples
    st.markdown("### Evolución Comparativa")

    # Crear DataFrame para gráfico múltiple
    datos_grafico = []
    for idx in range(len(df_comparacion)):
        ind_valor = df_comparacion.iloc[idx]['Indicador']
        try:
            ind_num = int(ind_valor)
            ind_label = f"Ind. {ind_num}"
        except:
            ind_label = f"Ind. {idx+1}"

        for mes in meses:
            valor = df_comparacion.iloc[idx][mes]
            if pd.notna(valor):
                datos_grafico.append({
                    'Mes': mes,
                    'Cumplimiento': valor,
                    'Indicador': ind_label
                })

    if datos_grafico:
        df_grafico = pd.DataFrame(datos_grafico)

        fig_lineas = px.line(
            df_grafico,
            x='Mes',
            y='Cumplimiento',
            color='Indicador',
            title='Evolución Mensual de Todos los Indicadores',
            markers=True,
            height=450
        )

        fig_lineas.update_layout(
            yaxis=dict(
                ticksuffix="%",
                range=[0, 100]
            )
        )

        st.plotly_chart(fig_lineas, use_container_width=True)

with tab3:
    st.subheader("Estadísticas Detalladas")

    # Usar datos actuales del session_state
    df_stats_base = st.session_state[session_key].copy()
    df_stats = df_stats_base[['Indicador', 'Descripcion', 'Meta_Anual_Display', 'Ponderacion_Display']].copy()

    # Convertir meses a numérico para estadísticas
    df_temp = df_stats_base[meses].copy()
    for mes in meses:
        df_temp[mes] = pd.to_numeric(df_temp[mes], errors='coerce')

    df_stats['Meta_Proyectada'] = df_temp.mean(axis=1, skipna=True).round(1)
    df_stats['Promedio'] = df_stats['Meta_Proyectada']
    df_stats['Mínimo'] = df_temp.min(axis=1, skipna=True).round(1)
    df_stats['Máximo'] = df_temp.max(axis=1, skipna=True).round(1)
    df_stats['Desv. Est.'] = df_temp.std(axis=1, skipna=True).round(1)
    df_stats['Meses Registrados'] = df_temp.notna().sum(axis=1)

    # Formatear columnas numéricas como porcentajes
    df_stats['Meta_Proyectada'] = df_stats['Meta_Proyectada'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    df_stats['Promedio'] = df_stats['Promedio'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    df_stats['Mínimo'] = df_stats['Mínimo'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    df_stats['Máximo'] = df_stats['Máximo'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    df_stats['Desv. Est.'] = df_stats['Desv. Est.'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")

    st.dataframe(df_stats, use_container_width=True, hide_index=True)

    # Resumen general
    st.markdown("---")
    st.markdown("### 📈 Resumen General")

    col_stat1, col_stat2, col_stat3 = st.columns(3)

    with col_stat1:
        # Calcular promedio global de los valores numéricos
        promedios_numericos = df_temp.mean(axis=1, skipna=True)
        promedio_todos = promedios_numericos.mean()
        st.metric("Promedio Global", f"{promedio_todos:.1f}%" if pd.notna(promedio_todos) else "N/A")

    with col_stat2:
        if len(promedios_numericos) > 0 and not promedios_numericos.isna().all():
            mejor_idx = promedios_numericos.idxmax()
            mejor_indicador = df_stats.loc[mejor_idx, 'Indicador']
            mejor_valor = promedios_numericos.loc[mejor_idx]
            try:
                st.metric("Mejor Indicador", f"Ind. {int(mejor_indicador)}: {mejor_valor:.1f}%")
            except:
                st.metric("Mejor Indicador", f"{mejor_valor:.1f}%")
        else:
            st.metric("Mejor Indicador", "N/A")

    with col_stat3:
        if len(promedios_numericos) > 0 and not promedios_numericos.isna().all():
            menor_idx = promedios_numericos.idxmin()
            menor_indicador = df_stats.loc[menor_idx, 'Indicador']
            menor_valor = promedios_numericos.loc[menor_idx]
            try:
                st.metric("Menor Indicador", f"Ind. {int(menor_indicador)}: {menor_valor:.1f}%")
            except:
                st.metric("Menor Indicador", f"{menor_valor:.1f}%")
        else:
            st.metric("Menor Indicador", "N/A")

# Sidebar con información
st.sidebar.markdown("### ℹ️ Acerca de")
st.sidebar.info(
    """
    **Dashboard Metas Sanitarias**

    Funcionalidades:
    - Selección de unidades
    - Visualización de indicadores
    - Simulación editable con persistencia
    - Calculadora de porcentaje referencial
    - Botón de reset
    - Comparación gráfica
    - Meta proyectada con indicador visual
    """
)

st.sidebar.markdown("---")
st.sidebar.caption("v4.1 - Dashboard Interactivo")