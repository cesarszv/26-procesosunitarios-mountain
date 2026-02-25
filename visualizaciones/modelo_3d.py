"""
modelo_3d.py — Modelo 3D interactivo de un tramo de tubería usando Three.js.

Genera HTML con Three.js embebido que se renderiza dentro de Streamlit
usando st.components.v1.html(). Muestra:
- Tubería cilíndrica con flujo animado
- Accesorios (codos, válvulas, entrada/salida)
- Gradiente de color según presión
- Indicadores de dirección del flujo
- Panel de información con datos del tramo
"""

import json
import math


def generar_html_modelo_3d(
    num_tramo: int,
    longitud: float,
    diametro: float,
    pendiente: float,
    altura: float,
    velocidad: float,
    presion_entrada: float,
    presion_salida: float,
    accesorios: list[dict],
    tipo: str,
    potencia_kw: float,
    reynolds: float,
    f_friccion: float,
    perdidas_friccion: float,
    perdidas_menores: float,
) -> str:
    """
    Genera el código HTML/JS completo con Three.js para el modelo 3D de un tramo.
    """
    
    # Convertir pendiente a radianes
    angulo_rad = math.radians(abs(pendiente)) if pendiente != 0 else 0
    signo = 1 if altura >= 0 else -1
    
    # Escalar para visualización (normalizar a un tamaño razonable)
    escala = 10.0 / longitud if longitud > 0 else 1.0
    L_vis = longitud * escala
    D_vis = max(diametro * escala * 15, 0.15)  # Exagerar diámetro para visibilidad
    H_vis = altura * escala
    
    # Serializar accesorios para JS
    accesorios_js = json.dumps(accesorios, ensure_ascii=False)
    
    # Color según tipo
    color_bomba = '#10B981' # Tailwind Emerald 500
    color_valvula = '#F59E0B' # Tailwind Amber 500
    color_principal = color_bomba if tipo == 'bomba' else color_valvula
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                background: #0f172a; /* Tailwind Slate 900 */
                overflow: hidden; 
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
            }}
            #container {{ width: 100%; height: 700px; position: relative; }}
            #info-panel {{
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(15, 23, 42, 0.75);
                color: #f8fafc;
                padding: 20px;
                border-radius: 16px;
                font-size: 14px;
                line-height: 1.6;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                max-width: 320px;
                z-index: 10;
            }}
            #info-panel h3 {{
                color: {color_principal};
                margin-bottom: 12px;
                font-size: 18px;
                font-weight: 600;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding-bottom: 8px;
            }}
            #info-panel .valor {{ color: #38bdf8; font-weight: 600; }} /* Tailwind Sky 400 */
            #info-panel .label {{ color: #94a3b8; }} /* Tailwind Slate 400 */
            #legend {{
                position: absolute;
                bottom: 20px;
                left: 20px;
                background: rgba(15, 23, 42, 0.75);
                color: #f8fafc;
                padding: 16px 20px;
                border-radius: 12px;
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                border: 1px solid rgba(255,255,255,0.1);
                font-size: 12px;
                border: 1px solid rgba(255,255,255,0.1);
                z-index: 10;
            }}
            #legend div {{ margin: 4px 0; display: flex; align-items: center; gap: 8px; }}
            .color-box {{ 
                width: 14px; height: 14px; border-radius: 3px; 
                display: inline-block; border: 1px solid rgba(255,255,255,0.2); 
            }}
            #controls {{
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(15, 23, 42, 0.75);
                color: #94a3b8;
                padding: 12px 16px;
                border-radius: 12px;
                font-size: 12px;
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                border: 1px solid rgba(255,255,255,0.1);
                z-index: 10;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="info-panel">
                <h3>🔧 Tramo {num_tramo}</h3>
                <div><span class="label">Tipo:</span> <span class="valor">{tipo.replace('_', ' ').title()}</span></div>
                <div><span class="label">Longitud:</span> <span class="valor">{longitud:.1f} m</span></div>
                <div><span class="label">Diámetro:</span> <span class="valor">{diametro*100:.1f} cm</span> ({diametro*1000:.1f} mm)</div>
                <div><span class="label">Pendiente:</span> <span class="valor">{pendiente:.1f}°</span></div>
                <div><span class="label">Δ Altura:</span> <span class="valor">{'+' if altura>=0 else ''}{altura:.0f} m</span></div>
                <div><span class="label">Velocidad:</span> <span class="valor">{velocidad:.2f} m/s</span></div>
                <div><span class="label">Reynolds:</span> <span class="valor">{reynolds:,.0f}</span></div>
                <div><span class="label">f (Colebrook):</span> <span class="valor">{f_friccion:.6f}</span></div>
                <div><span class="label">Pérd. fricción:</span> <span class="valor">{perdidas_friccion:.2f} m</span></div>
                <div><span class="label">Pérd. menores:</span> <span class="valor">{perdidas_menores:.2f} m</span></div>
                <div><span class="label">Potencia:</span> <span class="valor">{potencia_kw:.2f} kW</span> ({potencia_kw/0.7457:.1f} HP)</div>
            </div>
            <div id="legend">
                <div style="margin-bottom: 8px; font-weight: 600; color: #f8fafc;">Leyenda</div>
                <div><span class="color-box" style="background:#38bdf8"></span> Tubería (zona alta presión)</div>
                <div><span class="color-box" style="background:#ef4444"></span> Tubería (zona baja presión)</div>
                <div><span class="color-box" style="background:#10b981"></span> Bomba / Estación</div>
                <div><span class="color-box" style="background:#94a3b8"></span> Codos</div>
                <div><span class="color-box" style="background:#64748b"></span> Tanque</div>
                <div><span class="color-box" style="background:#38bdf8"></span> Partículas de flujo</div>
            </div>
            <div id="controls">
                🖱️ Rotar: Click + Arrastrar | Zoom: Scroll | Pan: Click derecho
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            // ===== Parámetros del tramo =====
            const TRAMO = {{
                num: {num_tramo},
                longitud: {L_vis},
                diametro: {D_vis},
                angulo: {angulo_rad},
                signo: {signo},
                altura: {H_vis},
                velocidad: {velocidad},
                tipo: "{tipo}",
                accesorios: {accesorios_js},
                presionEntrada: {presion_entrada},
                presionSalida: {presion_salida},
            }};

            // ===== Setup Three.js =====
            const container = document.getElementById('container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0f172a); // Tailwind Slate 900
            scene.fog = new THREE.FogExp2(0x0f172a, 0.02);

            const camera = new THREE.PerspectiveCamera(55, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(8, 5, 10);
            camera.lookAt(0, 0, 0);

            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);

            // ===== Luces =====
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
            dirLight.position.set(10, 15, 10);
            dirLight.castShadow = true;
            dirLight.shadow.mapSize.width = 2048;
            dirLight.shadow.mapSize.height = 2048;
            dirLight.shadow.bias = -0.0005;
            scene.add(dirLight);

            const pointLight = new THREE.PointLight(0x38bdf8, 0.8, 30); // Tailwind Sky 400
            pointLight.position.set(-5, 8, 5);
            scene.add(pointLight);

            // ===== Controles de órbita (implementación manual) =====
            let isDragging = false;
            let isPanning = false;
            let previousMousePosition = {{ x: 0, y: 0 }};
            let orbitAngle = {{ theta: 0.7, phi: 0.5 }};
            let orbitRadius = 14;
            let panOffset = {{ x: 0, y: 0, z: 0 }};

            function updateCamera() {{
                camera.position.x = orbitRadius * Math.sin(orbitAngle.theta) * Math.cos(orbitAngle.phi) + panOffset.x;
                camera.position.y = orbitRadius * Math.sin(orbitAngle.phi) + panOffset.y;
                camera.position.z = orbitRadius * Math.cos(orbitAngle.theta) * Math.cos(orbitAngle.phi) + panOffset.z;
                camera.lookAt(panOffset.x, panOffset.y, panOffset.z);
            }}

            container.addEventListener('mousedown', (e) => {{
                if (e.button === 0) isDragging = true;
                if (e.button === 2) isPanning = true;
                previousMousePosition = {{ x: e.clientX, y: e.clientY }};
            }});

            container.addEventListener('mousemove', (e) => {{
                const deltaMove = {{ x: e.clientX - previousMousePosition.x, y: e.clientY - previousMousePosition.y }};
                if (isDragging) {{
                    orbitAngle.theta -= deltaMove.x * 0.005;
                    orbitAngle.phi = Math.max(-Math.PI/2 + 0.1, Math.min(Math.PI/2 - 0.1, orbitAngle.phi + deltaMove.y * 0.005));
                    updateCamera();
                }}
                if (isPanning) {{
                    panOffset.x -= deltaMove.x * 0.02;
                    panOffset.y += deltaMove.y * 0.02;
                    updateCamera();
                }}
                previousMousePosition = {{ x: e.clientX, y: e.clientY }};
            }});

            container.addEventListener('mouseup', () => {{ isDragging = false; isPanning = false; }});
            container.addEventListener('mouseleave', () => {{ isDragging = false; isPanning = false; }});
            container.addEventListener('wheel', (e) => {{
                orbitRadius = Math.max(5, Math.min(30, orbitRadius + e.deltaY * 0.01));
                updateCamera();
            }});
            container.addEventListener('contextmenu', (e) => e.preventDefault());

            // ===== Grid auxiliar =====
            const gridHelper = new THREE.GridHelper(20, 20, 0x334155, 0x1e293b); // Tailwind Slate 700/800
            gridHelper.position.y = -2;
            gridHelper.material.opacity = 0.5;
            gridHelper.material.transparent = true;
            scene.add(gridHelper);

            // ===== Ejes de referencia =====
            const axesGroup = new THREE.Group();
            // Eje X (rojo)
            const axisXGeo = new THREE.CylinderGeometry(0.02, 0.02, 3, 8);
            const axisXMat = new THREE.MeshBasicMaterial({{ color: 0xef4444 }}); // Tailwind Red 500
            const axisX = new THREE.Mesh(axisXGeo, axisXMat);
            axisX.rotation.z = -Math.PI / 2;
            axisX.position.set(1.5, -2, -10);
            axesGroup.add(axisX);
            // Eje Y (verde)
            const axisYGeo = new THREE.CylinderGeometry(0.02, 0.02, 3, 8);
            const axisYMat = new THREE.MeshBasicMaterial({{ color: 0x10b981 }}); // Tailwind Emerald 500
            const axisY = new THREE.Mesh(axisYGeo, axisYMat);
            axisY.position.set(0, -0.5, -10);
            axesGroup.add(axisY);
            // Eje Z (azul)  
            const axisZGeo = new THREE.CylinderGeometry(0.02, 0.02, 3, 8);
            const axisZMat = new THREE.MeshBasicMaterial({{ color: 0x3b82f6 }}); // Tailwind Blue 500
            const axisZ = new THREE.Mesh(axisZGeo, axisZMat);
            axisZ.rotation.x = Math.PI / 2;
            axisZ.position.set(0, -2, -8.5);
            axesGroup.add(axisZ);
            scene.add(axesGroup);

            // ===== Construir tubería como path 3D =====
            const tubePoints = [];
            const numSegments = 50;
            const halfL = TRAMO.longitud / 2;

            for (let i = 0; i <= numSegments; i++) {{
                const t = i / numSegments;
                const x = -halfL + t * TRAMO.longitud;
                const y = t * TRAMO.altura * TRAMO.signo;
                tubePoints.push(new THREE.Vector3(x, y, 0));
            }}

            const tubePath = new THREE.CatmullRomCurve3(tubePoints);
            const tubeGeometry = new THREE.TubeGeometry(tubePath, 64, TRAMO.diametro, 16, false);

            // Gradiente de presión: azul (alta) → rojo (baja)
            const colors = [];
            const posAttr = tubeGeometry.attributes.position;
            for (let i = 0; i < posAttr.count; i++) {{
                const x = posAttr.getX(i);
                const t = (x + halfL) / TRAMO.longitud;
                const r = t * 0.9 + 0.1;
                const g = 0.2 + (1 - t) * 0.3;
                const b = (1 - t) * 0.8 + 0.2;
                colors.push(r, g, b);
            }}
            tubeGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

            const tubeMaterial = new THREE.MeshPhysicalMaterial({{
                vertexColors: true,
                transparent: true,
                opacity: 0.85,
                roughness: 0.2,
                metalness: 0.1,
                clearcoat: 0.8,
                clearcoatRoughness: 0.2,
                side: THREE.DoubleSide,
            }});
            const tubeMesh = new THREE.Mesh(tubeGeometry, tubeMaterial);
            tubeMesh.castShadow = true;
            scene.add(tubeMesh);

            // Borde de la tubería (wireframe sutil)
            const wireGeo = new THREE.TubeGeometry(tubePath, 32, TRAMO.diametro * 1.01, 8, false);
            const wireMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.1 }}); // Tailwind Sky 400
            scene.add(new THREE.Mesh(wireGeo, wireMat));

            // ===== Tanque de entrada (inicio) =====
            const tankGeo = new THREE.CylinderGeometry(0.5, 0.5, 1.2, 32);
            const tankMat = new THREE.MeshStandardMaterial({{ color: 0x64748b, roughness: 0.4, metalness: 0.6 }}); // Tailwind Slate 500
            const tankEntrada = new THREE.Mesh(tankGeo, tankMat);
            tankEntrada.position.set(-halfL - 0.8, tubePoints[0].y, 0);
            tankEntrada.castShadow = true;
            scene.add(tankEntrada);

            // Tanque de salida (fin)
            const tankSalida = new THREE.Mesh(tankGeo.clone(), tankMat.clone());
            tankSalida.position.set(halfL + 0.8, tubePoints[tubePoints.length-1].y, 0);
            tankSalida.castShadow = true;
            scene.add(tankSalida);

            // ===== Bomba o válvula al inicio =====
            if (TRAMO.tipo === 'bomba') {{
                // Cuerpo de la bomba  
                const bombaGeo = new THREE.SphereGeometry(0.4, 32, 32);
                const bombaMat = new THREE.MeshStandardMaterial({{ color: 0x10b981, roughness: 0.3, metalness: 0.8, emissive: 0x059669, emissiveIntensity: 0.2 }}); // Tailwind Emerald
                const bomba = new THREE.Mesh(bombaGeo, bombaMat);
                bomba.position.set(-halfL + 0.5, tubePoints[1].y + 0.1, 0);
                bomba.castShadow = true;
                scene.add(bomba);

                // Indicador luminoso de la bomba
                const bombaLight = new THREE.PointLight(0x10b981, 1.0, 5);
                bombaLight.position.copy(bomba.position);
                scene.add(bombaLight);

                // Etiqueta "BOMBA"
                const canvas1 = document.createElement('canvas');
                canvas1.width = 256; canvas1.height = 64;
                const ctx1 = canvas1.getContext('2d');
                ctx1.fillStyle = '#10b981';
                ctx1.font = 'bold 28px Inter, sans-serif';
                ctx1.textAlign = 'center';
                ctx1.fillText('BOMBA', 128, 40);
                const tex1 = new THREE.CanvasTexture(canvas1);
                const spriteMat1 = new THREE.SpriteMaterial({{ map: tex1 }});
                const sprite1 = new THREE.Sprite(spriteMat1);
                sprite1.position.set(-halfL + 0.5, tubePoints[1].y + 1.0, 0);
                sprite1.scale.set(2, 0.5, 1);
                scene.add(sprite1);
            }} else {{
                // Válvula de estrangulamiento
                const valvGeo = new THREE.TorusGeometry(0.35, 0.08, 16, 32);
                const valvMat = new THREE.MeshStandardMaterial({{ color: 0xf59e0b, roughness: 0.4, metalness: 0.7, emissive: 0xd97706, emissiveIntensity: 0.2 }}); // Tailwind Amber
                const valvula = new THREE.Mesh(valvGeo, valvMat);
                valvula.position.set(halfL - 0.5, tubePoints[tubePoints.length-2].y, 0);
                valvula.rotation.y = Math.PI / 2;
                valvula.castShadow = true;
                scene.add(valvula);

                const valvLight = new THREE.PointLight(0xf59e0b, 1.0, 5);
                valvLight.position.copy(valvula.position);
                scene.add(valvLight);
            }}

            // ===== Codos (en posiciones distribuidas) =====
            let codoCount = 0;
            TRAMO.accesorios.forEach(acc => {{
                if (acc.nombre && acc.nombre.toLowerCase().includes('codo') && acc.cantidad > 0) {{
                    for (let c = 0; c < acc.cantidad; c++) {{
                        codoCount++;
                        const t = codoCount / (codoCount + 2);
                        const pos = tubePath.getPoint(t * 0.7 + 0.15);
                        const codoGeo = new THREE.TorusGeometry(0.2, 0.06, 16, 24, Math.PI / 2);
                        const codoMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, roughness: 0.3, metalness: 0.8 }}); // Tailwind Slate 400
                        const codo = new THREE.Mesh(codoGeo, codoMat);
                        codo.position.copy(pos);
                        codo.position.y += 0.3;
                        codo.castShadow = true;
                        scene.add(codo);
                    }}
                }}
            }});

            // ===== Partículas de flujo animadas =====
            const particleCount = 200;
            const particleGeometry = new THREE.BufferGeometry();
            const particlePositions = new Float32Array(particleCount * 3);
            const particleSpeeds = new Float32Array(particleCount);
            const particlePhases = new Float32Array(particleCount);

            for (let i = 0; i < particleCount; i++) {{
                particlePhases[i] = Math.random();
                particleSpeeds[i] = 0.3 + Math.random() * 0.4;
                const t = particlePhases[i];
                const pos = tubePath.getPoint(t);
                const offsetR = (Math.random() - 0.5) * TRAMO.diametro * 0.7;
                const offsetAngle = Math.random() * Math.PI * 2;
                particlePositions[i * 3] = pos.x + offsetR * Math.cos(offsetAngle);
                particlePositions[i * 3 + 1] = pos.y + offsetR * Math.sin(offsetAngle);
                particlePositions[i * 3 + 2] = pos.z + offsetR * Math.sin(offsetAngle * 0.5);
            }}

            particleGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

            const particleMaterial = new THREE.PointsMaterial({{
                color: 0x38bdf8, // Tailwind Sky 400
                size: 0.08,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending,
            }});

            const particles = new THREE.Points(particleGeometry, particleMaterial);
            scene.add(particles);

            // ===== Flechas de dirección del flujo =====
            const arrowCount = 5;
            const arrowGroup = new THREE.Group();
            for (let i = 0; i < arrowCount; i++) {{
                const t = (i + 0.5) / arrowCount;
                const pos = tubePath.getPoint(t);
                const tangent = tubePath.getTangent(t);
                
                const arrowGeo = new THREE.ConeGeometry(0.1, 0.3, 16);
                const arrowMat = new THREE.MeshStandardMaterial({{ 
                    color: 0x38bdf8, // Tailwind Sky 400
                    emissive: 0x0284c7, // Tailwind Sky 600
                    emissiveIntensity: 0.5,
                    transparent: true, 
                    opacity: 0.8,
                    roughness: 0.2,
                    metalness: 0.5
                }});
                const arrow = new THREE.Mesh(arrowGeo, arrowMat);
                arrow.position.copy(pos);
                arrow.position.y += TRAMO.diametro + 0.2;
                
                // Orientar la flecha en la dirección del flujo
                arrow.quaternion.setFromUnitVectors(
                    new THREE.Vector3(0, 1, 0),
                    tangent.normalize()
                );
                
                arrowGroup.add(arrow);
            }}
            scene.add(arrowGroup);

            // ===== Escala de presión (barra lateral derecha) =====
            const barGeo = new THREE.PlaneGeometry(0.3, 5, 1, 20);
            const barColors = [];
            const barPosAttr = barGeo.attributes.position;
            for (let i = 0; i < barPosAttr.count; i++) {{
                const y = barPosAttr.getY(i);
                const t = (y + 2.5) / 5.0;
                barColors.push(t * 0.9 + 0.1, 0.2 + (1 - t) * 0.3, (1 - t) * 0.8 + 0.2);
            }}
            barGeo.setAttribute('color', new THREE.Float32BufferAttribute(barColors, 3));
            const barMat = new THREE.MeshBasicMaterial({{ vertexColors: true, side: THREE.DoubleSide }});
            const bar = new THREE.Mesh(barGeo, barMat);
            bar.position.set(halfL + 3, 0, 0);
            scene.add(bar);

            // Etiquetas de la barra de presión
            ['Alta P', 'Baja P'].forEach((txt, idx) => {{
                const c = document.createElement('canvas');
                c.width = 128; c.height = 32;
                const ct = c.getContext('2d');
                ct.fillStyle = idx === 0 ? '#38bdf8' : '#ef4444'; // Tailwind Sky 400 / Red 500
                ct.font = '18px Inter, sans-serif';
                ct.textAlign = 'center';
                ct.fillText(txt, 64, 22);
                const tx = new THREE.CanvasTexture(c);
                const sm = new THREE.SpriteMaterial({{ map: tx }});
                const sp = new THREE.Sprite(sm);
                sp.position.set(halfL + 3, idx === 0 ? -3 : 3, 0);
                sp.scale.set(1.2, 0.3, 1);
                scene.add(sp);
            }});

            // ===== Animación =====
            const clock = new THREE.Clock();
            let autoRotateAngle = 0;

            function animate() {{
                requestAnimationFrame(animate);
                const delta = clock.getDelta();
                const elapsed = clock.getElapsedTime();

                // Animar partículas (flujo)
                const positions = particles.geometry.attributes.position.array;
                for (let i = 0; i < particleCount; i++) {{
                    particlePhases[i] += particleSpeeds[i] * delta * 0.15;
                    if (particlePhases[i] > 1.0) particlePhases[i] -= 1.0;

                    const t = particlePhases[i];
                    const pos = tubePath.getPoint(t);
                    const offsetR = Math.sin(elapsed * 2 + i) * TRAMO.diametro * 0.3;
                    const offsetAngle = elapsed * 1.5 + i * 0.5;

                    positions[i * 3] = pos.x + offsetR * Math.cos(offsetAngle);
                    positions[i * 3 + 1] = pos.y + offsetR * Math.sin(offsetAngle);
                    positions[i * 3 + 2] = pos.z + offsetR * Math.cos(offsetAngle * 0.7) * 0.5;
                }}
                particles.geometry.attributes.position.needsUpdate = true;

                // Pulso suave de las flechas
                arrowGroup.children.forEach((arrow, idx) => {{
                    const pulse = 0.8 + 0.2 * Math.sin(elapsed * 3 + idx);
                    arrow.scale.set(pulse, pulse, pulse);
                }});

                // Auto-rotación suave si no hay interacción
                if (!isDragging && !isPanning) {{
                    autoRotateAngle += delta * 0.05;
                    // No auto-rotar para no marear
                }}

                renderer.render(scene, camera);
            }}

            updateCamera();
            animate();

            // Responsivo
            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    return html


