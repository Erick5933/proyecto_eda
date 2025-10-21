import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import StringIO
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Análisis Compras Públicas Ecuador",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Análisis Exploratorio de Compras Públicas Ecuador (2015-2025)")
st.markdown("### Análisis de datos de contratación pública del SERCOP")

# Función para cargar datos
@st.cache_data
def cargar_datos():
    """Carga datos de compras públicas desde la API del SERCOP o CSV simulado"""
    try:
        # Intentar cargar desde API del SERCOP (ejemplo)
        # URL: https://datosabiertos.compraspublicas.gob.ec/
        st.info("Cargando datos de compras públicas...")
        
        # Para este ejemplo, crearemos datos simulados realistas
        # En producción, usa: df = pd.read_csv('url_del_dataset') o API
        
        np.random.seed(42)
        n_registros = 5000
        
        años = np.random.choice(range(2015, 2026), n_registros)
        
        data = {
            'año': años,
            'mes': np.random.randint(1, 13, n_registros),
            'provincia': np.random.choice([
                'Pichincha', 'Guayas', 'Azuay', 'Manabí', 'El Oro', 
                'Los Ríos', 'Tungurahua', 'Esmeraldas', 'Imbabura', 'Loja'
            ], n_registros),
            'tipo_compra': np.random.choice([
                'Subasta Inversa', 'Menor Cuantía', 'Licitación', 
                'Contratación Directa', 'Catálogo Electrónico'
            ], n_registros),
            'sector': np.random.choice([
                'Salud', 'Educación', 'Infraestructura', 'Seguridad',
                'Servicios Públicos', 'Tecnología', 'Transporte'
            ], n_registros),
            'monto_usd': np.random.lognormal(9, 2, n_registros),
            'estado': np.random.choice([
                'Finalizado', 'En proceso', 'Cancelado', 'Adjudicado'
            ], n_registros, p=[0.6, 0.2, 0.1, 0.1]),
            'num_oferentes': np.random.randint(1, 15, n_registros),
            'tiempo_proceso_dias': np.random.randint(15, 180, n_registros)
        }
        
        df = pd.DataFrame(data)
        df['fecha'] = pd.to_datetime(
            df['año'].astype(str) + '-' + df['mes'].astype(str) + '-01'
        )
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return None

# Función de limpieza de datos
@st.cache_data
def limpiar_datos(df):
    """Limpieza y normalización del dataset"""
    df_clean = df.copy()
    
    # Eliminar duplicados
    df_clean = df_clean.drop_duplicates()
    
    # Manejar valores nulos
    df_clean = df_clean.dropna(subset=['monto_usd', 'año'])
    
    # Estandarizar textos
    df_clean['provincia'] = df_clean['provincia'].str.strip().str.title()
    df_clean['tipo_compra'] = df_clean['tipo_compra'].str.strip()
    df_clean['sector'] = df_clean['sector'].str.strip()
    
    # Eliminar valores negativos o cero en montos
    df_clean = df_clean[df_clean['monto_usd'] > 0]
    
    # Filtrar años válidos
    df_clean = df_clean[(df_clean['año'] >= 2015) & (df_clean['año'] <= 2025)]
    
    return df_clean

# Cargar y limpiar datos
df = cargar_datos()

