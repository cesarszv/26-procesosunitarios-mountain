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
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado para Tema Dark Engineering
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #f1f5f9; /* Slate 100 */
        background-color: #0a0f1e; /* Darkest Navy */
    }

    /* Global Backgrounds */
    .stApp {
        background-color: #0a0f1e;
    }
    
    /* Modern Metric Cards */
    [data-testid="stMetric"] {
        background-color: #111827; /* Gray 900 */
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
        border: 1px solid #1f2937; /* Gray 800 */
        transition: all 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: #38bdf8; /* Sky 400 */
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5);
    }
    
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important; /* Sky 400 */
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important; /* Slate 400 */
        font-size: 0.9rem;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 0;
        background-color: transparent;
        border: none;
        border-bottom: 1px solid #1f2937;
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
        color: #e2e8f0;
        border-bottom: 2px solid #475569;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #38bdf8 !important; /* Sky 400 */
        border-bottom: 2px solid #38bdf8 !important;
        font-weight: 600;
    }
    
    /* Expander Styling */
    [data-testid="stExpander"] {
        border: 1px solid #1f2937;
        border-radius: 8px;
        background-color: #111827; /* Gray 900 */
    }
    [data-testid="stExpander"] > details > summary {
        color: #e2e8f0;
        font-weight: 500;
    }
    [data-testid="stExpander"] > details > summary:hover {
        color: #38bdf8;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #334155;
        background-color: #1e293b;
        color: #e2e8f0;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #38bdf8;
        color: #38bdf8;
        background-color: #0f172a;
    }

    /* GitHub Button Custom */
    .github-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background-color: #1e293b;
        color: #e2e8f0 !important;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        border: 1px solid #334155;
        text-decoration: none !important;
    }
    .github-btn:hover {
        background-color: #0f172a;
        border-color: #38bdf8;
        color: #38bdf8 !important;
        transform: translateY(-1px);
    }
    .github-btn svg {
        fill: #e2e8f0;
        transition: fill 0.2s ease;
    }
    .github-btn:hover svg {
        fill: #38bdf8;
    }
    
    /* Dev Card (Sidebar) */
    .dev-card {
        margin-top: 2rem;
        padding: 1.5rem 1rem;
        border-radius: 12px;
        background: linear-gradient(145deg, #111827, #0f172a);
        border: 1px solid #1f2937;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .dev-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    }
    .dev-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .dev-name {
        font-size: 0.95rem;
        color: #f1f5f9;
        font-weight: 600;
        margin: 0;
        line-height: 1.4;
    }
    .dev-divider {
        font-size: 0.8rem;
        color: #475569;
        margin: 0.5rem 0;
    }

    /* Hero Section */
    .hero-container {
        background: linear-gradient(to right, #0f172a, #1e293b);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #1e293b;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .hero-icon {
        font-size: 3rem;
        background: rgba(56, 189, 248, 0.1);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
    .hero-text h1 {
        color: #f8fafc;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #f8fafc, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-text p {
        color: #94a3b8;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ====================================
# SESSION STATE & INIT
# ====================================
# Valores por defecto
DEFAULTS = {
    "Q": 0.025,
    "D": 0.1541,
    "epsilon": 0.000046,
    "rho": 998.0,
    "mu": 0.0010
}

# Inicializar estado si no existe
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

def reset_defaults():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()

# ====================================
# SIDEBAR REFACTORED
# ====================================

# --- Header Sidebar ---
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="background: #38bdf8; width: 4px; height: 24px; border-radius: 2px;"></div>
            <h2 style="margin: 0; border: none; padding: 0; font-size: 1.2rem; color: #f1f5f9;">Configuración</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.button("↺ Restaurar Valores por Defecto", on_click=reset_defaults, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

# --- Controles Agrupados ---
with st.sidebar:
    # 1. Tubería
    with st.expander("🔧 Parámetros de Tubería", expanded=True):
        st.session_state.Q = st.slider(
            "Caudal Q (m³/s)",
            min_value=0.005, max_value=0.100, step=0.001,
            value=st.session_state.Q,
            format="%.3f",
            help="Caudal volumétrico que transporta el sistema."
        )
        st.caption(f"💧 **{st.session_state.Q * 1000:.1f} L/s**")

        st.divider()

        st.session_state.D = st.slider(
            "Diámetro D (m)",
            min_value=0.05, max_value=0.30, step=0.001,
            value=st.session_state.D,
            format="%.4f",
            help="Diámetro interno de la tubería."
        )
        st.caption(f"📏 **{st.session_state.D * 1000:.1f} mm**")

        st.divider()

        st.session_state.epsilon = st.slider(
            "Rugosidad ε (m)",
            min_value=0.00001, max_value=0.001, step=0.000001,
            value=st.session_state.epsilon,
            format="%.6f",
            help="Rugosidad absoluta del material (Acero comercial ≈ 0.000046 m)"
        )

    # 2. Fluido
    with st.expander("💧 Propiedades del Fluido", expanded=False):
        st.session_state.rho = st.slider(
            "Densidad ρ (kg/m³)",
            min_value=900.0, max_value=1100.0, step=1.0,
            value=st.session_state.rho,
            help="Densidad del agua (dependiente de T°)"
        )

        st.session_state.mu = st.slider(
            "Viscosidad μ (Pa·s)",
            min_value=0.0005, max_value=0.0020, step=0.0001,
            value=st.session_state.mu,
            format="%.4f",
            help="Viscosidad dinámica del agua"
        )

    # 3. Visor 3D
    with st.expander("🧊 Configuración 3D", expanded=False):
        tramo_3d = st.selectbox(
            "Tramo a visualizar",
            options=list(range(1, 9)),
            index=0,
            format_func=lambda x: f"Tramo {x}",
            help="Selecciona el tramo para inspeccionar en detalle."
        )

    # --- Mini Resumen ---
    st.markdown("---")
    st.markdown("<p class='dev-label' style='margin-bottom: 0.5rem;'>Estado del Flujo (Tramo 1)</p>", unsafe_allow_html=True)
    
    # Calculamos preliminarmente para el sidebar
    _A = area_seccion(st.session_state.D)
    _v = velocidad(st.session_state.Q, _A)
    _Re = reynolds(st.session_state.rho, _v, st.session_state.D, st.session_state.mu)
    _regimen = "Turbulento" if _Re > 4000 else ("Transición" if _Re > 2300 else "Laminar")
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric("Reynolds", f"{_Re:,.0f}", label_visibility="visible")
    with col_res2:
        st.metric("Régimen", _regimen, label_visibility="visible")

    # --- Footer Sidebar ---
    st.markdown(
        """
        <div class="dev-card">
            <p class="dev-label">Equipo de Ingeniería</p>
            <div style="display: flex; flex-direction: column;">
                <p class="dev-name">Samuel Aguilera</p>
                <p class="dev-divider">✦</p>
                <p class="dev-name">Cesar Zambrana</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ====================================
# CÁLCULOS CENTRALIZADOS
# ====================================
@st.cache_data
def calcular(Q, D, rho, mu, epsilon):
    return calcular_sistema_completo(Q=Q, D=D, rho=rho, mu=mu, epsilon=epsilon)

resultados = calcular(
    st.session_state.Q,
    st.session_state.D,
    st.session_state.rho,
    st.session_state.mu,
    st.session_state.epsilon
)

# Valores derivados globales
A = area_seccion(st.session_state.D)
v = velocidad(st.session_state.Q, A)
hv = carga_cinetica(v)
Re = reynolds(st.session_state.rho, v, st.session_state.D, st.session_state.mu)
f_col = f_colebrook(Re, st.session_state.epsilon, st.session_state.D)
f_haa = f_haaland(Re, st.session_state.epsilon, st.session_state.D)

# Potencia total
pot_total_kw = sum(r['potencia_kw'] for r in resultados.values())
pot_total_hp = kw_a_hp(pot_total_kw) if pot_total_kw > 0 else 0


# ====================================
# HEADER / HERO SECTION
# ====================================
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-icon">🏔️</div>
        <div class="hero-text">
            <h1>Sistema Hidráulico Montañoso</h1>
            <p>Simulación de transporte de fluidos: Río → Montaña → Planta Industrial</p>
        </div>
        <div style="flex-grow: 1;"></div>
        <a href="https://github.com/samuelthecreat/PROCESOS_UNITARIOS---PROYECTO_MOUNTAIN" target="_blank" class="github-btn">
            <svg height="20" width="20" viewBox="0 0 16 16">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
            Repositorio
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# Metrics Bar
cols = st.columns(4)
with cols[0]:
    st.metric("Caudal de Diseño", f"{st.session_state.Q*1000:.1f} L/s", "Constante")
with cols[1]:
    st.metric("Potencia Total", f"{pot_total_kw:.1f} kW", f"{pot_total_hp:.1f} HP")
with cols[2]:
    st.metric("Elevación Máxima", "500 m", "Tramo 4")
with cols[3]:
    st.metric("Longitud Total", "3.4 km", "8 Tramos")

st.markdown("<br>", unsafe_allow_html=True)

# ====================================
# TABS PRINCIPALES
# ====================================
tab_home, tab_map, tab_terrain, tab_loss, tab_3d, tab_data, tab_docs = st.tabs([
    "🏠 Inicio",
    "📈 Mapa Piezométrico",
    "🏔️ Perfil Topográfico",
    "📉 Análisis de Pérdidas",
    "🧊 Modelo 3D",
    "📊 Datos Detallados",
    "📑 Documentación"
])


# ==============================
# TAB HOME: Resumen
# ==============================
with tab_home:
    col_h1, col_h2 = st.columns([1, 1])
    with col_h1:
        st.markdown("### 📋 Resumen del Proyecto")
        st.markdown(
            """
            Este simulador modela el comportamiento hidráulico de un sistema de tuberías que transporta agua
            desde una captación en un río (cota 0), atravesando una cadena montañosa (cota 500m), hasta llegar
            a una planta industrial.

            **Objetivos de la Simulación:**
            *   Analizar las **pérdidas de carga** por fricción y accesorios.
            *   Determinar la **potencia de bombeo** requerida en tramos de ascenso.
            *   Evaluar la **presión manométrica** para evitar cavitación.
            *   Visualizar el comportamiento del flujo en **3D**.
            """
        )
        st.info("💡 Usa el panel lateral para modificar el Caudal, Diámetro y propiedades del fluido.")

    with col_h2:
        # Placeholder for schematic diagram (using Mermaid for now as it's purely code-based)
        st.markdown("### 🗺️ Esquema del Sistema")
        st.markdown(
            """
            ```mermaid
            graph LR
                R[Río (0m)] -->|Bombeo| T1(Tramo 1)
                T1 -->|Bombeo| T2(Tramo 2)
                T2 -->|Bombeo| T3(Tramo 3)
                T3 -->|Plano| T4(Cima 500m)
                T4 -->|Gravedad| T5(Bajada)
                T5 -->|Gravedad| T6(Bajada Fuerte)
                T6 -->|Gravedad| T7(Bajada)
                T7 -->|Subterráneo| T8(Planta Industrial)

                style R fill:#0ea5e9,stroke:#0369a1,color:white
                style T4 fill:#eab308,stroke:#a16207,color:white
                style T8 fill:#a855f7,stroke:#7e22ce,color:white
            ```
            """
        )


# ==============================
# TAB 1: MAPA PIEZOMÉTRICO
# ==============================
with tab_map:
    st.markdown("### Líneas de Energía y Gradiente Hidráulico")
    st.caption("Visualización de las presiones a lo largo de todo el recorrido. La línea **cian (EGL)** representa la energía total y la **amarilla (HGL)** el gradiente hidráulico.")
    
    st.info(
        "**Interpretación:** La diferencia vertical entre la línea de energía (EGL) y la tubería representa la presión disponible. "
        "Si la línea de gradiente hidráulico (HGL) cruza por debajo de la tubería, existe riesgo de **presión negativa y cavitación**."
    )

    fig_piezo = crear_mapa_piezometrico(resultados, st.session_state.Q, st.session_state.D)
    st.plotly_chart(fig_piezo, use_container_width=True)


# ==============================
# TAB 2: PERFIL DEL TERRENO
# ==============================
with tab_terrain:
    st.markdown("### Perfil Topográfico")
    st.caption("Elevación del terreno y segmentación por tramos. Colores indican la función del tramo (Bombeo, Gravedad, Plano).")
    
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
            'Distancia (m)': d['distancia'],
            'Altura (m)': d['altura'],
            'Pendiente (°)': d['pendiente'],
            'L. Tubería (m)': d['longitud_tuberia'],
            'Tipo': d['tipo'].replace('_', ' ').title(),
            'Potencia (kW)': r['potencia_kw'],
        })
    
    st.dataframe(
        pd.DataFrame(tabla_tramos),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tramo": st.column_config.NumberColumn(format="%d"),
            "Distancia (m)": st.column_config.NumberColumn(format="%.1f m"),
            "Altura (m)": st.column_config.NumberColumn(format="%d m"),
            "Pendiente (°)": st.column_config.NumberColumn(format="%.1f°"),
            "L. Tubería (m)": st.column_config.NumberColumn(format="%.1f m"),
            "Potencia (kW)": st.column_config.ProgressColumn(
                format="%.2f kW", min_value=0, max_value=max(t['Potencia (kW)'] for t in tabla_tramos),
            ),
        }
    )


# ==============================
# TAB 3: ANÁLISIS DE PÉRDIDAS
# ==============================
with tab_loss:
    st.markdown("### Análisis de Eficiencia y Pérdidas")
    
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Desglose de Pérdidas")
        fig_perdidas = crear_desglose_perdidas(resultados)
        st.plotly_chart(fig_perdidas, use_container_width=True)
    
    with col_right:
        st.subheader("Consumo de Potencia")
        fig_potencia = crear_grafico_potencia(resultados)
        st.plotly_chart(fig_potencia, use_container_width=True)
    
    st.markdown("---")
    
    # Accesorios
    st.subheader("Detalle de Accesorios por Tramo")
    acc_tramo_sel = st.selectbox(
        "Seleccionar tramo para ver accesorios", range(1, 9),
        format_func=lambda x: f"Tramo {x}",
        key="acc_tramo_loss"
    )
    defn = definiciones[acc_tramo_sel]
    acc_df = pd.DataFrame(defn['accesorios'])
    if not acc_df.empty:
        acc_df['Pérdida (m)'] = acc_df['cantidad'] * acc_df['K'] * hv
        st.dataframe(
            acc_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Pérdida (m)": st.column_config.NumberColumn(format="%.4f m"),
                "K": st.column_config.NumberColumn(format="%.2f")
            }
        )
    else:
        st.info("Este tramo no tiene accesorios registrados.")


# ==============================
# TAB 4: MODELO 3D
# ==============================
with tab_3d:
    st.markdown(f"### Visualización 3D: Tramo {tramo_3d}")
    
    defn_3d = definiciones[tramo_3d]
    r_3d = resultados[tramo_3d]
    
    # KPIs visuales sobre el canvas
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Longitud", f"{defn_3d['longitud_tuberia']:.1f} m")
    kpi2.metric("Pendiente", f"{defn_3d['pendiente']:.1f}°")
    kpi3.metric("Tipo", defn_3d['tipo'].replace('_', ' ').title())
    kpi4.metric("Potencia", f"{r_3d['potencia_kw']:.2f} kW")

    # Render 3D
    html_3d = generar_modelo_tramo(tramo_3d, resultados)
    components.html(html_3d, height=720, scrolling=False)
    
    st.caption(
        "**Leyenda Visual:** El gradiente de color (Azul → Rojo) indica la caída de presión a lo largo del tramo. "
        "Las partículas blancas representan el flujo turbulento del agua."
    )

    if defn_3d.get('notas'):
        st.info(f"**Nota Técnica:** {defn_3d['notas']}")


# ==============================
# TAB 5: DATOS DETALLADOS
# ==============================
with tab_data:
    st.markdown("### Tablas de Datos y Fórmulas")
    
    datos = extraer_datos_completos()
    
    with st.expander("📐 Perfil del Terreno (Raw Data)", expanded=False):
        st.dataframe(datos['perfil_terreno'], use_container_width=True)

    with st.expander("📋 Tabla General de Resultados", expanded=True):
        tabla_completa = []
        for i in range(1, 9):
            r = resultados[i]
            tabla_completa.append({
                "Tramo": i,
                "Velocidad (m/s)": r['velocidad'],
                "Reynolds": r['reynolds'],
                "f (Colebrook)": r['f_colebrook'],
                "hf (m)": r['perdidas_friccion_colebrook'],
                "hm (m)": r['perdidas_menores'],
                "H Total (m)": r['carga_total']
            })
        
        st.dataframe(
            pd.DataFrame(tabla_completa),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Tramo": st.column_config.NumberColumn(format="%d"),
                "Velocidad (m/s)": st.column_config.NumberColumn(format="%.3f"),
                "Reynolds": st.column_config.NumberColumn(format="%.0f"),
                "f (Colebrook)": st.column_config.NumberColumn(format="%.6f"),
                "hf (m)": st.column_config.NumberColumn(format="%.4f"),
                "hm (m)": st.column_config.NumberColumn(format="%.4f"),
                "H Total (m)": st.column_config.NumberColumn(format="%.2f"),
            }
        )

    st.markdown("#### Fórmulas Utilizadas")
    fc1, fc2 = st.columns(2)
    with fc1:
        st.latex(r"Re = \frac{\rho \cdot v \cdot D}{\mu}")
        st.latex(r"\frac{1}{\sqrt{f}} = -2\log_{10}\left(\frac{\varepsilon/D}{3.7} + \frac{2.51}{Re\sqrt{f}}\right)")
    with fc2:
        st.latex(r"h_f = f \cdot \frac{L}{D} \cdot \frac{v^2}{2g}")
        st.latex(r"P = \rho \cdot g \cdot Q \cdot H")


# ==============================
# VISOR DE DOCUMENTOS
# ==============================
@st.dialog("📖 Visor de Documentos", width="large")
def visor_documento(file_path, file_type):
    # Updated CSS for Dark Theme Compatibility
    st.markdown("""
        <style>
        .doc-paper {
            background-color: #1e293b; /* Slate 800 */
            color: #e2e8f0; /* Slate 200 */
            padding: 2rem 3rem;
            border-radius: 4px;
            border: 1px solid #334155;
            line-height: 1.6;
        }
        .doc-paper h1, .doc-paper h2, .doc-paper h3 {
            color: #38bdf8; /* Sky 400 */
            border-bottom: 1px solid #334155;
        }
        .doc-paper table {
            border-color: #334155;
        }
        .doc-paper th, .doc-paper td {
            border: 1px solid #475569;
        }
        </style>
    """, unsafe_allow_html=True)

    st.caption(f"**Archivo:** `{Path(file_path).name}`")
    with st.container(height=650):
        if file_type == "docx":
            try:
                import mammoth
                with st.spinner("Procesando documento..."):
                    with open(file_path, "rb") as docx_file:
                        result = mammoth.convert_to_html(docx_file)
                        st.markdown(f"<div class='doc-paper'>{result.value}</div>", unsafe_allow_html=True)
            except ImportError:
                st.error("Error: La librería 'mammoth' no está instalada. Ejecute `pip install mammoth`.")
            except Exception as e:
                st.error(f"Error inesperado al abrir el documento: {e}")
        elif file_type == "md":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    st.markdown(f.read())
            except Exception as e:
                st.error(f"Error: {e}")

if "preview_file" in st.session_state and st.session_state.preview_file:
    visor_documento(st.session_state.preview_file, st.session_state.preview_type)
    st.session_state.preview_file = None


# ==============================
# TAB 6: DOCUMENTACIÓN
# ==============================
with tab_docs:
    st.markdown("### Documentación del Proyecto")
    
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        st.info("Vista previa del archivo README del proyecto.")
        md_path = Path("media/docs/PROYECTO.MD")
        if md_path.exists():
            with open(md_path, "r", encoding="utf-8") as f:
                with st.container(height=500, border=True):
                    st.markdown(f.read())

            if st.button("🔍 Abrir en Visor Completo", key="preview_md_btn"):
                st.session_state.preview_file = str(md_path)
                st.session_state.preview_type = "md"
                st.rerun()

    with col_d2:
        st.success("Descargas Disponibles")
        informe_path = Path("source/INFORME_PROYECTO.docx")
        if informe_path.exists():
            with open(informe_path, "rb") as f:
                st.download_button(
                    "📄 Descargar Informe Técnico", f,
                    file_name="Informe_Proyecto.docx",
                    use_container_width=True
                )

            if st.button("👁️ Vista Previa Informe", key="preview_docx_btn", use_container_width=True):
                st.session_state.preview_file = str(informe_path)
                st.session_state.preview_type = "docx"
                st.rerun()


# ====================================
# FOOTER
# ====================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; padding: 2rem 0; color: #64748b; font-size: 0.85rem;'>
        <p style='margin-bottom: 0.5rem;'>
            <strong>PROYECTO DE PROCESOS UNITARIOS</strong> • 5to SEMESTRE
        </p>
        <p style='font-size: 0.8rem;'>
            Desarrollado con <span style='color:#38bdf8'>Streamlit</span> + <span style='color:#38bdf8'>Plotly</span> + <span style='color:#38bdf8'>Three.js</span>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
