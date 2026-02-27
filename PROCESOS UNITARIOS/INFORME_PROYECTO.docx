INFORME DE INGENIERÍA HIDRÁULICA

Proyecto: Captación y Transporte de Agua para la Industria α

---

# 1. Introducción

Este informe presenta el diseño y evaluación de un sistema hidráulico para el transporte de agua desde un río hasta una planta industrial, siguiendo los lineamientos y pasos metodológicos definidos en el documento base (PROYECTO.MD). El análisis integra la lógica y resultados obtenidos mediante el desarrollo de un software especializado en Python, el cual permite simular y optimizar el sistema bajo criterios energéticos, hidráulicos y técnicos.

# 2. Problema Central

Una planta industrial requiere un suministro continuo de agua desde un río cercano para cubrir demandas domésticas, térmicas e industriales. El sistema debe recorrer aproximadamente 3 km, atravesando zonas montañosas, carreteras y áreas urbanas, enfrentando desafíos de pérdidas de carga, requerimientos energéticos, seguridad hidráulica y selección de bombeo.

# 3. Objetivo General

Diseñar y evaluar un sistema hidráulico de transporte de agua desde un río hasta una planta industrial que sea energéticamente eficiente, hidráulicamente seguro y técnicamente viable, considerando variaciones topográficas, restricciones urbanas y ambientales, y la distribución del caudal para los distintos usos.

# 4. Objetivos Específicos
1. Analizar el perfil topográfico del trayecto, identificando cotas críticas y tramos con restricciones especiales.
2. Determinar los caudales requeridos para los distintos usos del agua y establecer escenarios de operación representativos.
3. Proponer y justificar el trazado del sistema de conducción, incluyendo la selección del material y diámetro de las tuberías.
4. Calcular las pérdidas de carga mayores y menores utilizando modelos hidráulicos adecuados.
5. Evaluar la necesidad, ubicación y características de las estaciones de bombeo requeridas.

# 5. Metodología

## Paso 1: Interpretación del Problema
Se identifican la fuente (río), el destino (planta industrial) y las restricciones topográficas y urbanas. El contexto se modela en el software mediante la definición de tramos y cotas críticas (ver core/tramos.py).

## Paso 2: Elaboración del Croquis del Sistema
Se realiza un croquis en planta y perfil longitudinal, ubicando el río, montaña, carretera, zona urbana y planta. El software permite visualizar el perfil topográfico y la distribución de tramos, facilitando la identificación de zonas críticas.

## Paso 3: Definición de Datos y Supuestos
- Propiedades del agua: Temperatura 20 °C, Densidad 998 kg/m³, Viscosidad dinámica 1,0×10⁻³ Pa·s, Gravedad 9,81 m/s².
- Caudales de diseño: Uso doméstico 4 l/s, térmico 12 l/s, industrial 9 l/s, total 0,025 m³/s.
- Supuestos: Régimen permanente, presión máxima admisible 1,6 MPa, presión mínima absoluta > 20 kPa, velocidad recomendada 0,6–3,0 m/s, presión máxima urbana 1,2 MPa.

## Paso 4: Selección Preliminar de Tubería
Material de tubería: acero comercial (según indicación). Diámetro comercial usado en los cálculos: 0,1541 m.

## Paso 5: Cálculo del Régimen de Flujo
Se determina el número de Reynolds y se seleccionan las correlaciones de fricción (Haaland, Colebrook-White, Swamee-Jain) tal como implementa `core/hidraulica.py`.

## Paso 6: Cálculo de Pérdidas de Carga
Pérdidas mayores mediante Darcy–Weisbach y pérdidas menores sumando coeficientes K de accesorios. La lógica y fórmulas implementadas están en `core/hidraulica.py` y la lista de accesorios por tramo en `core/tramos.py`.

## Paso 7: Análisis Energético del Sistema
Aplicación de la ecuación general de la energía para cada tramo, considerando elevación, pérdidas y aportes/gravedad entre tramos (lógica implementada en `calcular_sistema_completo()` de `core/hidraulica.py`).

## Paso 8: Selección y Ubicación del Bombeo
Determinación de estaciones de bombeo conforme a las cargas por tramo y la estrategia de tanques rompe-presión en descensos (implementada en `core/tramos.py`).

# 6. Datos y tablas extraídas del archivo CALCULOS_HIDRAULICOS.csv (resumen)

**Resumen de tramos (extraído del bloque TRAMOS)**
- Longitud total (tramos 1–7): 1.669,94 m

Tabla: Resumen de tramos (resumen tabular)

| Tramo | Distancia (m) | Altura (m) | Pendiente (°) | Longitud tubería (m) |
|---:|---:|---:|---:|---:|
| 1 | 182,53 | +100 | 28,72 | 211,13 |
| 2 | 112,39 | +200 | 60,67 | 235,42 |
| 3 | 163,87 | +200 | 50,67 | 264,56 |
| 4 | 251,55 | 0 | 0,00 | 254,55 |
| 5 | 129,05 | -200 | -57,17 | 235,02 |
| 6 | 71,33 | -200 | -70,37 | 209,34 |
| 7 | 243,18 | -100 | -22,35 | 259,94 |

**Tramo 8 (subterráneo / carretera)**
- Longitud tramo 8 (tubería subterránea): 1.648,51 m
- Ver detalle de subsegmentos en `core/tramos.py` → `sub_segmentos`.

