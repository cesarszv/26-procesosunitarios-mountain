"""
app.py — Aplicación Streamlit: Cálculos Hidráulicos Interactivos
Proyecto de Procesos Unitarios — 5to Semestre

Visualización y análisis del sistema de transporte de agua
desde un río, cruzando una montaña, hasta una planta industrial.
"""
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

from core.hidraulica import (
    calcular_sistema_completo,
    area_seccion, velocidad, carga_cinetica,
    reynolds, f_colebrook, f_haaland, kw_a_hp,
)
from core.tramos import obtener_definicion_tramos, obtener_elevaciones_acumuladas
from core.datos import extraer_datos_completos
from visualizaciones.mapa_piezometrico import (
    crear_mapa_piezometrico,
    crear_desglose_perdidas,
    crear_grafico_potencia,
    crear_perfil_terreno_con_tramos,
)
from visualizaciones.modelo_3d import generar_modelo_tramo


# ====================================
# CONFIGURACIÓN DE LA PÁGINA
# ====================================
st.set_page_config(
    page_title="Cálculos Hidráulicos — Procesos Unitarios",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #334155;
    }
    
    /* Modern Metric Cards */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    .main .block-container {
        padding-top: 2.5rem;
        max-width: 1100px;
    }
    
    /* Typography improvements */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    h2 { 
        border-bottom: 1px solid #f1f5f9; 
        padding-bottom: 0.75rem; 
        margin-top: 2.5rem; 
    }
    
    /* Cleaner Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 0;
        background-color: transparent;
        border: none;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0;
        padding: 0 16px;
        border: none;
        border-bottom: 2px solid transparent;
        color: #64748b;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #0f172a;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #0f172a !important;
        border-bottom: 2px solid #0f172a !important;
        font-weight: 600;
    }
    
    /* Clean Expanders */
    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background-color: #ffffff;
    }
    [data-testid="stExpander"] > details > summary {
        padding: 14px 16px;
        font-weight: 500;
        color: #1e293b;
    }
    [data-testid="stExpander"] > details > summary:hover {
        color: #0f172a;
    }
    
    /* Button styles */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #cbd5e1;
        background-color: #f8fafc;
    }
    
    /* GitHub Button */
    .github-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background-color: #ffffff;
        color: #0f172a !important;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        text-decoration: none !important;
    }
    .github-btn:hover {
        background-color: #f8fafc;
        border-color: #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transform: translateY(-1px);
    }
    .github-btn svg {
        fill: #0f172a;
        transition: transform 0.2s ease;
    }
    .github-btn:hover svg {
        transform: scale(1.05);
    }
    
    /* Dev Card (Sidebar) */
    .dev-card {
        margin-top: 2rem;
        padding: 1.5rem 1rem;
        border-radius: 12px;
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .dev-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        opacity: 0.8;
    }
    .dev-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        transform: translateY(-2px);
    }
    .dev-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 0 1rem 0;
        font-weight: 600;
    }
    .dev-name {
        font-size: 0.95rem;
        color: #0f172a;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin: 0;
        line-height: 1.3;
    }
    .dev-divider {
        font-size: 0.8rem;
        color: #cbd5e1;
        margin: 0.35rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ====================================
# SIDEBAR
# ====================================

# --- Memoria de Cálculo ---
with st.sidebar.container(border=True):
    st.markdown(
        "<div style='text-align: center; padding: 5px 0;'>"
        "<h3 style='margin-top: 0; color: #0f172a; font-size: 1.05rem; font-weight: 600;'>Documentación</h3>"
        "<p style='font-size: 0.85em; color: #64748b; margin-bottom: 12px;'>"
        "Memoria de cálculo y justificación teórica."
        "</p>"
        "</div>", 
        unsafe_allow_html=True
    )
    
    informe_path = Path("source/INFORME_PROYECTO.docx")
    if informe_path.exists():
        with open(informe_path, "rb") as f:
            st.download_button(
                label="📥 Descargar Informe",
                data=f,
                file_name="INFORME_PROYECTO_Procesos_Unitarios.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
                key="sidebar_download_informe"
            )
        
        if st.button("👁️ Vista Previa", use_container_width=True, key="sidebar_preview"):
            st.session_state.preview_file = str(informe_path)
            st.session_state.preview_type = "docx"
            st.rerun()
    else:
        st.error("Archivo no encontrado")

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# --- Parámetros del Sistema ---
st.sidebar.title("Configuración")
st.sidebar.markdown(
    "<p style='color: #64748b; font-size: 0.85em; margin-bottom: 1.5rem;'>"
    "Ajuste los parámetros para recalcular las variables en tiempo real."
    "</p>", 
    unsafe_allow_html=True
)

st.sidebar.subheader("Tubería")
with st.sidebar.container(border=True):
    Q = st.slider(
        "Caudal Q (m³/s)",
        min_value=0.005, max_value=0.100, value=0.025, step=0.001,
        format="%.3f",
        help="Caudal volumétrico del flujo de agua"
    )
    Q_ls = Q * 1000  # L/s para mostrar
    st.caption(f"**Equivalente:** {Q_ls:.1f} L/s")
    
    st.divider()

    D = st.slider(
        "Diámetro D (m)",
        min_value=0.05, max_value=0.30, value=0.1541, step=0.001,
        format="%.4f",
        help="Diámetro interno de la tubería"
    )
    st.caption(f"**Equivalente:** {D*100:.1f} cm = {D*1000:.1f} mm")
    
    st.divider()

    epsilon = st.slider(
        "Rugosidad ε (m)",
        min_value=0.00001, max_value=0.001, value=0.000046, step=0.000001,
        format="%.6f",
        help="Rugosidad absoluta (acero comercial ≈ 0.046 mm)"
    )

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.subheader("Fluido")
with st.sidebar.container(border=True):
    rho = st.slider(
        "Densidad ρ (kg/m³)",
        min_value=900.0, max_value=1100.0, value=998.0, step=1.0,
        help="Densidad del agua a ~20°C = 998 kg/m³"
    )
    
    st.divider()
    
    mu = st.slider(
        "Viscosidad μ (Pa·s)",
        min_value=0.0005, max_value=0.0020, value=0.0010, step=0.0001,
        format="%.4f",
        help="Viscosidad dinámica del agua a ~20°C = 0.001 Pa·s"
    )

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.subheader("Visor 3D")
with st.sidebar.container(border=True):
    tramo_3d = st.selectbox(
        "Tramo a visualizar",
        options=list(range(1, 9)),
        index=0,
        format_func=lambda x: f"Tramo {x}",
        help="Selecciona el tramo para el modelo 3D interactivo"
    )

st.sidebar.markdown(
    """
    <div class="dev-card">
        <p class="dev-label">Desarrolladores</p>
        <div style="display: flex; flex-direction: column;">
            <p class="dev-name">Samuel Aguilera Araujo</p>
            <p class="dev-divider">✦</p>
            <p class="dev-name">Cesar Sebastian<br>Zambrana Ventura</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ====================================
# CÁLCULOS
# ====================================
@st.cache_data
def calcular(Q, D, rho, mu, epsilon):
    return calcular_sistema_completo(Q=Q, D=D, rho=rho, mu=mu, epsilon=epsilon)


resultados = calcular(Q, D, rho, mu, epsilon)

# Valores derivados globales
A = area_seccion(D)
v = velocidad(Q, A)
hv = carga_cinetica(v)
Re = reynolds(rho, v, D, mu)
f_col = f_colebrook(Re, epsilon, D)
f_haa = f_haaland(Re, epsilon, D)

# Potencia total del sistema
pot_total_kw = sum(r['potencia_kw'] for r in resultados.values())
pot_total_hp = kw_a_hp(pot_total_kw) if pot_total_kw > 0 else 0


# ====================================
# TÍTULO PRINCIPAL
# ====================================
col_title, col_github = st.columns([4, 1])

with col_title:
    st.markdown("<h1 style='color: #0f172a; font-weight: 800; font-size: 2.2rem; letter-spacing: -0.03em; margin-bottom: 0;'>Sistema Hidráulico</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #64748b; font-weight: 400; font-size: 1.2rem; margin-top: 0.2rem; margin-bottom: 1.5rem;'>Dashboard de Análisis Dinámico</h3>", unsafe_allow_html=True)

with col_github:
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='display: flex; justify-content: flex-end;'>
            <a href="https://github.com/samuelthecreat/PROCESOS_UNITARIOS---PROYECTO_MOUNTAIN" target="_blank" class="github-btn">
                <svg height="18" width="18" viewBox="0 0 16 16">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
                <span>GitHub</span>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    "Este panel permite simular y analizar el transporte de agua desde una fuente natural, "
    "cruzando una montaña, hasta una planta industrial ubicada a **3.4 km** de distancia."
)

# ====================================
# KPIs PRINCIPALES
# ====================================
st.markdown("<h4 style='color: #334155; font-weight: 600; margin-top: 1.5rem; margin-bottom: 1rem; font-size: 1.1rem;'>Indicadores Principales</h4>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Velocidad del Fluido", f"{v:.2f} m/s", help="v = Q/A")
with col2:
    regimen = "Turbulento" if Re > 4000 else ("Transición" if Re > 2300 else "Laminar")
    st.metric("Régimen de Flujo", regimen, f"Re = {Re:,.0f}")
with col3:
    st.metric("Factor de Fricción (f)", f"{f_col:.5f}", help="Ecuación de Colebrook-White")
with col4:
    st.metric("Potencia Total Requerida", f"{pot_total_kw:.1f} kW", f"{pot_total_hp:.1f} HP")

st.markdown("<br>", unsafe_allow_html=True)

# ====================================
# PESTAÑAS PRINCIPALES
# ====================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Mapa Piezométrico",
    "Perfil Topográfico",
    "Análisis de Pérdidas",
    "Modelo 3D",
    "Datos Origines",
    "Documentación Formal",
])


# ==============================
# TAB 1: MAPA PIEZOMÉTRICO
# ==============================
with tab1:
    st.header("Mapa Piezométrico del Sistema")
    st.markdown(
        "Visualización de las **líneas de energía (EGL)** y **gradiente hidráulico (HGL)** "
        "a lo largo de todo el sistema. Los saltos verdes representan la energía agregada por "
        "las bombas; las pérdidas graduales son por fricción y accesorios."
    )
    
    fig_piezo = crear_mapa_piezometrico(resultados, Q, D)
    st.plotly_chart(fig_piezo, use_container_width=True)
    
    st.info(
        "**Análisis de presiones:** La presión manométrica (panel inferior) debe mantenerse por encima de cero "
        "para mitigar el riesgo de cavitación. Las estaciones de bombeo introducen energía al sistema, mientras "
        "que la rugosidad de la tubería y los accesorios instalados generan una disipación paulatina."
    )


# ==============================
# TAB 2: PERFIL DEL TERRENO
# ==============================
with tab2:
    st.header("Perfil Topográfico y Tramos")
    st.markdown(
        "El sistema cruza una montaña con elevaciones de hasta **500 m** sobre el nivel del río. "
        "Los tramos ascendentes requieren bombeo; los descendentes usan válvulas de estrangulamiento."
    )
    
    fig_terreno = crear_perfil_terreno_con_tramos(resultados)
    st.plotly_chart(fig_terreno, use_container_width=True)
    
    # Tabla resumen de tramos
    st.subheader("Resumen de Tramos")
    
    definiciones = obtener_definicion_tramos()
    tabla_tramos = []
    for i in range(1, 9):
        d = definiciones[i]
        r = resultados[i]
        tabla_tramos.append({
            'Tramo': i,
            'Distancia (m)': f"{d['distancia']:.1f}",
            'Altura (m)': f"{d['altura']:.0f}",
            'Pendiente (°)': f"{d['pendiente']:.1f}",
            'L. Tubería (m)': f"{d['longitud_tuberia']:.1f}",
            'Tipo': d['tipo'].replace('_', ' ').title(),
            'N° Estaciones': d['num_estaciones'],
            'Potencia (kW)': f"{r['potencia_kw']:.2f}",
            'Potencia (HP)': f"{r['potencia_hp']:.2f}",
        })
    
    st.dataframe(
        pd.DataFrame(tabla_tramos),
        use_container_width=True,
        hide_index=True,
    )
    
    # Datos del mapa topográfico
    with st.expander("📐 Datos del perfil topográfico (mapa original)"):
        datos = extraer_datos_completos()
        st.dataframe(datos['perfil_terreno'], use_container_width=True)
        st.json(datos['parametros'])


# ==============================
# TAB 3: ANÁLISIS DE PÉRDIDAS
# ==============================
with tab3:
    st.header("Análisis de Pérdidas y Potencia")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Desglose de Pérdidas")
        fig_perdidas = crear_desglose_perdidas(resultados)
        st.plotly_chart(fig_perdidas, use_container_width=True)
    
    with col_right:
        st.subheader("Potencia por Tramo")
        fig_potencia = crear_grafico_potencia(resultados)
        st.plotly_chart(fig_potencia, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla detallada de cálculos hidráulicos
    st.subheader("Cálculos Hidráulicos Detallados")
    
    tabla_hidraulica = []
    for i in range(1, 9):
        r = resultados[i]
        tabla_hidraulica.append({
            'Tramo': f"T{i}",
            'Área (m²)': f"{r['area']:.5f}",
            'v (m/s)': f"{r['velocidad']:.3f}",
            'hv (m)': f"{r['carga_cinetica']:.4f}",
            'Re': f"{r['reynolds']:,.0f}",
            'f Colebrook': f"{r['f_colebrook']:.6f}",
            'f Haaland': f"{r['f_haaland']:.6f}",
            'hf fricción (m)': f"{r['perdidas_friccion_colebrook']:.4f}",
            'hm menores (m)': f"{r['perdidas_menores']:.4f}",
            'H estación (m)': f"{r['carga_estacion']:.2f}",
            'H total (m)': f"{r['carga_total']:.2f}",
            'P (kW)': f"{r['potencia_kw']:.2f}",
            'P (HP)': f"{r['potencia_hp']:.2f}",
        })
    
    st.dataframe(
        pd.DataFrame(tabla_hidraulica),
        use_container_width=True,
        hide_index=True,
    )
    
    # Comparación de factores de fricción
    st.subheader("Comparación de Factores de Fricción")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Colebrook-White", f"{f_col:.6f}", help="Ecuación implícita (iterativa)")
    with col_f2:
        st.metric("Haaland", f"{f_haa:.6f}", delta=f"{(f_haa - f_col)/f_col*100:.2f}%")
    with col_f3:
        from core.hidraulica import f_swamee_jain
        f_swa = f_swamee_jain(Re, epsilon, D)
        st.metric("Swamee-Jain", f"{f_swa:.6f}", delta=f"{(f_swa - f_col)/f_col*100:.2f}%")
    
    # Accesorios por tramo
    st.markdown("---")
    st.subheader("Accesorios por Tramo")
    
    acc_tramo_sel = st.selectbox(
        "Seleccionar tramo", range(1, 9),
        format_func=lambda x: f"Tramo {x}",
        key="acc_tramo"
    )
    
    defn = definiciones[acc_tramo_sel]
    acc_df = pd.DataFrame(defn['accesorios'])
    if not acc_df.empty:
        acc_df['carga (m)'] = acc_df['cantidad'] * acc_df['K'] * hv
        st.dataframe(acc_df, use_container_width=True, hide_index=True)
        st.caption(f"K total = {defn['K_total']:.2f} | Pérdida total accesorios = {defn['K_total'] * hv:.4f} m")
    
    if defn.get('notas'):
        st.info(f"**Observación técnica:** {defn['notas']}")


# ==============================
# TAB 4: MODELO 3D
# ==============================
with tab4:
    st.header(f"Modelo 3D — Tramo {tramo_3d}")
    
    defn_3d = definiciones[tramo_3d]
    r_3d = resultados[tramo_3d]
    
    # Indicadores del tramo seleccionado
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Longitud", f"{defn_3d['longitud_tuberia']:.1f} m")
    with c2:
        st.metric("Pendiente", f"{defn_3d['pendiente']:.1f}°")
    with c3:
        st.metric("Tipo", defn_3d['tipo'].replace('_', ' ').title())
    with c4:
        st.metric("Potencia", f"{r_3d['potencia_kw']:.2f} kW")
    
    st.markdown(
        "**Instrucciones:** Arrastra para rotar | Scroll para zoom | "
        "Click derecho para desplazar la vista."
    )
    
    # Generar y renderizar modelo 3D
    html_3d = generar_modelo_tramo(tramo_3d, resultados)
    components.html(html_3d, height=720, scrolling=False)
    
    st.caption(
        f"El gradiente de color en la tubería representa la caída de presión: "
        f"**azul** = alta presión (entrada) → **rojo** = baja presión (salida). "
        f"Las partículas celestes representan el flujo de agua a {r_3d['velocidad']:.2f} m/s."
    )
    
    if defn_3d.get('notas'):
        st.info(f"**Observación técnica:** {defn_3d['notas']}")


# ==============================
# TAB 5: DATOS DETALLADOS
# ==============================
with tab5:
    st.header("Datos de Origen (CSV)")
    st.markdown("Consulta de los datos técnicos extraídos del diseño.")
    
    datos = extraer_datos_completos()
    
    with st.expander("📐 Perfil del Terreno", expanded=False):
        st.dataframe(datos['perfil_terreno'], use_container_width=True)
    
    with st.expander("📊 Parámetros Globales", expanded=False):
        params = datos['parametros']
        st.json(params)
    
    with st.expander("📏 Resumen de Tramos (CSV original)", expanded=False):
        st.dataframe(datos['resumen_tramos'], use_container_width=True)
    
    with st.expander("🔧 Tramo 8 — Sub-segmentos", expanded=False):
        st.dataframe(datos['tramo_8_distancias'], use_container_width=True)
    
    with st.expander("📋 Datos Detallados por Tramo (CSV original)", expanded=True):
        tramo_csv = st.selectbox(
            "Seleccionar tramo", range(1, 9),
            format_func=lambda x: f"Tramo {x}",
            key="csv_tramo"
        )
        detalle = datos['tramos_detalle'][tramo_csv]
        
        # Mostrar parámetros del tramo
        params_tramo = {k: v for k, v in detalle.items()
                       if k not in ('accesorios',)}
        col1_d, col2_d = st.columns(2)
        with col1_d:
            st.markdown("**Parámetros calculados (CSV)**")
            for k, v in params_tramo.items():
                if isinstance(v, float):
                    st.text(f"  {k}: {v}")
                else:
                    st.text(f"  {k}: {v}")
        
        with col2_d:
            st.markdown("**Parámetros recalculados (Python)**")
            r_comp = resultados[tramo_csv]
            for k in ['area', 'velocidad', 'carga_cinetica', 'reynolds',
                      'f_colebrook', 'f_haaland', 'perdidas_friccion_colebrook',
                      'perdidas_menores', 'carga_total', 'potencia_kw', 'potencia_hp']:
                if k in r_comp:
                    st.text(f"  {k}: {r_comp[k]:.6f}" if isinstance(r_comp[k], float) else f"  {k}: {r_comp[k]}")
        
        # Accesorios del CSV
        if 'accesorios' in detalle and isinstance(detalle['accesorios'], pd.DataFrame):
            if not detalle['accesorios'].empty:
                st.markdown("**Accesorios (CSV)**")
                st.dataframe(detalle['accesorios'], use_container_width=True, hide_index=True)
    
    # Fórmulas empleadas
    with st.expander("📖 Fórmulas Empleadas", expanded=False):
        st.markdown(r"""
        ### Ecuaciones Fundamentales
        
        **Área de la sección:**
        $$A = \frac{\pi D^2}{4}$$
        
        **Velocidad del flujo:**
        $$v = \frac{Q}{A}$$
        
        **Carga cinética:**
        $$h_v = \frac{v^2}{2g}$$
        
        **Número de Reynolds:**
        $$Re = \frac{\rho \cdot v \cdot D}{\mu}$$
        
        **Ecuación de Colebrook-White** (implícita):
        $$\frac{1}{\sqrt{f}} = -2\log_{10}\left(\frac{\varepsilon/D}{3.7} + \frac{2.51}{Re\sqrt{f}}\right)$$
        
        **Correlación de Haaland** (explícita):
        $$\frac{1}{\sqrt{f}} = -1.8\log_{10}\left[\left(\frac{\varepsilon/D}{3.7}\right)^{1.11} + \frac{6.9}{Re}\right]$$
        
        **Pérdidas por fricción (Darcy-Weisbach):**
        $$h_f = f \cdot \frac{L}{D} \cdot \frac{v^2}{2g}$$
        
        **Pérdidas menores (accesorios):**
        $$h_m = \sum K \cdot \frac{v^2}{2g}$$
        
        **Carga total:**
        $$H = z + h_f + h_m$$
        
        **Potencia de la bomba:**
        $$P = \rho \cdot g \cdot Q \cdot H \quad \text{[W]}$$
        """)


# ==============================
# VISOR DE DOCUMENTOS
# ==============================
@st.dialog("📖 Visor de Documentos", width="large")
def visor_documento(file_path, file_type):
    st.markdown("""
        <style>
        .doc-paper {
            background-color: #ffffff;
            padding: 2rem 3rem;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
            color: #334155;
            font-family: 'Inter', -apple-system, sans-serif;
            line-height: 1.6;
        }
        .doc-paper h1, .doc-paper h2, .doc-paper h3 {
            color: #0f172a;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 0.5rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .doc-paper table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }
        .doc-paper th, .doc-paper td {
            border: 1px solid #cbd5e1;
            padding: 0.75rem;
            text-align: left;
        }
        .doc-paper th {
            background-color: #f8fafc;
            font-weight: 600;
        }
        .doc-paper p {
            margin-bottom: 1.2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.caption(f"**Archivo:** `{Path(file_path).name}`")

    with st.container(height=650):
        if file_type == "docx":
            try:
                import mammoth
                with st.spinner("Renderizando documento..."):
                    with open(file_path, "rb") as docx_file:
                        result = mammoth.convert_to_html(docx_file)
                        html_content = result.value

                    st.markdown(
                        f"<div class='doc-paper'>{html_content}</div>",
                        unsafe_allow_html=True
                    )
            except ImportError:
                st.error("Librería 'mammoth' no instalada. Ejecute `pip install mammoth`.")
            except Exception as e:
                st.error(f"Error al cargar el documento: {e}\n\nAsegúrese de que el archivo es un documento .docx válido (no .md renombrado).")

        elif file_type == "md":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    md_content = f.read()

                # Para el markdown nativo, aplicamos estilos mediante un contenedor con borde
                with st.container():
                    st.markdown(md_content)
            except Exception as e:
                st.error(f"Error al cargar el documento: {e}")

    if st.button("Cerrar Visor", type="secondary", use_container_width=True):
        st.rerun()

# Lógica compartida para invocar el modal
if "preview_file" in st.session_state and st.session_state.preview_file:
    visor_documento(st.session_state.preview_file, st.session_state.preview_type)
    st.session_state.preview_file = None
# ==============================
# TAB 6: DOCUMENTACIÓN
# ==============================
with tab6:
    st.header("Documentación Formal")
    st.markdown(
        "Sección dedicada a la revisión técnica del proyecto. "
        "A continuación se encuentra disponible el informe completo y la memoria de cálculo interactiva."
    )
    
    st.divider()
    
    col_doc1, col_doc2 = st.columns([2, 1])
    
    with col_doc1:
        st.subheader("📖 Vista Previa del Proyecto")
        
        # Leemos el archivo markdown del proyecto para la vista previa principal
        md_path = Path("media/docs/PROYECTO.MD")
        md_content = "⚠️ Contenido no disponible."
        if md_path.exists():
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
                
        # Contenedor con scroll tipo "hoja de papel"
        with st.container(height=600, border=True):
            st.markdown(
                "<style> "
                ".stMarkdown { font-family: 'Inter', sans-serif; color: #334155; } "
                "</style>", 
                unsafe_allow_html=True
            )
            st.markdown(md_content)
            
        if st.button("🔍 Abrir en Visor Completo", key="preview_md"):
            st.session_state.preview_file = str(md_path)
            st.session_state.preview_type = "md"
            st.rerun()
        
    with col_doc2:
        st.subheader("📥 Descargas")
        with st.container(border=True):
            st.markdown(
                """
                <div style="text-align: center; padding: 25px 10px;">
                    <h4 style="margin: 0; color: #0f172a; font-size: 1.15rem; font-weight: 700;">INFORME TÉCNICO</h4>
                    <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px; margin-bottom: 20px;">Formato: Word (.docx)<br>Memoria de cálculo completa y fundamentación técnica.</p>
                </div>
                """, unsafe_allow_html=True
            )
            
            informe_path_tab = Path("source/INFORME_PROYECTO.docx")
            if informe_path_tab.exists():
                with open(informe_path_tab, "rb") as f:
                    st.download_button(
                        label="Descargar Documento",
                        data=f,
                        file_name="INFORME_PROYECTO_Procesos_Unitarios.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                        key="main_download_informe"
                    )
                
                if st.button("👁️ Vista Previa", use_container_width=True, key="main_preview"):
                    st.session_state.preview_file = str(informe_path_tab)
                    st.session_state.preview_type = "docx"
                    st.rerun()
            else:
                st.error("⚠️ Documento no disponible.")

# ====================================
# FOOTER
# ====================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; padding: 1rem 0 2rem 0; font-family: "Inter", sans-serif;'>
        <p style='color: #64748b; font-size: 0.8rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.75rem;'>
            Desarrolladores
        </p>
        <p style='color: #0f172a; font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem; letter-spacing: -0.01em;'>
            Samuel Aguilera Araujo <span style='color: #cbd5e1; font-weight: 400; margin: 0 0.75rem;'>|</span> Cesar Sebastian Zambrana Ventura
        </p>
        <p style='color:#94a3b8; font-size:0.85rem; margin-top: 1.5rem;'>
            Proyecto de Procesos Unitarios — 5to Semestre <br>
            <span style='font-size: 0.75rem;'>Python • Pandas • Plotly • Three.js • Streamlit</span>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
