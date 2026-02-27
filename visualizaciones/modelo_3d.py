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
                /* Gradient Background: Night Sky to Earth */
                background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
                overflow: hidden; 
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                color: #f8fafc;
            }}
            #container {{ width: 100%; height: 700px; position: relative; }}
            #info-panel {{
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(15, 23, 42, 0.85);
                color: #f8fafc;
                padding: 20px;
                border-radius: 12px;
                font-size: 13px;
                line-height: 1.5;
                border: 1px solid rgba(148, 163, 184, 0.2);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
                max-width: 280px;
                z-index: 10;
            }}
            #info-panel h3 {{
                color: {color_principal};
                margin-bottom: 10px;
                font-size: 16px;
                font-weight: 600;
                border-bottom: 1px solid rgba(148, 163, 184, 0.2);
                padding-bottom: 6px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            #info-panel .valor {{ color: #38bdf8; font-weight: 600; float: right; }} /* Tailwind Sky 400 */
            #info-panel .label {{ color: #94a3b8; }} /* Tailwind Slate 400 */
            #info-panel .row {{ margin-bottom: 4px; border-bottom: 1px dashed rgba(255,255,255,0.05); padding-bottom: 2px; }}

            #legend {{
                position: absolute;
                bottom: 20px;
                left: 20px;
                background: rgba(15, 23, 42, 0.85);
                color: #f8fafc;
                padding: 12px 16px;
                border-radius: 12px;
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(148, 163, 184, 0.2);
                font-size: 11px;
                z-index: 10;
            }}
            #legend div {{ margin: 3px 0; display: flex; align-items: center; gap: 8px; }}
            .color-box {{ 
                width: 12px; height: 12px; border-radius: 3px;
                display: inline-block; border: 1px solid rgba(255,255,255,0.2); 
            }}

            #controls {{
                position: absolute;
                top: 20px;
                right: 20px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                z-index: 20;
            }}
            .ctrl-btn {{
                background: rgba(30, 41, 59, 0.8);
                color: #e2e8f0;
                border: 1px solid rgba(148, 163, 184, 0.3);
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 500;
                transition: all 0.2s;
                backdrop-filter: blur(4px);
            }}
            .ctrl-btn:hover {{ background: rgba(51, 65, 85, 0.9); color: #fff; border-color: #38bdf8; }}
            .ctrl-btn.active {{ background: #0ea5e9; color: white; border-color: #0ea5e9; }}

            #tooltip {{
                position: absolute;
                background: rgba(15, 23, 42, 0.95);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                pointer-events: none;
                display: none;
                z-index: 100;
                border: 1px solid #38bdf8;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}

            #help-text {{
                position: absolute;
                bottom: 20px;
                right: 20px;
                color: #64748b;
                font-size: 11px;
                text-align: right;
                pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="info-panel">
                <h3><span>🔧</span> Tramo {num_tramo}</h3>
                <div class="row"><span class="label">Tipo:</span> <span class="valor">{tipo.replace('_', ' ').title()}</span></div>
                <div class="row"><span class="label">Longitud:</span> <span class="valor">{longitud:.1f} m</span></div>
                <div class="row"><span class="label">Diámetro:</span> <span class="valor">{diametro*100:.1f} cm</span></div>
                <div class="row"><span class="label">Pendiente:</span> <span class="valor">{pendiente:.1f}°</span></div>
                <div class="row"><span class="label">Δ Altura:</span> <span class="valor">{'+' if altura>=0 else ''}{altura:.0f} m</span></div>
                <div class="row"><span class="label">Velocidad:</span> <span class="valor">{velocidad:.2f} m/s</span></div>
                <div class="row"><span class="label">Reynolds:</span> <span class="valor">{reynolds:,.0f}</span></div>
                <div class="row"><span class="label">f (Colebrook):</span> <span class="valor">{f_friccion:.6f}</span></div>
                <div class="row"><span class="label">Potencia:</span> <span class="valor">{potencia_kw:.2f} kW</span></div>
            </div>

            <div id="legend">
                <div style="margin-bottom: 6px; font-weight: 600; color: #cbd5e1; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 4px;">Leyenda</div>
                <div><span class="color-box" style="background: linear-gradient(90deg, #38bdf8, #ef4444)"></span> Gradiente Presión</div>
                <div><span class="color-box" style="background:#10b981"></span> Bomba / Estación</div>
                <div><span class="color-box" style="background:#f59e0b"></span> Válvula Control</div>
                <div><span class="color-box" style="background:#94a3b8"></span> Accesorios (Codos)</div>
                <div><span class="color-box" style="background:#38bdf8"></span> Flujo Agua</div>
            </div>

            <div id="controls">
                <button class="ctrl-btn active" id="btn-rotate" onclick="toggleRotation()">↻ Rotación Auto</button>
                <button class="ctrl-btn" id="btn-reset" onclick="resetView()">⌖ Reset Vista</button>
                <button class="ctrl-btn" id="btn-labels" onclick="toggleLabels()">🏷️ Etiquetas</button>
            </div>

            <div id="help-text">
                Click + Arrastrar: Rotar | Scroll: Zoom | Click Derecho: Pan
            </div>

            <div id="tooltip"></div>
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
            const tooltip = document.getElementById('tooltip');

            const scene = new THREE.Scene();
            // Gradient handled by CSS, scene background transparent or matching start color for fog
            scene.fog = new THREE.FogExp2(0x0f172a, 0.015);

            const camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 1000);
            const initialCameraPos = {{ x: 10, y: 6, z: 14 }};
            camera.position.set(initialCameraPos.x, initialCameraPos.y, initialCameraPos.z);
            camera.lookAt(0, 0, 0);

            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);

            // ===== Luces Mejoradas =====
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
            dirLight.position.set(10, 20, 10);
            dirLight.castShadow = true;
            dirLight.shadow.mapSize.width = 2048;
            dirLight.shadow.mapSize.height = 2048;
            dirLight.shadow.bias = -0.0005;
            scene.add(dirLight);

            const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.3); // Sky fill
            fillLight.position.set(-10, 10, -10);
            scene.add(fillLight);

            // ===== Interaction Logic =====
            let isDragging = false;
            let isPanning = false;
            let autoRotate = true;
            let previousMousePosition = {{ x: 0, y: 0 }};
            let orbitAngle = {{ theta: 0.7, phi: 0.5 }};
            let orbitRadius = 18;
            let panOffset = {{ x: 0, y: 0, z: 0 }};

            // Raycaster for tooltips
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            const interactables = [];

            function updateCamera() {{
                // Smooth damping could be added here
                camera.position.x = orbitRadius * Math.sin(orbitAngle.theta) * Math.cos(orbitAngle.phi) + panOffset.x;
                camera.position.y = orbitRadius * Math.sin(orbitAngle.phi) + panOffset.y;
                camera.position.z = orbitRadius * Math.cos(orbitAngle.theta) * Math.cos(orbitAngle.phi) + panOffset.z;
                camera.lookAt(panOffset.x, panOffset.y, panOffset.z);
            }}

            // Event Listeners
            container.addEventListener('mousedown', (e) => {{
                if (e.button === 0) {{ isDragging = true; autoRotate = false; updateBtns(); }}
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
                    const panSpeed = 0.03;
                    // Approximate panning relative to camera view
                    const forward = new THREE.Vector3();
                    camera.getWorldDirection(forward);
                    const right = new THREE.Vector3().crossVectors(forward, camera.up).normalize();
                    const up = new THREE.Vector3().crossVectors(right, forward).normalize();

                    panOffset.x -= (right.x * deltaMove.x - up.x * deltaMove.y) * panSpeed;
                    panOffset.y -= (right.y * deltaMove.x - up.y * deltaMove.y) * panSpeed;
                    panOffset.z -= (right.z * deltaMove.x - up.z * deltaMove.y) * panSpeed;
                    updateCamera();
                }}

                previousMousePosition = {{ x: e.clientX, y: e.clientY }};

                // Tooltip Logic
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(interactables);

                if (intersects.length > 0) {{
                    const obj = intersects[0].object;
                    if (obj.userData.tooltip) {{
                        tooltip.style.display = 'block';
                        tooltip.style.left = (e.clientX + 10) + 'px';
                        tooltip.style.top = (e.clientY + 10) + 'px';
                        tooltip.textContent = obj.userData.tooltip;
                        document.body.style.cursor = 'pointer';
                    }}
                }} else {{
                    tooltip.style.display = 'none';
                    document.body.style.cursor = 'default';
                }}
            }});

            container.addEventListener('mouseup', () => {{ isDragging = false; isPanning = false; }});
            container.addEventListener('mouseleave', () => {{ isDragging = false; isPanning = false; }});
            container.addEventListener('wheel', (e) => {{
                e.preventDefault();
                orbitRadius = Math.max(5, Math.min(40, orbitRadius + e.deltaY * 0.02));
                updateCamera();
            }});
            container.addEventListener('contextmenu', (e) => e.preventDefault());

            // ===== Environment =====
            // Grid
            const gridHelper = new THREE.GridHelper(30, 30, 0x334155, 0x1e293b);
            gridHelper.position.y = -3;
            scene.add(gridHelper);

            // ===== Tubería =====
            const tubePoints = [];
            const numSegments = 60;
            const halfL = TRAMO.longitud / 2;

            for (let i = 0; i <= numSegments; i++) {{
                const t = i / numSegments;
                const x = -halfL + t * TRAMO.longitud;
                const y = t * TRAMO.altura * TRAMO.signo;
                tubePoints.push(new THREE.Vector3(x, y, 0));
            }}

            const tubePath = new THREE.CatmullRomCurve3(tubePoints);
            const tubeGeometry = new THREE.TubeGeometry(tubePath, 64, TRAMO.diametro, 24, false);

            // Vertex Colors for Pressure Gradient
            const colors = [];
            const posAttr = tubeGeometry.attributes.position;
            for (let i = 0; i < posAttr.count; i++) {{
                const x = posAttr.getX(i);
                // Normalized position along tube (approx)
                const t = (x + halfL) / TRAMO.longitud;
                // Color Map: Blue (0.2, 0.7, 1.0) to Red (1.0, 0.2, 0.2)
                const r = t * 0.8 + 0.2;
                const g = 0.2 + (1-t) * 0.5; // less green
                const b = (1 - t) * 0.8 + 0.2;
                colors.push(r, g, b);
            }}
            tubeGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

            const tubeMaterial = new THREE.MeshPhysicalMaterial({{
                vertexColors: true,
                transparent: true,
                opacity: 0.9,
                roughness: 0.1,
                metalness: 0.2,
                clearcoat: 1.0,
                side: THREE.DoubleSide
            }});
            const tubeMesh = new THREE.Mesh(tubeGeometry, tubeMaterial);
            tubeMesh.castShadow = true;
            tubeMesh.receiveShadow = true;
            tubeMesh.userData = {{ tooltip: "Tubería Principal (L: " + TRAMO.longitud.toFixed(1) + "m)" }};
            scene.add(tubeMesh);
            interactables.push(tubeMesh);

            // Wireframe Overlay
            const wireGeo = new THREE.TubeGeometry(tubePath, 32, TRAMO.diametro * 1.02, 8, false);
            const wireMat = new THREE.MeshBasicMaterial({{ color: 0x7dd3fc, wireframe: true, transparent: true, opacity: 0.15 }});
            scene.add(new THREE.Mesh(wireGeo, wireMat));

            // ===== Componentes (Bomba/Válvula/Tanques) =====
            const tankGeo = new THREE.CylinderGeometry(0.6, 0.6, 1.5, 32);
            const tankMat = new THREE.MeshStandardMaterial({{ color: 0x64748b, roughness: 0.5, metalness: 0.5 }});

            // Entrada
            const tankIn = new THREE.Mesh(tankGeo, tankMat);
            tankIn.position.set(-halfL - 0.9, tubePoints[0].y, 0);
            tankIn.castShadow = true;
            tankIn.userData = {{ tooltip: "Inicio Tramo" }};
            scene.add(tankIn);
            interactables.push(tankIn);

            // Salida
            const tankOut = new THREE.Mesh(tankGeo.clone(), tankMat.clone());
            tankOut.position.set(halfL + 0.9, tubePoints[tubePoints.length-1].y, 0);
            tankOut.castShadow = true;
            tankOut.userData = {{ tooltip: "Fin Tramo" }};
            scene.add(tankOut);
            interactables.push(tankOut);

            // Elemento Principal
            if (TRAMO.tipo === 'bomba') {{
                const bombaGroup = new THREE.Group();
                const bBody = new THREE.Mesh(
                    new THREE.SphereGeometry(0.5, 32, 32),
                    new THREE.MeshStandardMaterial({{ color: 0x10b981, roughness: 0.2, metalness: 0.6 }})
                );
                const bBase = new THREE.Mesh(
                    new THREE.BoxGeometry(1, 0.2, 1),
                    new THREE.MeshStandardMaterial({{ color: 0x334155 }})
                );
                bBase.position.y = -0.6;
                bombaGroup.add(bBody);
                bombaGroup.add(bBase);

                bombaGroup.position.set(-halfL + 1.5, tubePoints[2].y + 0.2, 0);
                bombaGroup.userData = {{ tooltip: "Estación de Bombeo" }};
                scene.add(bombaGroup);
                interactables.push(bBody); // Add specific mesh to raycaster

                // Glow effect
                const light = new THREE.PointLight(0x10b981, 1, 8);
                light.position.copy(bombaGroup.position);
                scene.add(light);
            }} else {{
                // Válvula
                const valBody = new THREE.Mesh(
                    new THREE.TorusGeometry(0.4, 0.1, 16, 32),
                    new THREE.MeshStandardMaterial({{ color: 0xf59e0b, roughness: 0.3, metalness: 0.7 }})
                );
                valBody.rotation.y = Math.PI/2;
                valBody.position.set(halfL - 1.5, tubePoints[tubePoints.length-3].y, 0);
                valBody.userData = {{ tooltip: "Válvula de Control" }};
                valBody.castShadow = true;
                scene.add(valBody);
                interactables.push(valBody);

                const light = new THREE.PointLight(0xf59e0b, 1, 8);
                light.position.copy(valBody.position);
                scene.add(light);
            }}

            // ===== Accesorios (Codos) =====
            let codoCount = 0;
            TRAMO.accesorios.forEach(acc => {{
                if (acc.nombre && acc.nombre.toLowerCase().includes('codo') && acc.cantidad > 0) {{
                    for (let c = 0; c < acc.cantidad; c++) {{
                        codoCount++;
                        const t = codoCount / (acc.cantidad + 2); // Distribute simply
                        // A bit of offset logic
                        const t_pos = 0.2 + (0.6 * (c+1)/(acc.cantidad+1));
                        const pos = tubePath.getPoint(t_pos);

                        const codoGeo = new THREE.TorusGeometry(TRAMO.diametro * 1.2, TRAMO.diametro * 0.2, 16, 24, Math.PI / 2);
                        const codoMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, roughness: 0.3, metalness: 0.8 }});
                        const codo = new THREE.Mesh(codoGeo, codoMat);

                        codo.position.copy(pos);
                        // Orient randomly to look like fittings
                        codo.rotation.x = Math.random() * Math.PI;
                        codo.rotation.y = Math.random() * Math.PI;
                        codo.castShadow = true;
                        codo.userData = {{ tooltip: "Codo / Accesorio" }};

                        scene.add(codo);
                        interactables.push(codo);
                    }}
                }}
            }});

            // ===== Partículas (Flujo) =====
            const particleCount = 200; // Reduced for performance
            const pGeo = new THREE.BufferGeometry();
            const pPos = new Float32Array(particleCount * 3);
            // Pre-calculate random values for better performance
            const pOffsets = [];

            for(let i=0; i<particleCount; i++) {{
                const r = TRAMO.diametro * 0.35;
                const theta = Math.random() * Math.PI * 2;
                pOffsets.push({{
                    r: r * (0.5 + Math.random() * 0.5),
                    theta: theta,
                    speed: 0.2 + Math.random() * 0.3,
                    phase: Math.random()
                }});
            }}
            pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));

            const pMat = new THREE.PointsMaterial({{
                color: 0xe0f2fe,
                size: 0.1,
                transparent: true,
                opacity: 0.6,
                blending: THREE.AdditiveBlending
            }});
            const particles = new THREE.Points(pGeo, pMat);
            scene.add(particles);

            // ===== Labels Sprites =====
            const labelGroup = new THREE.Group();
            scene.add(labelGroup);

            function createLabel(text, pos) {{
                const canvas = document.createElement('canvas');
                canvas.width = 256; canvas.height = 64;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';

                // Manual Rounded Rect for compatibility
                const x = 0, y = 0, w = 256, h = 64, r = 12;
                ctx.beginPath();
                ctx.moveTo(x + r, y);
                ctx.lineTo(x + w - r, y);
                ctx.quadraticCurveTo(x + w, y, x + w, y + r);
                ctx.lineTo(x + w, y + h - r);
                ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
                ctx.lineTo(x + r, y + h);
                ctx.quadraticCurveTo(x, y + h, x, y + h - r);
                ctx.lineTo(x, y + r);
                ctx.quadraticCurveTo(x, y, x + r, y);
                ctx.closePath();
                ctx.fill();

                ctx.strokeStyle = '#38bdf8';
                ctx.lineWidth = 4;
                ctx.stroke();

                ctx.fillStyle = '#f8fafc';
                ctx.font = 'bold 32px Inter, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(text, 128, 42);
                
                const tex = new THREE.CanvasTexture(canvas);
                const mat = new THREE.SpriteMaterial({{ map: tex, transparent: true }});
                const sprite = new THREE.Sprite(mat);
                sprite.position.copy(pos);
                sprite.scale.set(3, 0.75, 1);
                return sprite;
            }}

            // Add Start/End labels
            labelGroup.add(createLabel("Inicio", new THREE.Vector3(-halfL, tubePoints[0].y + 1.5, 0)));
            labelGroup.add(createLabel("Fin", new THREE.Vector3(halfL, tubePoints[tubePoints.length-1].y + 1.5, 0)));

            // ===== UI Functions =====
            window.toggleRotation = () => {{
                autoRotate = !autoRotate;
                updateBtns();
            }};

            window.resetView = () => {{
                autoRotate = false;
                panOffset = {{ x: 0, y: 0, z: 0 }};
                orbitRadius = 18;
                orbitAngle = {{ theta: 0.7, phi: 0.5 }};
                updateCamera();
                updateBtns();
            }};

            window.toggleLabels = () => {{
                labelGroup.visible = !labelGroup.visible;
                const btn = document.getElementById('btn-labels');
                btn.classList.toggle('active');
            }};

            function updateBtns() {{
                const btnRot = document.getElementById('btn-rotate');
                if(autoRotate) btnRot.classList.add('active');
                else btnRot.classList.remove('active');
            }}

            // ===== Animation Loop =====
            const clock = new THREE.Clock();

            function animate() {{
                requestAnimationFrame(animate);
                const delta = clock.getDelta();
                const elapsed = clock.getElapsedTime();

                // Optimized Particle System Update
                const positions = particles.geometry.attributes.position.array;
                for(let i=0; i<particleCount; i++) {{
                    const p = pOffsets[i];
                    p.phase += p.speed * delta * 0.4;
                    if(p.phase > 1) p.phase -= 1;

                    const curvePos = tubePath.getPoint(p.phase);

                    // Simple rotation for swirl effect without heavy math
                    const angle = p.theta + elapsed * 2;

                    positions[i*3] = curvePos.x + Math.cos(angle) * p.r;
                    positions[i*3+1] = curvePos.y + Math.sin(angle) * p.r;
                    positions[i*3+2] = curvePos.z;
                }}
                particles.geometry.attributes.position.needsUpdate = true;

                // Auto Rotation
                if (autoRotate) {{
                    orbitAngle.theta += delta * 0.1;
                    updateCamera();
                }}

                renderer.render(scene, camera);
            }}

            animate();

            // Resize Handler
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
