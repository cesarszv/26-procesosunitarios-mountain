"""
mapa_piezometrico.py — Mapa piezométrico de presiones del sistema.

Visualiza la línea de energía (EGL), la línea de gradiente hidráulico (HGL),
y las pérdidas/ganancias de presión en cada bomba y válvula del sistema.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def crear_mapa_piezometrico(resultados: dict, Q: float, D: float) -> go.Figure:
    """
    Genera el mapa piezométrico completo del sistema.
    """
    from core.tramos import obtener_definicion_tramos
    
    definiciones = obtener_definicion_tramos()
    
    dist_puntos = [0.0]       # Distancia acumulada
    elev_puntos = [0.0]       # Elevación del terreno
    egl_puntos = [0.0]        # Línea de energía
    hgl_puntos = [0.0]        # Línea gradiente hidráulico
    presion_puntos = [0.0]    # Presión manométrica (m.c.a.)
    etiquetas = ['Río\n(Captación)']
    
    dist_acum = 0.0
    elev_acum = 0.0
    energia_actual = 0.0
    
    bombas_x = []
    bombas_y_antes = []
    bombas_y_despues = []
    bombas_label = []
    
    valvulas_x = []
    valvulas_y = []
    valvulas_label = []
    
    hv = resultados[1]['carga_cinetica']
    
    for num_tramo in range(1, 9):
        if num_tramo > 7:
            dist_tramo = definiciones[8]['distancia']
        else:
            dist_tramo = definiciones[num_tramo]['distancia']
        
        r = resultados[num_tramo]
        n_est = r['num_estaciones']
        L_est = r['longitud_estacion']
        hf_est = r['perdidas_friccion_colebrook']
        hm_est = r['perdidas_menores']
        z_total = definiciones[num_tramo]['altura']
        z_est = z_total / n_est if n_est > 0 else z_total
        
        for est in range(n_est):
            x_inicio = dist_acum
            
            if not r['es_bajada']:
                H_bomba = r['carga_estacion']
                bombas_x.append(x_inicio)
                bombas_y_antes.append(energia_actual)
                energia_actual += H_bomba
                bombas_y_despues.append(energia_actual)
                bombas_label.append(
                    f'Bomba T{num_tramo}'
                    + (f'-E{est+1}' if n_est > 1 else '')
                    + f'\nΔH = {H_bomba:.1f} m'
                    + f'\nP = {r["potencia_kw"]:.1f} kW'
                )
            
            dist_sub = dist_tramo / n_est
            n_puntos_sub = 5
            
            for j in range(1, n_puntos_sub + 1):
                frac = j / n_puntos_sub
                dx = dist_sub * frac
                dz = z_est * frac
                
                hf_parcial = hf_est * frac
                hm_parcial = hm_est if j == 1 else 0
                
                x_actual = x_inicio + dx
                elev_actual = elev_acum + dz
                energia_actual -= (hf_est / n_puntos_sub + (hm_est if j == 1 else 0))
                
                dist_puntos.append(x_actual)
                elev_puntos.append(elev_actual)
                egl_puntos.append(energia_actual)
                hgl_puntos.append(energia_actual - hv)
                presion_puntos.append(energia_actual - hv - elev_actual)
                
                if j == n_puntos_sub:
                    etiquetas.append(
                        f'T{num_tramo}' + (f'-E{est+1}' if n_est > 1 else '') + ' fin'
                    )
                else:
                    etiquetas.append('')
            
            elev_acum += z_est
            dist_acum += dist_sub
            
            if r['es_bajada']:
                tiene_tanque = definiciones[num_tramo].get('tanque_rompe_presion', True)
                
                if tiene_tanque:
                    egl_meta = elev_acum + hv
                    perdida = energia_actual - egl_meta
                    
                    valvulas_x.append(dist_acum)
                    valvulas_y.append(energia_actual)
                    valvulas_label.append(
                        f'Tanque rompe-presión T{num_tramo}'
                        + (f'-E{est+1}' if n_est > 1 else '')
                        + f'\nDisipa: {perdida:.1f} m'
                    )
                    
                    energia_actual -= perdida
                    
                    if abs(perdida) > 0.01:
                        dist_puntos.append(dist_acum)
                        elev_puntos.append(elev_acum)
                        egl_puntos.append(energia_actual)
                        hgl_puntos.append(energia_actual - hv)
                        presion_puntos.append(energia_actual - hv - elev_acum)
                        etiquetas.append(f'Tanque T{num_tramo}' + (f'-E{est+1}' if n_est > 1 else ''))
                else:
                    presion_local = energia_actual - hv - elev_acum
                    valvulas_x.append(dist_acum)
                    valvulas_y.append(energia_actual)
                    valvulas_label.append(
                        f'T{num_tramo} → Gravedad a T{num_tramo+1}'
                        + f'\nCabeza disponible: {presion_local:.1f} m'
                    )
    
    # ====== Crear figura ======
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            '<b>Mapa Piezométrico</b> — Líneas de Energía y Gradiente Hidráulico',
            '<b>Presión Manométrica</b> a lo largo del Sistema'
        ),
        vertical_spacing=0.15,
        row_heights=[0.65, 0.35],
    )
    
    # --- Panel superior: EGL, HGL, Terreno ---
    
    # Terreno (relleno)
    fig.add_trace(go.Scatter(
        x=dist_puntos, y=elev_puntos,
        fill='tozeroy',
        fillcolor='rgba(100, 116, 139, 0.4)', # Slate 500 con opacidad
        line=dict(color='#94a3b8', width=1),
        name='Terreno (elevación)',
        hovertemplate='<b>Distancia:</b> %{x:.0f} m<br><b>Elevación:</b> %{y:.0f} m<extra></extra>',
    ), row=1, col=1)
    
    # EGL
    fig.add_trace(go.Scatter(
        x=dist_puntos, y=egl_puntos,
        line=dict(color='#00d4ff', width=3), # Cian eléctrico
        name='EGL (Línea de Energía)',
        hovertemplate='<b>Distancia:</b> %{x:.0f} m<br><b>EGL:</b> %{y:.1f} m<extra></extra>',
    ), row=1, col=1)
    
    # HGL
    fig.add_trace(go.Scatter(
        x=dist_puntos, y=hgl_puntos,
        line=dict(color='#f4c430', width=3, dash='dash'), # Amarillo dorado
        name='HGL (Gradiente Hidráulico)',
        hovertemplate='<b>Distancia:</b> %{x:.0f} m<br><b>HGL:</b> %{y:.1f} m<extra></extra>',
    ), row=1, col=1)
    
    # Marcadores de bombas
    for i, (bx, by_a, by_d, blbl) in enumerate(zip(
        bombas_x, bombas_y_antes, bombas_y_despues, bombas_label
    )):
        fig.add_trace(go.Scatter(
            x=[bx, bx], y=[by_a, by_d],
            mode='lines+markers',
            line=dict(color='#10B981', width=4), # Green
            marker=dict(size=10, symbol='triangle-up', color='#10B981'),
            name=f'Bomba T{i+1}' if i == 0 else None,
            showlegend=(i == 0),
            hovertext=blbl,
            hoverinfo='text',
        ), row=1, col=1)
        
        fig.add_annotation(
            x=bx, y=(by_a + by_d) / 2,
            text=f'<b>⬆ {by_d - by_a:.0f} m</b>',
            showarrow=True,
            arrowhead=2,
            arrowcolor='#10B981',
            font=dict(size=11, color='#059669', family="Inter, sans-serif"),
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="#10B981",
            borderwidth=1,
            borderpad=3,
            ax=45, ay=0,
            row=1, col=1,
        )
    
    # Marcadores de válvulas
    for i, (vx, vy, vlbl) in enumerate(zip(valvulas_x, valvulas_y, valvulas_label)):
        fig.add_trace(go.Scatter(
            x=[vx], y=[vy],
            mode='markers',
            marker=dict(size=14, symbol='x', color='#ef4444', line=dict(width=2)), # Red
            name='Válv. Estrang.' if i == 0 else None,
            showlegend=(i == 0),
            hovertext=vlbl,
            hoverinfo='text',
        ), row=1, col=1)
    
    # --- Panel inferior: Presión manométrica ---
    
    colores_presion = ['#10B981' if p >= 0 else '#EF4444' for p in presion_puntos]
    
    fig.add_trace(go.Scatter(
        x=dist_puntos, y=presion_puntos,
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)', # Green tint
        line=dict(color='#22d3ee', width=2), # Cyan
        name='Presión manométrica',
        hovertemplate='<b>Distancia:</b> %{x:.0f} m<br><b>Presión:</b> %{y:.1f} m.c.a.<extra></extra>',
    ), row=2, col=1)
    
    # Línea de presión cero
    fig.add_hline(
        y=0, line=dict(color='#EF4444', width=1, dash='dot'),
        annotation_text='Presión atmosférica',
        annotation_position='top right',
        annotation_font=dict(color='#ef4444'),
        row=2, col=1,
    )

    # Anotaciones de presión negativa (Fix: Check for empty list)
    if presion_puntos:
        min_presion = min(presion_puntos)
        if min_presion < 0:
            idx_min = presion_puntos.index(min_presion)
            fig.add_annotation(
                x=dist_puntos[idx_min], y=min_presion,
                text=f'<b>⚠️ Cavitación ({min_presion:.1f} m)</b>',
                showarrow=True,
                arrowhead=2,
                arrowcolor='#EF4444',
                font=dict(size=12, color='#EF4444', family="Inter, sans-serif"),
                bgcolor="rgba(0,0,0,0.8)",
                row=2, col=1,
            )
    
    # ====== Formato ======
    fig.update_layout(
        height=900,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, system-ui, sans-serif', size=14, color='#f1f5f9'),
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=14,
            font_family="Inter, system-ui, sans-serif",
            font_color="#f8fafc"
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(15, 23, 42, 0.8)',
            bordercolor='#334155',
            borderwidth=1
        ),
        title=dict(
            text=(
                f'<b>Sistema Hidráulico — Mapa Piezométrico</b><br>'
                f'<span style="font-size:14px; color:#94a3b8">Q = {Q*1000:.1f} L/s | '
                f'D = {D*100:.1f} cm | v = {resultados[1]["velocidad"]:.2f} m/s | '
                f'Re = {resultados[1]["reynolds"]:,.0f}</span>'
            ),
            x=0.05,
        ),
        margin=dict(t=130, l=60, r=40, b=60)
    )
    
    fig.update_xaxes(
        title_text='<b>Distancia acumulada (m)</b>', 
        row=2, col=1,
        gridcolor='#334155',
        zerolinecolor='#475569'
    )
    fig.update_xaxes(gridcolor='#334155', zerolinecolor='#475569', row=1, col=1)
    
    fig.update_yaxes(
        title_text='<b>Altura / Energía (m)</b>', 
        row=1, col=1,
        gridcolor='#334155',
        zerolinecolor='#475569'
    )
    fig.update_yaxes(
        title_text='<b>Presión (m.c.a.)</b>', 
        row=2, col=1,
        gridcolor='#334155',
        zerolinecolor='#475569'
    )
    
    return fig


def crear_desglose_perdidas(resultados: dict) -> go.Figure:
    """
    Gráfico de barras apiladas: desglose de pérdidas por tramo.
    """
    tramos_nums = list(range(1, 9))
    nombres = [f'Tramo {i}' for i in tramos_nums]
    
    z_vals = []
    hf_vals = []
    hm_vals = []
    
    for i in tramos_nums:
        r = resultados[i]
        z_abs = abs(r.get('z_estacion', 0)) * r['num_estaciones']
        hf = r['perdidas_friccion_colebrook'] * r['num_estaciones']
        hm = r['perdidas_menores'] * r['num_estaciones']
        
        z_vals.append(z_abs if not r['es_bajada'] else 0)
        hf_vals.append(hf)
        hm_vals.append(hm)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Elevación (z)',
        x=nombres, y=z_vals,
        marker_color='#3B82F6', # Blue
        marker_line_width=0,
        hovertemplate='<b>%{x}</b><br>Elevación: %{y:.2f} m<extra></extra>',
    ))
    
    fig.add_trace(go.Bar(
        name='Pérdidas fricción',
        x=nombres, y=hf_vals,
        marker_color='#f4c430', # Gold
        marker_line_width=0,
        hovertemplate='<b>%{x}</b><br>Fricción: %{y:.2f} m<extra></extra>',
    ))
    
    fig.add_trace(go.Bar(
        name='Pérdidas menores',
        x=nombres, y=hm_vals,
        marker_color='#EF4444', # Red
        marker_line_width=0,
        hovertemplate='<b>%{x}</b><br>Accesorios: %{y:.2f} m<extra></extra>',
    ))
    
    fig.update_layout(
        barmode='stack',
        title='<b>Desglose de Pérdidas por Tramo</b>',
        xaxis_title='<b>Tramo</b>',
        yaxis_title='<b>Carga (m)</b>',
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        font=dict(family='Inter, system-ui, sans-serif', size=14, color='#f1f5f9'),
        hoverlabel=dict(bgcolor="#1e293b", font_size=14),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        xaxis=dict(gridcolor='#334155'),
        yaxis=dict(gridcolor='#334155')
    )
    
    return fig


def crear_grafico_potencia(resultados: dict) -> go.Figure:
    """Gráfico de barras: potencia requerida por tramo (kW y HP)."""
    tramos_nums = list(range(1, 9))
    nombres = [f'T{i}' for i in tramos_nums]
    
    kw_vals = [resultados[i]['potencia_kw'] for i in tramos_nums]
    hp_vals = [resultados[i]['potencia_hp'] for i in tramos_nums]
    tipos = [resultados[i]['tipo'] for i in tramos_nums]
    colores = ['#10B981' if t == 'bomba' else '#F59E0B' for t in tipos] # Green vs Amber
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=('<b>Potencia (kW)</b>', '<b>Potencia (HP)</b>'))
    
    fig.add_trace(go.Bar(
        x=nombres, y=kw_vals,
        marker_color=colores,
        name='kW',
        hovertemplate='<b>%{x}</b><br>%{y:.2f} kW<extra></extra>',
        text=[f'{v:.1f}' if v > 0 else '' for v in kw_vals],
        textposition='outside',
        textfont=dict(family="Inter, sans-serif", color="#f8fafc")
    ), row=1, col=1)
    
    fig.add_trace(go.Bar(
        x=nombres, y=hp_vals,
        marker_color=colores,
        name='HP',
        hovertemplate='<b>%{x}</b><br>%{y:.2f} HP<extra></extra>',
        text=[f'{v:.1f}' if v > 0 else '' for v in hp_vals],
        textposition='outside',
        textfont=dict(family="Inter, sans-serif", color="#f8fafc")
    ), row=1, col=2)
    
    fig.update_layout(
        title='<b>Potencia Requerida por Tramo</b><br>'
              '<span style="font-size:12px; color:#94a3b8">Verde = Bomba | Naranja = Válvula</span>',
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        showlegend=False,
        font=dict(family='Inter, system-ui, sans-serif', size=14, color='#f1f5f9'),
        hoverlabel=dict(bgcolor="#1e293b", font_size=14),
    )
    
    fig.update_xaxes(gridcolor='#334155')
    fig.update_yaxes(gridcolor='#334155')
    
    return fig


def crear_perfil_terreno_con_tramos(resultados: dict) -> go.Figure:
    """
    Perfil de elevación del terreno con tramos coloreados.
    """
    from core.tramos import obtener_definicion_tramos, obtener_elevaciones_acumuladas
    
    puntos = obtener_elevaciones_acumuladas()
    
    x = [p['distancia_acum'] for p in puntos]
    y = [p['elevacion'] for p in puntos]
    
    fig = go.Figure()
    
    # Relleno del terreno
    fig.add_trace(go.Scatter(
        x=x, y=y,
        fill='tozeroy',
        fillcolor='rgba(148, 163, 184, 0.2)', # Slate 400 faint
        line=dict(color='#64748b', width=1),
        name='Terreno',
        showlegend=False,
    ))
    
    # Segmentos por tramo con colores
    definiciones = obtener_definicion_tramos()
    colores_tramo = {
        1: '#ef4444',  # Red - Pump
        2: '#dc2626',  # Dark Red - Pump
        3: '#ef4444',  # Red - Pump
        4: '#f59e0b',  # Amber - Flat
        5: '#3b82f6',  # Blue - Gravity
        6: '#2563eb',  # Dark Blue - Gravity
        7: '#3b82f6',  # Blue - Gravity
        8: '#a855f7',  # Purple - Underground
    }
    
    dist_acum = 0.0
    elev_acum = 0.0
    
    for i in range(1, 8):
        d = definiciones[i]
        x0 = dist_acum
        y0 = elev_acum
        x1 = dist_acum + d['distancia']
        y1 = elev_acum + d['altura']
        
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode='lines+markers',
            line=dict(color=colores_tramo[i], width=5),
            marker=dict(size=8, color=colores_tramo[i]),
            name=f'T{i}: {d["tipo"]}',
            hovertemplate=(
                f'<b>Tramo {i}</b><br>'
                f'Dist: %{{x:.0f}} m<br>'
                f'Elev: %{{y:.0f}} m<br>'
                f'Pendiente: {d["pendiente"]:.1f}°'
                '<extra></extra>'
            ),
        ))
        
        # Etiqueta en punto medio
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=(y0 + y1) / 2 + 30,
            text=f'<b>T{i}</b>',
            showarrow=False,
            font=dict(size=12, color=colores_tramo[i], family="Inter, sans-serif"),
        )
        
        dist_acum = x1
        elev_acum = y1
    
    # Tramo 8 (simplificado)
    x8_start = dist_acum
    y8_start = elev_acum
    
    fig.add_trace(go.Scatter(
        x=[x8_start, x8_start + 250, x8_start + 250, x8_start + 1775, x8_start + 1837.5],
        y=[y8_start, y8_start, y8_start - 10, y8_start - 10, y8_start + 100],
        mode='lines+markers',
        line=dict(color=colores_tramo[8], width=4, dash='dot'),
        marker=dict(size=8, color=colores_tramo[8]),
        name='T8: subterráneo',
        hovertemplate='Tramo 8 (subterráneo)<br>Dist: %{x:.0f} m<br>Elev: %{y:.0f} m<extra></extra>',
    ))
    
    fig.add_annotation(
        x=x8_start + 900, y=y8_start - 40,
        text='<b>T8 (subterráneo)</b>',
        showarrow=False,
        font=dict(size=12, color=colores_tramo[8], family="Inter, sans-serif"),
    )
    
    fig.update_layout(
        title='<b>Perfil Topográfico y Tramos del Sistema</b><br>'
              '<span style="font-size:12px; color:#94a3b8">Rojo = Subida (Bomba) | Amarillo = Plano | '
              'Azul = Bajada (Gravedad) | Morado = Subterráneo</span>',
        xaxis_title='Distancia acumulada (m)',
        yaxis_title='Elevación (m)',
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=550,
        font=dict(family='Inter, system-ui, sans-serif', size=14, color='#f1f5f9'),
        legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5),
        xaxis=dict(gridcolor='#334155'),
        yaxis=dict(gridcolor='#334155'),
        margin=dict(l=60, r=40)
    )
    
    return fig
