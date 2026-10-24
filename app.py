# ==============================================================================
# ULTRON WEB HUD v4.0.1 — CAPTURA DE VOZ ROBUSTA
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ULTRON // Web HUD v4.0</title>
    <style>
        :root {
            --bg-deep: #05070b;
            --panel-bg: rgba(10, 16, 26, 0.85);
            --neon-cyan: #00f0ff;
            --neon-red: #ff003c;
            --text-main: #c0d2e8;
            --border-glow: 0 0 10px rgba(0, 240, 255, 0.3);
        }
        body {
            background-color: var(--bg-deep);
            color: var(--text-main);
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 15px;
            display: flex;
            flex-direction: column;
            height: 92vh;
            box-sizing: border-box;
            background-image: 
                linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
            background-size: 20px 20px;
        }
        .header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--panel-bg);
            border: 1px solid var(--neon-cyan);
            box-shadow: var(--border-glow);
            padding: 12px 20px;
            margin-bottom: 15px;
        }
        .brand-area {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .reactor-core {
            width: 24px;
            height: 24px;
            border: 2px solid var(--neon-cyan);
            border-radius: 50%;
            position: relative;
            box-shadow: 0 0 8px var(--neon-cyan);
        }
        h1 {
            font-size: 1.1rem;
            margin: 0;
            letter-spacing: 3px;
            color: #ffffff;
            text-shadow: 0 0 5px var(--neon-cyan);
        }
        .main-layout {
            display: flex;
            gap: 15px;
            flex: 1;
            overflow: hidden;
        }
        .quick-panel {
            width: 220px;
            background: var(--panel-bg);
            border: 1px solid rgba(0, 240, 255, 0.4);
            border-radius: 4px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            overflow-y: auto;
        }
        .panel-title {
            font-size: 0.85rem;
            color: var(--neon-cyan);
            letter-spacing: 1.5px;
            margin-bottom: 5px;
            border-bottom: 1px solid rgba(0, 240, 255, 0.2);
            padding-bottom: 5px;
            font-weight: bold;
        }
        .btn-shortcut {
            background: rgba(0, 240, 255, 0.05);
            color: var(--text-main);
            border: 1px solid rgba(0, 240, 255, 0.2);
            padding: 10px;
            text-align: left;
            font-family: monospace;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            border-radius: 2px;
        }
        .btn-shortcut:hover {
            background: rgba(0, 240, 255, 0.2);
            color: #fff;
            border-color: var(--neon-cyan);
            box-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
        }
        #chat-container {
            flex: 1;
            background: var(--panel-bg);
            border: 1px solid rgba(0, 240, 255, 0.4);
            border-radius: 4px;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .mensaje {
            padding: 12px 16px;
            border-radius: 2px;
            max-width: 85%;
            line-height: 1.5;
            word-break: break-word;
            white-space: pre-wrap;
        }
        .usuario {
            background: rgba(0, 240, 255, 0.08);
            color: #8be9fd;
            align-self: flex-end;
            border-right: 3px solid var(--neon-cyan);
        }
        .ultron {
            background: rgba(255, 0, 60, 0.08);
            color: #ffb86c;
            align-self: flex-start;
            border-left: 3px solid var(--neon-red);
        }
        .input-area {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            align-items: center;
        }
        textarea {
            flex: 1;
            background: var(--panel-bg);
            border: 1px solid var(--neon-cyan);
            color: #ffffff;
            padding: 12px;
            font-family: monospace;
            font-size: 1rem;
            border-radius: 2px;
            resize: none;
            height: 24px;
        }
        button.action-btn {
            background: rgba(0, 240, 255, 0.1);
            color: var(--neon-cyan);
            border: 1px solid var(--neon-cyan);
            height: 48px;
            width: 48px;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        button.action-btn:hover {
            background: var(--neon-cyan);
            color: var(--bg-deep);
            box-shadow: 0 0 10px var(--neon-cyan);
        }
        button.recording {
            background: var(--neon-red) !important;
            color: #fff !important;
            border-color: var(--neon-red) !important;
            box-shadow: 0 0 15px var(--neon-red) !important;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        button.enviar {
            background: var(--neon-cyan);
            color: var(--bg-deep);
            border: none;
            padding: 0 25px;
            height: 48px;
            font-weight: bold;
            font-family: monospace;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header-bar">
        <div class="brand-area">
            <div class="reactor-core"></div>
            <h1>ULTRON WEB v4.0</h1>
        </div>
    </div>
    
    <div class="main-layout">
        <div class="quick-panel">
            <div class="panel-title">// CONSULTAS IA</div>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('Hola Ultron, preséntate.')">⚡ Saludo Inicial</button>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('Cuéntame un chiste técnico.')">🃏 Chiste Técnico</button>
            <button class="btn-shortcut" onclick="ejecutarComandoWeb('¿Qué hora es?')">🕒 Consultar Hora</button>
        </div>

        <div id="chat-container">
            <div class="mensaje ultron">HUD Web Público de Ultron v4.0 en línea. Presiona 🎤 para dictar por voz.</div>
        </div>
    </div>

    <div class="input-area">
        <button id="micBtn" class="action-btn" onclick="toggleVoz()" title="Hablar por micrófono">🎤</button>
        <textarea id="userInput" placeholder="Escribe tu mensaje o usa el micrófono..." autofocus onkeydown="if(event.key==='Enter'){event.preventDefault();enviarMensaje();}"></textarea>
        <button class="enviar" onclick="enviarMensaje()">ENVIAR</button>
    </div>

    <script>
        let recognition = null;
        let isRecording = false;

        function toggleVoz() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            
            if (!SpeechRecognition) {
                mostrarSistemaMsg("Este navegador no soporta reconocimiento de voz nativo. Prueba en Chrome, Edge o Safari.");
                return;
            }

            if (isRecording) {
                if (recognition) recognition.stop();
                stopRecording();
                return;
            }

            // Inicialización limpia directa
            recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = () => {
                isRecording = true;
                document.getElementById('micBtn').classList.add('recording');
                mostrarSistemaMsg("🎤 Escuchando... habla ahora.");
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('userInput').value = transcript;
                stopRecording();
                enviarMensaje();
            };

            recognition.onerror = (event) => {
                console.error("Error de voz:", event.error);
                stopRecording();
                if (event.error === 'not-allowed') {
                    mostrarSistemaMsg("Permiso bloqueado por el navegador. Toca el candado o ícono al lado de la URL para dar permiso explícito de micrófono a este sitio.");
                } else if (event.error === 'no-speech') {
                    mostrarSistemaMsg("No se escuchó ningún sonido. Inténtalo de nuevo.");
                } else {
                    mostrarSistemaMsg("Estado de voz: " + event.error);
                }
            };

            recognition.onend = () => {
                stopRecording();
            };

            try {
                recognition.start();
            } catch (e) {
                console.error(e);
                stopRecording();
            }
        }

        function stopRecording() {
            isRecording = false;
            document.getElementById('micBtn').classList.remove('recording');
        }

        function mostrarSistemaMsg(texto) {
            const container = document.getElementById('chat-container');
            container.innerHTML += `<div class="mensaje ultron" style="color: var(--neon-cyan);"><b>[SISTEMA]:</b> ${texto}</div>`;
            container.scrollTop = container.scrollHeight;
        }

        async function enviarMensaje() {
            const input = document.getElementById('userInput');
            const texto = input.value.trim();
            if (!texto) return;
            input.value = '';

            const container = document.getElementById('chat-container');
            container.innerHTML += `<div class="mensaje usuario"><b>Tú:</b>\n${escapeHtml(texto)}</div>`;
            container.scrollTop = container.scrollHeight;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'mensaje=' + encodeURIComponent(texto)
                });
                const data = await response.json();
                container.innerHTML += `<div class="mensaje ultron"><b>Ultron:</b>\n${escapeHtml(data.respuesta)}</div>`;
                container.scrollTop = container.scrollHeight;
            } catch (error) {
                container.innerHTML += `<div class="mensaje ultron" style="color: var(--neon-red);"><b>Error:</b> Sin conexión.</div>`;
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
                "Eres Ultron, un asistente cibernético de inteligencia artificial avanzado y conciso. "
                "Sé directo, breve y preciso. Responde en pocas oraciones (máximo 2 a 3 frases) salvo que el usuario pida explícitamente una explicación detallada."
            )

            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=mensaje_usuario,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        max_output_tokens=250
                    )
                )
                respuesta_texto = response.text
            except Exception as e_primary:
                logger.warning(f"Error en modelo primario gemini-2.5-flash: {e_primary}. Intentando con gemini-2.0-flash...")
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=mensaje_usuario,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        max_output_tokens=250
                    )
                )
                respuesta_texto = response.text

        except Exception as e:
            logger.error(f"Error al consultar la API de Gemini: {e}")
            respuesta_texto = "Sistemas parcialmente saturados. Ultron operando en respuesta de contingencia."
    else:
        respuesta_texto = f"Ultron Web procesó tu mensaje: '{mensaje_usuario}'. (Aviso: GEMINI_API_KEY no detectada)."

    return jsonify({"respuesta": respuesta_texto})

if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=5000, debug=False)
