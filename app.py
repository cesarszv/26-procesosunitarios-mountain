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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stMetric > div {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stMetric > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    h1 { 
        color: #1e293b; 
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    h2 { 
        color: #334155; 
        font-weight: 600;
        border-bottom: 2px solid #e2e8f0; 
        padding-bottom: 8px; 
        margin-top: 1.5rem;
    }
    
    h3 { 
        color: #475569; 
        font-weight: 500;
    }
    
    /* Estilizar las pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8fafc;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        border: 1px solid #e2e8f0;
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-top: 3px solid #3b82f6;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ====================================
# SIDEBAR — PARÁMETROS INTERACTIVOS
# ====================================
st.sidebar.title("⚙️ Parámetros del Sistema")
st.sidebar.markdown("Ajusta las variables para recalcular el sistema en tiempo real.")
st.sidebar.markdown("---")

with st.sidebar.expander("📐 Tubería", expanded=True):
    Q = st.slider(
        "Caudal Q (m³/s)",
        min_value=0.005, max_value=0.100, value=0.025, step=0.001,
        format="%.3f",
        help="Caudal volumétrico del flujo de agua"
    )
    Q_ls = Q * 1000  # L/s para mostrar
    st.caption(f"**Equivalente:** {Q_ls:.1f} L/s")

    D = st.slider(
        "Diámetro D (m)",
        min_value=0.05, max_value=0.30, value=0.1541, step=0.001,
        format="%.4f",
        help="Diámetro interno de la tubería"
    )
    st.caption(f"**Equivalente:** {D*100:.1f} cm = {D*1000:.1f} mm")

    epsilon = st.slider(
        "Rugosidad ε (m)",
        min_value=0.00001, max_value=0.001, value=0.000046, step=0.000001,
        format="%.6f",
        help="Rugosidad absoluta (acero comercial ≈ 0.046 mm)"
    )

with st.sidebar.expander("💧 Fluido", expanded=False):
    rho = st.slider(
        "Densidad ρ (kg/m³)",
        min_value=900.0, max_value=1100.0, value=998.0, step=1.0,
        help="Densidad del agua a ~20°C = 998 kg/m³"
    )
    
    mu = st.slider(
        "Viscosidad μ (Pa·s)",
        min_value=0.0005, max_value=0.0020, value=0.0010, step=0.0001,
        format="%.4f",
        help="Viscosidad dinámica del agua a ~20°C = 0.001 Pa·s"
    )

with st.sidebar.expander("🔬 Modelo 3D", expanded=False):
    tramo_3d = st.selectbox(
        "Tramo a visualizar",
        options=list(range(1, 9)),
        index=0,
        format_func=lambda x: f"Tramo {x}",
        help="Selecciona el tramo para el modelo 3D interactivo"
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
st.title("� Sistema Hidráulico — Dashboard de Análisis")
st.markdown(
    "**Proyecto de Procesos Unitarios** | Simulación de transporte de agua desde un río, "
    "cruzando una montaña, hasta una planta industrial a **3.4 km** de distancia."
)

# ====================================
# KPIs PRINCIPALES
# ====================================
st.markdown("### 📊 Indicadores Clave de Rendimiento (KPIs)")
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Mapa Piezométrico",
    "🏔️ Perfil del Terreno",
    "📈 Análisis de Pérdidas",
    "🧊 Modelo 3D",
    "📋 Datos Detallados",
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
        "💡 **Interpretación:** La presión manométrica (panel inferior) debe mantenerse positiva "
        "para evitar cavitación. Las bombas elevan la energía (saltos verdes) y la fricción + "
        "accesorios la disipan gradualmente."
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
        st.info(f"📝 **Nota:** {defn['notas']}")


# ==============================
# TAB 4: MODELO 3D
# ==============================
with tab4:
    st.header(f"Modelo 3D Interactivo — Tramo {tramo_3d}")
    
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
        st.info(f"📝 {defn_3d['notas']}")


# ==============================
# TAB 5: DATOS DETALLADOS
# ==============================
with tab5:
    st.header("Datos Crudos del CSV")
    st.markdown("Datos extraídos directamente del archivo `CALCULOS_HIDRAULICOS.csv`.")
    
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


# ====================================
# FOOTER
# ====================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#7f8c8d; font-size:12px;'>"
    "Proyecto de Procesos Unitarios — 5to Semestre | "
    "Desarrollado con Python, Pandas, Plotly, Three.js y Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
