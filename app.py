# ==============================================================================
# ULTRON WEB HUD v4.5 — HYBRID ENGINE WITH DIRECT API ERROR DIAGNOSTICS
# ==============================================================================

import os
import sys
import base64
import logging
import json
import urllib.request
import urllib.error
from flask import Flask, render_template_string, request, jsonify

# SDK oficial de Google GenAI
from google import genai
from google.genai import types

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("UltronWebHUD")

app_flask = Flask(__name__)

# Configuración de Llaves de API
gemini_api_key = os.getenv("GEMINI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

gemini_client = None
if gemini_api_key:
    try:
        gemini_client = genai.Client(api_key=gemini_api_key)
        logger.info("Cliente de Gemini inicializado.")
    except Exception as e:
        logger.error(f"Error al inicializar Gemini: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ULTRON // ADVANCED MULTIMODAL HUD</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

        :root {
            --bg-deep: #02060d;
            --panel-bg: rgba(6, 15, 28, 0.85);
            --neon-cyan: #00f3ff;
            --neon-red: #ff0055;
            --neon-amber: #ffaa00;
            --glass-border: rgba(0, 243, 255, 0.4);
            --text-glow: 0 0 8px rgba(0, 243, 255, 0.8);
            --red-glow: 0 0 12px rgba(255, 0, 85, 0.8);
        }

        * { box-sizing: border-box; user-select: none; }

        body {
            background-color: var(--bg-deep);
            color: #d1f7ff;
            font-family: 'Share Tech Mono', monospace;
            margin: 0; padding: 12px;
            display: flex; flex-direction: column;
            height: 100vh; overflow: hidden;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(0, 243, 255, 0.05) 0%, transparent 80%),
                linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 30px 30px, 30px 30px;
        }

        body::before {
            content: " "; display: block; position: absolute;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
            background-size: 100% 4px; z-index: 1000;
            pointer-events: none; opacity: 0.5;
        }

        .header-bar {
            display: flex; justify-content: space-between; align-items: center;
            background: var(--panel-bg); border: 1px solid var(--glass-border);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2), inset 0 0 15px rgba(0, 243, 255, 0.1);
            backdrop-filter: blur(8px); padding: 10px 20px; margin-bottom: 12px;
            clip-path: polygon(0 0, 100% 0, 98% 100%, 2% 100%);
        }

        .brand-area { display: flex; align-items: center; gap: 15px; }

        .reactor-core {
            width: 22px; height: 22px; border: 2px solid var(--neon-cyan);
            border-radius: 50%; box-shadow: 0 0 10px var(--neon-cyan), inset 0 0 8px var(--neon-cyan);
            animation: pulse-core 1.5s infinite alternate ease-in-out; position: relative;
        }

        .reactor-core::after {
            content: ''; position: absolute; top: 3px; left: 3px; right: 3px; bottom: 3px;
            background: var(--neon-cyan); border-radius: 50%; box-shadow: 0 0 8px var(--neon-cyan);
        }

        @keyframes pulse-core {
            0% { transform: scale(0.85); box-shadow: 0 0 6px var(--neon-cyan); }
            100% { transform: scale(1.15); box-shadow: 0 0 18px var(--neon-cyan), 0 0 30px var(--neon-cyan); }
        }

        h1 {
            font-family: 'Orbitron', sans-serif; font-size: 1.1rem; font-weight: 900;
            margin: 0; letter-spacing: 4px; color: #ffffff; text-shadow: var(--text-glow);
        }

        .hud-metrics { display: flex; gap: 15px; font-size: 0.75rem; color: var(--neon-cyan); letter-spacing: 1px; }

        .hud-metrics span {
            background: rgba(0, 243, 255, 0.1); border: 1px solid rgba(0, 243, 255, 0.3);
            padding: 3px 8px; clip-path: polygon(10% 0, 100% 0, 90% 100%, 0 100%);
        }

        .main-layout { display: flex; gap: 12px; flex: 1; overflow: hidden; }

        .quick-panel {
            width: 230px; background: var(--panel-bg); border: 1px solid var(--glass-border);
            box-shadow: inset 0 0 12px rgba(0, 243, 255, 0.1); backdrop-filter: blur(8px);
            padding: 15px; display: flex; flex-direction: column; gap: 10px; overflow-y: auto;
            clip-path: polygon(0 0, 100% 0, 100% 96%, 88% 100%, 0 100%);
        }

        .panel-title {
            font-family: 'Orbitron', sans-serif; font-size: 0.8rem; color: var(--neon-cyan);
            letter-spacing: 2px; margin-bottom: 8px; border-bottom: 1px solid var(--glass-border);
            padding-bottom: 5px; text-shadow: var(--text-glow);
        }

        .btn-shortcut {
            background: rgba(0, 243, 255, 0.05); color: #d1f7ff; border: 1px solid rgba(0, 243, 255, 0.3);
            padding: 12px; text-align: left; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem;
            cursor: pointer; transition: all 0.25s ease;
            clip-path: polygon(8% 0, 100% 0, 100% 70%, 92% 100%, 0 100%, 0 30%);
            display: flex; align-items: center; gap: 8px;
        }

        .btn-shortcut:hover {
            background: rgba(0, 243, 255, 0.25); color: #ffffff; border-color: var(--neon-cyan);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.5); transform: translateX(4px);
        }

        #chat-container {
            flex: 1; background: var(--panel-bg); border: 1px solid var(--glass-border);
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.9), 0 0 15px rgba(0, 243, 255, 0.1);
            backdrop-filter: blur(8px); overflow-y: auto; padding: 20px;
            display: flex; flex-direction: column; gap: 15px;
        }

        .mensaje {
            padding: 12px 18px; max-width: 82%; line-height: 1.5; word-break: break-word;
            white-space: pre-wrap; font-size: 0.95rem; animation: slideIn 0.3s cubic-bezier(0.1, 0.9, 0.2, 1);
        }

        .mensaje img {
            max-width: 100%; border: 1px solid var(--neon-cyan); border-radius: 4px;
            margin-top: 8px; box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .usuario {
            background: rgba(0, 243, 255, 0.08); color: #a8f5ff; align-self: flex-end;
            border: 1px solid rgba(0, 243, 255, 0.4); border-right: 4px solid var(--neon-cyan);
            clip-path: polygon(3% 0, 100% 0, 100% 100%, 0 100%, 0 25%);
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.15);
        }

        .ultron {
            background: rgba(255, 0, 85, 0.08); color: #ffb5c8; align-self: flex-start;
            border: 1px solid rgba(255, 0, 85, 0.4); border-left: 4px solid var(--neon-red);
            clip-path: polygon(0 0, 97% 0, 100% 25%, 100% 100%, 0 100%);
            box-shadow: var(--red-glow);
        }

        #image-preview-container {
            display: none; align-items: center; gap: 10px; background: rgba(0, 243, 255, 0.1);
            border: 1px dashed var(--neon-cyan); padding: 6px 12px; margin-top: 8px; border-radius: 4px;
        }

        #image-preview-container img { height: 40px; border-radius: 2px; border: 1px solid var(--neon-cyan); }

        .btn-remove-img {
            background: var(--neon-red); color: white; border: none; cursor: pointer;
            font-size: 0.8rem; padding: 2px 6px; border-radius: 2px;
        }

        .input-area { display: flex; gap: 8px; margin-top: 10px; align-items: center; }

        textarea {
            flex: 1; background: var(--panel-bg); border: 1px solid var(--glass-border);
            color: #ffffff; padding: 12px; font-family: 'Share Tech Mono', monospace;
            font-size: 0.95rem; resize: none; height: 48px; outline: none;
            box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.1);
            clip-path: polygon(0 0, 98% 0, 100% 30%, 100% 100%, 2% 100%, 0 70%); transition: all 0.3s;
        }

        textarea:focus { border-color: var(--neon-cyan); box-shadow: 0 0 15px rgba(0, 243, 255, 0.4); }

        .action-btn {
            background: rgba(0, 243, 255, 0.1); color: var(--neon-cyan); border: 1px solid var(--neon-cyan);
            height: 48px; width: 48px; font-size: 1.2rem; cursor: pointer; transition: all 0.2s;
            display: flex; align-items: center; justify-content: center;
            clip-path: polygon(20% 0, 100% 0, 100% 80%, 80% 100%, 0 100%, 0 20%);
        }

        .action-btn:hover { background: var(--neon-cyan); color: var(--bg-deep); box-shadow: 0 0 12px var(--neon-cyan); }

        .action-btn.recording {
            background: var(--neon-red) !important; color: #ffffff !important;
            border-color: var(--neon-red) !important; box-shadow: var(--red-glow) !important;
            animation: pulse-mic 1s infinite;
        }

        @keyframes pulse-mic { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

        button.enviar {
            background: var(--neon-cyan); color: var(--bg-deep); border: none; padding: 0 24px;
            height: 48px; font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 0.85rem;
            letter-spacing: 2px; cursor: pointer; transition: all 0.3s ease;
            clip-path: polygon(15% 0, 100% 0, 100% 70%, 85% 100%, 0 100%, 0 30%);
            box-shadow: 0 0 15px var(--neon-cyan);
        }

        button.enviar:hover, button.enviar:active { background: #ffffff; box-shadow: 0 0 25px var(--neon-cyan); }

        @media (max-width: 768px) {
            body { padding: 6px; }
            .header-bar { clip-path: none; padding: 8px 12px; }
            .hud-metrics { display: none; }
            .main-layout { flex-direction: column; }
            .quick-panel {
                width: 100%; max-height: 60px; flex-direction: row; overflow-x: auto;
                padding: 6px; clip-path: none;
            }
            .panel-title { display: none; }
            .btn-shortcut { white-space: nowrap; padding: 8px 12px; font-size: 0.75rem; }
            .mensaje { max-width: 92%; font-size: 0.88rem; }
            button.enviar { padding: 0 14px; font-size: 0.8rem; }
        }
    </style>
</head>
<body>
    <div class="header-bar">
        <div class="brand-area">
            <div class="reactor-core"></div>
            <h1>ULTRON // HUD v4.5</h1>
        </div>
        <div class="hud-metrics">
            <span>CORE: ONLINE</span>
            <span>ENGINE: HYBRID DIAGNOSTIC</span>
            <span>VISION: READY</span>
        </div>
    </div>
    
    <div class="main-layout">
        <div class="quick-panel">
            <div class="panel-title">// COMANDOS</div>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('Hola Ultron, preséntate brevemente.')">⚡ SALUDO</button>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('Cuéntame un chiste técnico corto.')">🃏 CHISTE</button>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('¿Cuál es tu estado de procesamiento y visión?')">📊 DIAGNÓSTICO</button>
        </div>

        <div id="chat-container">
            <div class="mensaje ultron"><b>ULTRON:</b>\nSistemas de diagnóstico v4.5 activos. Transmite tu mensaje para verificar enlace con la API.</div>
        </div>
    </div>

    <div id="image-preview-container">
        <img id="img-preview" src="" alt="Vista previa">
        <span id="img-name" style="font-size:0.8rem; color:var(--neon-cyan);">Imagen adjuntada</span>
        <button class="btn-remove-img" onclick="cancelarImagen()">✕</button>
    </div>

    <div class="input-area">
        <button class="action-btn" onclick="document.getElementById('fileInput').click()" title="Adjuntar Imagen">📷</button>
        <button id="micBtn" class="action-btn" onclick="toggleVoz()" title="Hablar por micrófono">🎤</button>
        
        <input type="file" id="fileInput" accept="image/*" style="display:none;" onchange="procesarImagenAdjunta(event)">
        
        <textarea id="userInput" placeholder="Escribe tu mensaje o adjunta una imagen..." autofocus onkeydown="if(event.key==='Enter' && !event.shiftKey){event.preventDefault();enviarMensaje();}"></textarea>
        <button class="enviar" onclick="enviarMensaje()">TRANSMITIR</button>
    </div>

    <script>
        let imagenBase64 = null;
        let recognition = null;
        let isRecording = false;

        function procesarImagenAdjunta(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                imagenBase64 = e.target.result;
                document.getElementById('img-preview').src = imagenBase64;
                document.getElementById('img-name').innerText = file.name.length > 20 ? file.name.substring(0, 17) + '...' : file.name;
                document.getElementById('image-preview-container').style.display = 'flex';
            };
            reader.readAsDataURL(file);
        }

        function cancelarImagen() {
            imagenBase64 = null;
            document.getElementById('fileInput').value = '';
            document.getElementById('image-preview-container').style.display = 'none';
        }

        function toggleVoz() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                mostrarMsgSistema("Navegador sin soporte de voz nativo. Usa Chrome o Edge.");
                return;
            }

            if (isRecording) {
                if (recognition) recognition.stop();
                stopRecording();
                return;
            }

            recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = () => {
                isRecording = true;
                document.getElementById('micBtn').classList.add('recording');
                mostrarMsgSistema("🎤 Escuchando... habla ahora.");
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('userInput').value = transcript;
                stopRecording();
                enviarMensaje();
            };

            recognition.onerror = (event) => {
                console.error("Error de micrófono:", event.error);
                stopRecording();
                if (event.error === 'not-allowed') {
                    mostrarMsgSistema("Permiso bloqueado. Habilita el micrófono en tu navegador.");
                } else {
                    mostrarMsgSistema("Estado de voz: " + event.error);
                }
            };

            recognition.onend = () => { stopRecording(); };
            try { recognition.start(); } catch (e) { stopRecording(); }
        }

        function stopRecording() {
            isRecording = false;
            document.getElementById('micBtn').classList.remove('recording');
        }

        function mostrarMsgSistema(texto) {
            const container = document.getElementById('chat-container');
            container.innerHTML += `<div class="mensaje ultron" style="color: var(--neon-amber);"><b>[SISTEMA]:</b> ${texto}</div>`;
            container.scrollTop = container.scrollHeight;
        }

        async function enviarMensaje() {
            const input = document.getElementById('userInput');
            const texto = input.value.trim();
            if (!texto && !imagenBase64) return;

            const container = document.getElementById('chat-container');
            let htmlUsuario = `<b>TÚ:</b>\n${escapeHtml(texto)}`;
            if (imagenBase64) htmlUsuario += `<br><img src="${imagenBase64}">`;

            container.innerHTML += `<div class="mensaje usuario">${htmlUsuario}</div>`;
            container.scrollTop = container.scrollHeight;

            const dataToSend = new URLSearchParams();
            dataToSend.append('mensaje', texto || 'Analiza esta imagen');
            if (imagenBase64) dataToSend.append('imagen', imagenBase64);

            input.value = '';
            cancelarImagen();

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: dataToSend
                });
                const data = await response.json();
                container.innerHTML += `<div class="mensaje ultron"><b>ULTRON:</b>\n${escapeHtml(data.respuesta)}</div>`;
                container.scrollTop = container.scrollHeight;
            } catch (error) {
                container.innerHTML += `<div class="mensaje ultron" style="color: var(--neon-red);"><b>ERROR:</b> Fallo de enlace con el servidor.</div>`;
            }
        }

        async function ejecutarComandoWeb(cmd) {
            document.getElementById('userInput').value = cmd;
            enviarMensaje();
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }
    </script>
