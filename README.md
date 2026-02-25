# 🔧 Cálculos Hidráulicos — Procesos Unitarios

Aplicación interactiva para el análisis y visualización del sistema hidráulico
de transporte de agua desde un río, cruzando una montaña, hasta una planta industrial.

## 📋 Descripción del Sistema

- **Distancia total:** ~3,434 m (8 tramos)
- **Elevación máxima:** 500 m sobre el nivel del río
- **Tubería:** DN150 (Ø 154.1 mm), acero comercial
- **Caudal de diseño:** 25 L/s
- **Tramos 1–3:** Subida (bombas hidráulicas)
- **Tramo 4:** Plano (bomba pequeña)
- **Tramos 5–7:** Bajada (válvulas de estrangulamiento)
- **Tramo 8:** Subterráneo hacia la empresa (bomba)

## 🚀 Instalación

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app.py
```

## 📦 Dependencias

- `streamlit` — Framework web interactivo
- `pandas` — Análisis de datos
- `numpy` — Cálculos numéricos
- `plotly` — Gráficos interactivos
- `scipy` — Resolución de ecuaciones (Colebrook-White)

## 🖥️ Funcionalidades

### Parámetros Interactivos (Sidebar)
Modifica en tiempo real:
- Caudal (Q)
- Diámetro de tubería (D)
- Rugosidad (ε)
- Densidad del fluido (ρ)
- Viscosidad (μ)

### Pestañas de Visualización

| Pestaña | Contenido |
|---------|-----------|
| 📊 Mapa Piezométrico | EGL, HGL, presión a lo largo del sistema |
| 🏔️ Perfil del Terreno | Elevación topográfica con tramos coloreados |
| 📈 Análisis de Pérdidas | Barras apiladas de pérdidas + potencia por tramo |
| 🧊 Modelo 3D | Tramo interactivo con Three.js (flujo animado) |
| 📋 Datos Detallados | DataFrames, accesorios, fórmulas empleadas |

### Modelo 3D (Three.js)
- Tubería con gradiente de presión (azul → rojo)
- Partículas de flujo animadas
- Accesorios visibles (codos, bombas, válvulas)
- Controles: rotar, zoom, desplazar

## 📁 Estructura del Proyecto

```
PROCESOS_UNITARIOS/
├── app.py                          # Aplicación Streamlit
├── requirements.txt                # Dependencias
├── CALCULOS_HIDRAULICOS.csv        # Datos originales
├── core/
│   ├── __init__.py
│   ├── datos.py                    # Parseo del CSV
│   ├── hidraulica.py               # Fórmulas hidráulicas
│   └── tramos.py                   # Definición de tramos
└── visualizaciones/
    ├── __init__.py
    ├── mapa_piezometrico.py        # Gráficos 2D (Plotly)
    └── modelo_3d.py                # Modelo 3D (Three.js)
```

## 📐 Fórmulas Implementadas

- Reynolds: `Re = ρvD/μ`
- Colebrook-White (iterativa con scipy)
- Haaland (explícita)
- Swamee-Jain (explícita)
- Darcy-Weisbach: `hf = f·(L/D)·v²/(2g)`
- Pérdidas menores: `hm = ΣK·v²/(2g)`
- Potencia: `P = ρgQH`

## 👨‍🎓 Proyecto Académico

Materia: **Procesos Unitarios** — 5to Semestre  
