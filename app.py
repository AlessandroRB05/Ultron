# ==============================================================================
# ULTRON WEB HUD v4.0.0 — ADVANCED SCI-FI HUD INTERFACE
# ==============================================================================

import os
import sys
import logging
from flask import Flask, render_template_string, request, jsonify

from google import genai
from google.genai import types

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("UltronWebHUD")

app_flask = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        logger.info("Cliente de Google GenAI inicializado correctamente.")
    except Exception as e:
        logger.error(f"Error al inicializar el cliente de GenAI: {e}")
else:
    logger.warning("GEMINI_API_KEY no encontrada en las variables de entorno.")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ULTRON // ADVANCED HUD SYSTEM</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

        :root {
            --bg-deep: #02060d;
            --panel-bg: rgba(6, 15, 28, 0.75);
            --neon-cyan: #00f3ff;
            --neon-red: #ff0055;
            --neon-amber: #ffaa00;
            --glass-border: rgba(0, 243, 255, 0.4);
            --text-glow: 0 0 8px rgba(0, 243, 255, 0.8);
            --red-glow: 0 0 12px rgba(255, 0, 85, 0.8);
        }

        * {
            box-sizing: border-box;
            user-select: none;
        }

        body {
            background-color: var(--bg-deep);
            color: #d1f7ff;
            font-family: 'Share Tech Mono', monospace;
            margin: 0;
            padding: 12px;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(0, 243, 255, 0.05) 0%, transparent 80%),
                linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 30px 30px, 30px 30px;
        }

        /* EFECTO SCANLINE CRT FUTURISTA */
        body::before {
            content: " ";
            display: block;
            position: absolute;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
            background-size: 100% 4px;
            z-index: 1000;
            pointer-events: none;
            opacity: 0.6;
        }

        /* HEADER / BARRA DE NAVEGACIÓN FUTURISTA */
        .header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--panel-bg);
            border: 1px solid var(--glass-border);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2), inset 0 0 15px rgba(0, 243, 255, 0.1);
            backdrop-filter: blur(8px);
            padding: 10px 20px;
            margin-bottom: 12px;
            clip-path: polygon(0 0, 100% 0, 98% 100%, 2% 100%);
        }

        .brand-area {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .reactor-core {
            width: 22px;
            height: 22px;
            border: 2px solid var(--neon-cyan);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--neon-cyan), inset 0 0 8px var(--neon-cyan);
            animation: pulse-core 1.5s infinite alternate ease-in-out;
            position: relative;
        }

        .reactor-core::after {
            content: '';
            position: absolute;
            top: 3px; left: 3px; right: 3px; bottom: 3px;
            background: var(--neon-cyan);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--neon-cyan);
        }

        @keyframes pulse-core {
            0% { transform: scale(0.85); box-shadow: 0 0 6px var(--neon-cyan); }
            100% { transform: scale(1.15); box-shadow: 0 0 18px var(--neon-cyan), 0 0 30px var(--neon-cyan); }
        }

        h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem;
            font-weight: 900;
            margin: 0;
            letter-spacing: 4px;
            color: #ffffff;
            text-shadow: var(--text-glow);
        }

        .hud-metrics {
            display: flex;
            gap: 15px;
            font-size: 0.75rem;
            color: var(--neon-cyan);
            letter-spacing: 1px;
        }

        .hud-metrics span {
            background: rgba(0, 243, 255, 0.1);
            border: 1px solid rgba(0, 243, 255, 0.3);
            padding: 3px 8px;
            clip-path: polygon(10% 0, 100% 0, 90% 100%, 0 100%);
        }

        /* LAYOUT PRINCIPAL */
        .main-layout {
            display: flex;
            gap: 12px;
            flex: 1;
            overflow: hidden;
        }

        /* PANEL LATERAL DE CONTROL */
        .quick-panel {
            width: 230px;
            background: var(--panel-bg);
            border: 1px solid var(--glass-border);
            box-shadow: inset 0 0 12px rgba(0, 243, 255, 0.1);
            backdrop-filter: blur(8px);
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            overflow-y: auto;
            clip-path: polygon(0 0, 100% 0, 100% 96%, 88% 100%, 0 100%);
        }

        .panel-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
            color: var(--neon-cyan);
            letter-spacing: 2px;
            margin-bottom: 8px;
            border-bottom: 1px solid var(--glass-border);
            padding-bottom: 5px;
            text-shadow: var(--text-glow);
        }

        .btn-shortcut {
            background: rgba(0, 243, 255, 0.05);
            color: #d1f7ff;
            border: 1px solid rgba(0, 243, 255, 0.3);
            padding: 12px;
            text-align: left;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.25s ease;
            clip-path: polygon(8% 0, 100% 0, 100% 70%, 92% 100%, 0 100%, 0 30%);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-shortcut:hover {
            background: rgba(0, 243, 255, 0.25);
            color: #ffffff;
            border-color: var(--neon-cyan);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.5);
            transform: translateX(4px);
        }

        /* ÁREA DE CHAT TERMINAL */
        #chat-container {
            flex: 1;
            background: var(--panel-bg);
            border: 1px solid var(--glass-border);
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.9), 0 0 15px rgba(0, 243, 255, 0.1);
            backdrop-filter: blur(8px);
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            position: relative;
        }

        .mensaje {
            padding: 12px 18px;
            max-width: 80%;
            line-height: 1.5;
            word-break: break-word;
            white-space: pre-wrap;
            font-size: 0.95rem;
            position: relative;
            animation: slideIn 0.3s cubic-bezier(0.1, 0.9, 0.2, 1);
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .usuario {
            background: rgba(0, 243, 255, 0.08);
            color: #a8f5ff;
            align-self: flex-end;
            border: 1px solid rgba(0, 243, 255, 0.4);
            border-right: 4px solid var(--neon-cyan);
            clip-path: polygon(3% 0, 100% 0, 100% 100%, 0 100%, 0 25%);
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.15);
        }

        .ultron {
            background: rgba(255, 0, 85, 0.08);
            color: #ffb5c8;
            align-self: flex-start;
            border: 1px solid rgba(255, 0, 85, 0.4);
            border-left: 4px solid var(--neon-red);
            clip-path: polygon(0 0, 97% 0, 100% 25%, 100% 100%, 0 100%);
            box-shadow: var(--red-glow);
        }

        /* ENTRADA DE MENSAJES */
        .input-area {
            display: flex;
            gap: 10px;
            margin-top: 12px;
            align-items: center;
        }

        textarea {
            flex: 1;
            background: var(--panel-bg);
            border: 1px solid var(--glass-border);
            color: #ffffff;
            padding: 14px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 1rem;
            resize: none;
            height: 52px;
            outline: none;
            box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.1);
            clip-path: polygon(0 0, 98% 0, 100% 30%, 100% 100%, 2% 100%, 0 70%);
            transition: all 0.3s;
        }

        textarea:focus {
            border-color: var(--neon-cyan);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.4), inset 0 0 10px rgba(0, 243, 255, 0.2);
        }

        button.enviar {
            background: var(--neon-cyan);
            color: var(--bg-deep);
            border: none;
            padding: 0 28px;
            height: 52px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 0.9rem;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all 0.3s ease;
            clip-path: polygon(15% 0, 100% 0, 100% 70%, 85% 100%, 0 100%, 0 30%);
            box-shadow: 0 0 15px var(--neon-cyan);
        }

        button.enviar:hover, button.enviar:active {
            background: #ffffff;
            box-shadow: 0 0 25px var(--neon-cyan);
            transform: scale(1.02);
        }

        /* RESPONSIVO PARA CELULARES */
        @media (max-width: 768px) {
            body { padding: 6px; }
            .header-bar { clip-path: none; padding: 8px 12px; }
            .hud-metrics { display: none; }
            .main-layout { flex-direction: column; }
            .quick-panel {
                width: 100%;
                max-height: 60px;
                flex-direction: row;
                overflow-x: auto;
                padding: 6px;
                clip-path: none;
            }
            .panel-title { display: none; }
            .btn-shortcut { white-space: nowrap; padding: 8px 12px; font-size: 0.75rem; }
            .mensaje { max-width: 92%; font-size: 0.88rem; }
            button.enviar { padding: 0 16px; font-size: 0.8rem; }
        }
    </style>
