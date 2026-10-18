import requests
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- SERVIDOR FALSO PARA MANTENER RENDER ACTIVO ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Binance Activo 24/7")

def run_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("🌐 Servidor interno iniciado en puerto 10000...")
    httpd.serve_forever()

# Iniciar servidor en hilo secundario
Thread(target=run_server, daemon=True).start()

# --- CONFIGURACIÓN DE TU BOT DE TRADING ---
TOKEN = "8721042176:AAGW4GcUn9N17jysRT9CG1E50jPaD3jMSk"
CHAT_ID = "1828560047"

print("🚀 Bot iniciado correctamente en la nube. Verificando Telegram...")

# --- PRUEBA DIRECTA CON DIAGNÓSTICO DE TELEGRAM ---
try:
    url_test = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🔔 ¡Prueba de diagnóstico: El bot está conectado con éxito!"}
    
    respuesta = requests.post(url_test, json=payload, timeout=10)
    
    print(f"📡 Código de respuesta de Telegram: {respuesta.status_code}")
    print(f"📄 Respuesta completa de Telegram: {respuesta.text}")
    
except Exception as e:
    print(f"❌ Error crítico al conectar con Telegram: {e}")

# Bucle simple para mantener el script corriendo
while True:
    print("⏳ Ciclo de espera activo... (El bot está en línea)")
    time.sleep(120)