def generar_modelo_tramo(num_tramo: int, resultados: dict) -> str:
    """
    Genera el HTML del modelo 3D para un tramo específico
    usando los resultados calculados.
    """
    from core.tramos import obtener_definicion_tramos
    
    definiciones = obtener_definicion_tramos()
    defn = definiciones[num_tramo]
    r = resultados[num_tramo]
    
    # Calcular presiones aproximadas
    presion_entrada = 0.0  # Presión manométrica al inicio (m.c.a.)
    if not r['es_bajada']:
        presion_entrada = r['carga_estacion']  # Después de la bomba
    presion_salida = presion_entrada - r['perdidas_friccion_colebrook'] - r['perdidas_menores']
    
    return generar_html_modelo_3d(
        num_tramo=num_tramo,
        longitud=defn['longitud_tuberia'],
        diametro=r.get('area', 0.01865) * 4 / 3.14159,  # Recalcular D del área si aplica
        pendiente=defn['pendiente'],
        altura=defn['altura'],
        velocidad=r['velocidad'],
        presion_entrada=presion_entrada,
        presion_salida=presion_salida,
        accesorios=defn['accesorios'],
        tipo=defn['tipo'],
        potencia_kw=r['potencia_kw'],
        reynolds=r['reynolds'],
        f_friccion=r['f_colebrook'],
        perdidas_friccion=r['perdidas_friccion_colebrook'],
        perdidas_menores=r['perdidas_menores'],
    )