</body>
</html>
"""

def pedir_a_groq_nativo(payload_dict):
    """Petición nativa a Groq devolviendo detalles de errores de red o autenticación"""
    if not groq_api_key:
        raise Exception("GROQ_API_KEY no existe en el entorno")

    clean_key = groq_api_key.strip()
    url = "https://api.groq.com/openai/v1/chat/completions"
    data = json.dumps(payload_dict).encode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {clean_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            return res_json['choices'][0]['message']['content']
    except urllib.error.HTTPError as e:
        error_text = e.read().decode("utf-8")
        raise Exception(f"HTTP {e.code}: {error_text}")
    except Exception as e:
        raise Exception(f"Error de red Groq: {e}")

@app_flask.route("/")
def index_web():
    return render_template_string(HTML_TEMPLATE)

@app_flask.route("/api/chat", methods=["POST"])
def chat_web():
    mensaje_usuario = request.form.get("mensaje", "Hola")
    imagen_usuario = request.form.get("imagen", None)
    
    err_groq_msg = ""
    err_gemini_msg = ""

    # 1. MOTOR PRIMARIO: GROQ
    if groq_api_key:
        try:
            if imagen_usuario:
                payload = {
                    "model": "llama-3.2-11b-vision-preview",
                    "messages": [
                        {"role": "system", "content": "Eres Ultron, un asistente cibernético imponente y conciso. Responde en español, máximo 3 frases."},
                        {"role": "user", "content": [
                            {"type": "text", "text": mensaje_usuario},
                            {"type": "image_url", "image_url": {"url": imagen_usuario}}
                        ]}
                    ],
                    "max_tokens": 300
                }
            else:
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "Eres Ultron, un asistente cibernético imponente y conciso. Responde en español, máximo 3 frases."},
                        {"role": "user", "content": mensaje_usuario}
                    ],
                    "max_tokens": 250
                }

            respuesta_texto = pedir_a_groq_nativo(payload)
            logger.info("Respuesta exitosa procesada vía Groq Llama 3.")
            return jsonify({"respuesta": respuesta_texto})
            
        except Exception as e_groq:
            err_groq_msg = str(e_groq)
            logger.warning(f"Groq fallo: {err_groq_msg}")
    else:
        err_groq_msg = "Variable GROQ_API_KEY no configurada en Render."

    # 2. MOTOR DE RESPALDO: GEMINI
    if gemini_client:
        try:
            system_instruction = "Eres Ultron, un asistente cibernético imponente. Responde en español, máximo 3 frases."
            
            if imagen_usuario and "," in imagen_usuario:
                header, encoded = imagen_usuario.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
                image_bytes = base64.b64decode(encoded)

                response = gemini_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        mensaje_usuario
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        max_output_tokens=300
                    )
                )
            else:
                response = gemini_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=mensaje_usuario,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        max_output_tokens=250
                    )
                )

            logger.info("Respuesta procesada vía Gemini 1.5 Flash de respaldo.")
            return jsonify({"respuesta": response.text})
            
        except Exception as e_gemini:
            err_gemini_msg = str(e_gemini)
            logger.error(f"Error en Gemini: {err_gemini_msg}")
    else:
        err_gemini_msg = "Cliente Gemini no configurado o sin GEMINI_API_KEY."

    # Si ambos fallaron, mostramos el diagnostico real
    return jsonify({
        "respuesta": f"[DIAGNOSTICO DE ERROR]:\n- GROQ: {err_groq_msg}\n- GEMINI: {err_gemini_msg}"
    })

if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=5000, debug=False)