**Parámetros hidráulicos (valores tomados del CSV, aplicables globalmente en los cálculos)**

| Parámetro | Valor |
|---|---:|
| Caudal de diseño Q | 0,025 m³/s |
| Diámetro de cálculo D | 0,1541 m (acero comercial) |
| Área A | 0,01865 m² |
| Velocidad v | 1,34 m/s |
| Número de Reynolds Re | 2,06·10^5 |
| Factor fricción (Colebrook) | 0,017649 |
| Factor fricción (Haaland) | 0,017438 |
| Pérdidas Darcy (referencia por tramo) | ≈ 2,19–2,21 m |

**Potencias y observaciones tomadas del CSV**

| Descripción | Valor |
|---|---:|
| Potencia sistema (registro global) | 25,05 kW (33,59 HP) |
| Potencia Tramo 8 (bloque específico) | 36,04 kW (48,34 HP) |
| Observación Tramo 2 | 2 estaciones de bombeo; accesorios y potencias se duplican para cálculo total |

**Accesorios y coeficientes K (resumen)**

| Accesorio | Cantidad típica (ej.) | K | Carga (m) |
|---|---:|---:|---:|
| Entrada al río proyectada | 1 | 0,50 | 0,0458 |
| 2 codos 45° | 2 | 0,12 | 0,0220 |
| 2 codos 60° | 2 | 0,375 | 0,0687 |
| Salida a tanque receptor | 1 | 1,00 | 0,0916 |
| Suma K por estación (ej.) | — | — | 1,33–1,43 m |

# 7. Resultados (párrafo)

Los cálculos extraídos del archivo CSV y las rutinas del software muestran que, con el caudal de diseño Q = 0,025 m³/s y un diámetro comercial de 0,1541 m (acero comercial), la velocidad de flujo resultante es aproximadamente 1,34 m/s, dentro del rango recomendado (0,6–3,0 m/s). El régimen de flujo es turbulento (Re ≈ 2,06×10^5) y las fricciones calculadas por Colebrook y Haaland son próximas (f ≈ 0,0176). Las pérdidas distribuidas por tramo (Darcy) se estiman en torno a 2,19–2,21 m según los bloques de cálculo; las pérdidas menores por accesorios agregan típicamente 1,3–1,4 m por estación cuando se consideran entradas, codos y salidas a tanques. La potencia total reportada en el CSV para el sistema (registro global) es 25,05 kW; se observa además que el tramo subterráneo (Tramo 8) registra una potencia estimada de 36,04 kW en su bloque específico, y que Tramo 2 se modela con dos estaciones de bombeo según la estrategia de diseño.

# 8. Conclusiones (párrafo)

Con la configuración y parámetros extraídos del CSV y la lógica implementada en el código, el sistema es hidráulicamente viable: la elección de diámetro y material (acero comercial) mantiene velocidades adecuadas y un factor de fricción bajo que permite pérdidas razonables. La recuperación de energía en tramos descendentes (cuando no se usan tanques rompe-presión) reduce la carga de bombeo para tramos posteriores, lo que es aprovechado en el modelo. Se recomienda validar las líneas piezométricas y las presiones máximas/locales con las gráficas provistas externamente (paso 9 excluido del informe) antes de la selección final de bombas y elementos de control. También se sugiere revisar la duplicación de datos para estaciones múltiples (por ejemplo Tramo 2) y realizar un chequeo final de tensiones y anclajes mecánicos sobre tubería de acero.

# 9. Anexos y código

- El informe conserva la referencia y explicaciones sobre la implementación del cálculo en el repositorio Python: `core/hidraulica.py` (motor de fricción, pérdidas y energía), `core/tramos.py` (definición de tramos, accesorios y decisiones de bombeo/tanques) y `app.py` (interfaz Streamlit y parámetros interactivos).
- Fragmentos relevantes y tablas originales están disponibles en `CALCULOS_HIDRAULICOS.csv` para auditoría y comparación con las rutinas.
- Fragmentos relevantes y tablas originales están disponibles en `CALCULOS_HIDRAULICOS.csv` para auditoría y comparación con las rutinas.

**Fragmentos adicionales incluidos (selección mínima):**

- `core/hidraulica.py` — `calcular_tramo` (función clave, ver Anexo A) calcula: área, velocidad, Re, factores de fricción (Colebrook/Haaland/Swamee-Jain), pérdidas por fricción y menores, carga por estación y potencia de bomba.

- `core/hidraulica.py` — `calcular_sistema_completo` recalcula todo el sistema usando definiciones en `core/tramos.py` e incluye la lógica de transferencia de cabeza gravitacional entre tramos cuando aplica.

- `core/datos.py` — `extraer_datos_completos()` lee `CALCULOS_HIDRAULICOS.csv` y devuelve: `perfil_terreno`, `parametros`, `resumen_tramos`, `tramo_8_distancias` y `tramos_detalle`. Esta función es la fuente de los valores tabulados en el informe.

- `visualizaciones/mapa_piezometrico.py` — `crear_mapa_piezometrico(resultados, Q, D)` genera la figura Plotly con EGL, HGL, marcadores de bombas y tanques, y la curva de presión manométrica.

---

Este documento incorpora el resumen tabular y los valores clave tomados directamente del CSV, mantiene la información sobre el código y añade párrafos de resultados y conclusiones solicitados.