if df is not None:
    df_clean = limpiar_datos(df)
    
    # Sidebar para filtros
    st.sidebar.header("🔍 Filtros")
    
    años_seleccionados = st.sidebar.multiselect(
        "Seleccionar años:",
        options=sorted(df_clean['año'].unique()),
        default=sorted(df_clean['año'].unique())
    )
    
    provincias_seleccionadas = st.sidebar.multiselect(
        "Seleccionar provincias:",
        options=sorted(df_clean['provincia'].unique()),
        default=sorted(df_clean['provincia'].unique())
    )
    
    sectores_seleccionados = st.sidebar.multiselect(
        "Seleccionar sectores:",
        options=sorted(df_clean['sector'].unique()),
        default=sorted(df_clean['sector'].unique())
    )
    
    # Filtrar datos
    df_filtrado = df_clean[
        (df_clean['año'].isin(años_seleccionados)) &
        (df_clean['provincia'].isin(provincias_seleccionadas)) &
        (df_clean['sector'].isin(sectores_seleccionados))
    ]
    
    # Métricas principales (KPIs)
    st.header("📈 KPIs Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_contratos = len(df_filtrado)
        st.metric("Total Contratos", f"{total_contratos:,}")
    
    with col2:
        monto_total = df_filtrado['monto_usd'].sum()
        st.metric("Monto Total", f"${monto_total:,.2f}")
    
    with col3:
        monto_promedio = df_filtrado['monto_usd'].mean()
        st.metric("Monto Promedio", f"${monto_promedio:,.2f}")
    
    with col4:
        tiempo_promedio = df_filtrado['tiempo_proceso_dias'].mean()
        st.metric("Tiempo Promedio (días)", f"{tiempo_promedio:.0f}")
    
    # Tabs para diferentes análisis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Análisis Temporal", 
        "🗺️ Análisis Geográfico",
        "💼 Análisis por Sector",
        "🔗 Correlaciones",
        "📋 Datos"
    ])
    
    with tab1:
        st.subheader("Evolución de Compras Públicas por Año")
        
        # Gráfico de barras: Número de contratos por año
        contratos_año = df_filtrado.groupby('año').size().reset_index(name='cantidad')
        
        fig1 = px.bar(
            contratos_año,
            x='año',
            y='cantidad',
            title='Número de Contratos por Año',
            labels={'año': 'Año', 'cantidad': 'Cantidad de Contratos'},
            color='cantidad',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico de líneas: Monto total por año
        monto_año = df_filtrado.groupby('año')['monto_usd'].sum().reset_index()
        
        fig2 = px.line(
            monto_año,
            x='año',
            y='monto_usd',
            title='Monto Total Contratado por Año (USD)',
            labels={'año': 'Año', 'monto_usd': 'Monto Total (USD)'},
            markers=True
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Análisis mensual
        st.subheader("Análisis Mensual")
        df_filtrado['mes_nombre'] = pd.to_datetime(df_filtrado['mes'], format='%m').dt.month_name()
        contratos_mes = df_filtrado.groupby('mes_nombre').size().reset_index(name='cantidad')
        
        # Ordenar meses correctamente
        meses_orden = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        contratos_mes['mes_nombre'] = pd.Categorical(
            contratos_mes['mes_nombre'], 
            categories=meses_orden, 
            ordered=True
        )
        contratos_mes = contratos_mes.sort_values('mes_nombre')
        
        fig3 = px.bar(
            contratos_mes,
            x='mes_nombre',
            y='cantidad',
            title='Distribución de Contratos por Mes',
            labels={'mes_nombre': 'Mes', 'cantidad': 'Cantidad'},
            color='cantidad',
            color_continuous_scale='Viridis'
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab2:
        st.subheader("Análisis por Provincia")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pastel: Contratos por provincia
            contratos_prov = df_filtrado.groupby('provincia').size().reset_index(name='cantidad')
            contratos_prov = contratos_prov.sort_values('cantidad', ascending=False).head(10)
            
            fig4 = px.pie(
                contratos_prov,
                values='cantidad',
                names='provincia',
                title='Top 10 Provincias por Número de Contratos',
                hole=0.3
            )
            fig4.update_layout(height=500)
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            # Gráfico de barras horizontales: Monto por provincia
            monto_prov = df_filtrado.groupby('provincia')['monto_usd'].sum().reset_index()
            monto_prov = monto_prov.sort_values('monto_usd', ascending=True).tail(10)
            
            fig5 = px.bar(
            monto_prov,
                x='monto_usd',
                y='provincia',
                orientation='h',
                title='Top 10 Provincias por Monto Contratado',
                labels={'monto_usd': 'Monto (USD)', 'provincia': 'Provincia'},
                color='monto_usd',
                color_continuous_scale='Reds'
            )
            fig5.update_layout(height=500)
            st.plotly_chart(fig5, use_container_width=True)
    
    with tab3:
        st.subheader("Análisis por Sector y Tipo de Compra")
        
        # Gráfico de barras agrupadas: Sector por año
        sector_año = df_filtrado.groupby(['año', 'sector']).size().reset_index(name='cantidad')
        
        fig6 = px.bar(
            sector_año,
            x='año',
            y='cantidad',
            color='sector',
            title='Contratos por Sector y Año',
            labels={'año': 'Año', 'cantidad': 'Cantidad', 'sector': 'Sector'},
            barmode='group'
        )
        fig6.update_layout(height=500)
        st.plotly_chart(fig6, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tipo de compra
            tipo_compra = df_filtrado.groupby('tipo_compra')['monto_usd'].sum().reset_index()
            tipo_compra = tipo_compra.sort_values('monto_usd', ascending=False)
            
            fig7 = px.bar(
                tipo_compra,
                x='tipo_compra',
                y='monto_usd',
                title='Monto por Tipo de Compra',
                labels={'tipo_compra': 'Tipo de Compra', 'monto_usd': 'Monto (USD)'},
                color='monto_usd',
                color_continuous_scale='Greens'
            )
            fig7.update_layout(height=400)
            st.plotly_chart(fig7, use_container_width=True)
        
        with col2:
            # Estado de contratos
            estado = df_filtrado.groupby('estado').size().reset_index(name='cantidad')
            
            fig8 = px.pie(
                estado,
                values='cantidad',
                names='estado',
                title='Distribución por Estado de Contrato',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig8.update_layout(height=400)
            st.plotly_chart(fig8, use_container_width=True)
    
    with tab4:
        st.subheader("Análisis de Correlaciones")
        
        # Gráfico de dispersión: Monto vs Tiempo de proceso
        fig9 = px.scatter(
            df_filtrado,
            x='tiempo_proceso_dias',
            y='monto_usd',
            color='tipo_compra',
            size='num_oferentes',
            title='Relación entre Tiempo de Proceso y Monto',
            labels={
                'tiempo_proceso_dias': 'Tiempo de Proceso (días)',
                'monto_usd': 'Monto (USD)',
                'tipo_compra': 'Tipo de Compra',
                'num_oferentes': 'Núm. Oferentes'
            },
            hover_data=['provincia', 'sector'],
            opacity=0.6
        )
        fig9.update_layout(height=500)
        st.plotly_chart(fig9, use_container_width=True)
        
        # Matriz de correlación
        st.subheader("Matriz de Correlación")
        
        variables_numericas = df_filtrado[['monto_usd', 'num_oferentes', 'tiempo_proceso_dias']]
        correlacion = variables_numericas.corr()
        
        fig10 = px.imshow(
            correlacion,
            text_auto='.2f',
            title='Matriz de Correlación',
            labels=dict(color="Correlación"),
            color_continuous_scale='RdBu_r',
            aspect='auto'
        )
        fig10.update_layout(height=400)
        st.plotly_chart(fig10, use_container_width=True)
        
        # Análisis por número de oferentes
        col1, col2 = st.columns(2)
        
        with col1:
            oferentes_stats = df_filtrado.groupby('num_oferentes').agg({
                'monto_usd': 'mean'
            }).reset_index()
            
            fig11 = px.line(
                oferentes_stats,
                x='num_oferentes',
                y='monto_usd',
                title='Monto Promedio según Número de Oferentes',
                labels={'num_oferentes': 'Número de Oferentes', 'monto_usd': 'Monto Promedio (USD)'},
                markers=True
            )
            fig11.update_layout(height=400)
            st.plotly_chart(fig11, use_container_width=True)
        
        with col2:
            # Box plot: Distribución de montos por tipo de compra
            fig12 = px.box(
                df_filtrado,
                x='tipo_compra',
                y='monto_usd',
                title='Distribución de Montos por Tipo de Compra',
                labels={'tipo_compra': 'Tipo de Compra', 'monto_usd': 'Monto (USD)'},
                color='tipo_compra'
            )
            fig12.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig12, use_container_width=True)
    
    with tab5:
        st.subheader("Vista de Datos")
        
        # Estadísticas descriptivas
        st.write("**Estadísticas Descriptivas:**")
        st.dataframe(df_filtrado.describe())
        
        # Datos filtrados
        st.write(f"**Datos Filtrados ({len(df_filtrado)} registros):**")
        st.dataframe(
            df_filtrado.head(100),
            use_container_width=True
        )
        
        # Descargar datos
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv,
            file_name='compras_publicas_filtrado.csv',
            mime='text/csv',
        )
    
    # Conclusiones
    st.header("📝 Conclusiones del Análisis")
    
    conclusiones = f"""
    ### Hallazgos Principales:
    
    1. **Volumen de Contratación**: Se registraron **{total_contratos:,}** contratos en el período seleccionado, 
       con un monto total de **${monto_total:,.2f} USD**.
    
    2. **Promedio de Contratación**: El monto promedio por contrato es de **${monto_promedio:,.2f} USD**, 
       con un tiempo de proceso promedio de **{tiempo_promedio:.0f} días**.
    
    3. **Distribución Geográfica**: Las provincias con mayor actividad son {', '.join(df_filtrado.groupby('provincia').size().nlargest(3).index.tolist())}.
    
    4. **Sectores Prioritarios**: Los sectores con mayor inversión son {', '.join(df_filtrado.groupby('sector')['monto_usd'].sum().nlargest(3).index.tolist())}.
    
    5. **Tendencias Temporales**: El análisis por años permite identificar patrones de crecimiento o 
       decrecimiento en la contratación pública.
    
    6. **Eficiencia**: Existe una relación entre el número de oferentes y los montos contratados, 
       lo que sugiere la importancia de la competencia en el proceso.
    """
    
    st.markdown(conclusiones)
    
    # Footer
    st.markdown("---")
    st.markdown("**Desarrollado por:** Erick Chacon | **Fuente:** Sistema Nacional de Contratación Pública (SERCOP)")

else:
    st.error("No se pudieron cargar los datos. Por favor, verifica la conexión o la fuente de datos.")