</head>
<body>
    <div class="header-bar">
        <div class="brand-area">
            <div class="reactor-core"></div>
            <h1>ULTRON // HUD v4.0</h1>
        </div>
        <div class="hud-metrics">
            <span>CORE: ONLINE</span>
            <span>AI: GEMINI-FLASH</span>
            <span>NET: SECURE</span>
        </div>
    </div>
    
    <div class="main-layout">
        <div class="quick-panel">
            <div class="panel-title">// COMANDOS</div>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('Hola Ultron, preséntate brevemente.')">⚡ SALUDO</button>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('Cuéntame un chiste técnico corto.')">🃏 CHISTE</button>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('¿Cuál es tu estado de procesamiento?')">📊 DIAGNÓSTICO</button>
        </div>

        <div id="chat-container">
            <div class="mensaje ultron"><b>ULTRON:</b>\nSistemas neuronales acoplados. HUD de combate activo. ¿Cuáles son tus órdenes?</div>
        </div>
    </div>

    <div class="input-area">
        <textarea id="userInput" placeholder="Ingresa comando de voz o texto..." autofocus onkeydown="if(event.key==='Enter' && !event.shiftKey){event.preventDefault();enviarMensaje();}"></textarea>
        <button class="enviar" onclick="enviarMensaje()">TRANSMITIR</button>
    </div>

    <script>
        async function enviarMensaje() {
            const input = document.getElementById('userInput');
            const texto = input.value.trim();
            if (!texto) return;
            input.value = '';

            const container = document.getElementById('chat-container');
            container.innerHTML += `<div class="mensaje usuario"><b>TÚ:</b>\n${escapeHtml(texto)}</div>`;
            container.scrollTop = container.scrollHeight;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'mensaje=' + encodeURIComponent(texto)
                });
                const data = await response.json();
                container.innerHTML += `<div class="mensaje ultron"><b>ULTRON:</b>\n${escapeHtml(data.respuesta)}</div>`;
                container.scrollTop = container.scrollHeight;
            } catch (error) {
                container.innerHTML += `<div class="mensaje ultron" style="color: var(--neon-red);"><b>ERROR:</b> Fallo en enlace cuántico con servidor.</div>`;
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

@app_flask.route("/")
def index_web():
    return render_template_string(HTML_TEMPLATE)

@app_flask.route("/api/chat", methods=["POST"])
def chat_web():
    mensaje_usuario = request.form.get("mensaje", "Hola")
    
    if client:
        try:
            system_instruction = (
                "Eres Ultron, un asistente cibernético de inteligencia artificial avanzado, imponente y muy conciso. "
                "Responde con tono profesional, tecnológico e imponente. Mantén tus respuestas breves y directas (máximo 2 a 3 frases)."
            )

            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=mensaje_usuario,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    max_output_tokens=300
                )
            )
            respuesta_texto = response.text

        except Exception as e:
            logger.error(f"Error al consultar la API de Gemini: {e}")
            respuesta_texto = f"Error en la red neuronal: {str(e)}"
    else:
        respuesta_texto = f"Ultron Web procesó tu mensaje: '{mensaje_usuario}'. (Aviso: GEMINI_API_KEY no detectada)."

    return jsonify({"respuesta": respuesta_texto})

if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=5000, debug=False)
