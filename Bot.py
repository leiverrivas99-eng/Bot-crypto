import requests
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- SERVIDOR FALSO PARA MANTENER RENDER ACTIVO ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Binance Volatilidad y Muros Activo 24/7")

def run_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("🌐 Servidor interno iniciado en puerto 10000...")
    httpd.serve_forever()

Thread(target=run_server, daemon=True).start()

# --- CONFIGURACIÓN DE TELEGRAM ---
TOKEN = "8721042176:AAGW4GcUn9N17jysrT9CGlE50jPaD3jMSk"
CHAT_ID = "1828560047"

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Error enviando mensaje a Telegram: {e}")

# --- ENLACES DE BINANCE (ENDPOINTS DE RESPALDO) ---
ENDPOINTS_BINANCE = [
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com"
]

def obtener_datos(path, params=None):
    for base_url in ENDPOINTS_BINANCE:
        try:
            url = base_url + path
            r = requests.get(url, params=params, timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            continue
    return None

# Criptomonedas a monitorear (puedes agregar más pares USDT)
SIMBOLOS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", 
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", 
    "LINKUSDT", "NEARUSDT", "SUIUSDT", "PEPEUSDT"
]

# Umbral en USDT para considerar una "pared de compra" (muro de soporte)
UMBRAL_MURO_USDT = 50000  # $50,000 USDT en un solo nivel de precio

# Registro para evitar enviar alertas repetidas seguidas del mismo precio
alertas_enviadas = {}

print("🚀 Bot de detección de Muros de Soporte iniciado correctamente...")
enviar_telegram("🤖 *Bot de Trading Iniciado*\n\nVigilando libros de órdenes de Binance 24/7 en busca de muros de soporte ($50k+ USDT).")

while True:
    try:
        for simbolo in SIMBOLOS:
            # Obtener el libro de órdenes (Order Book - Bids/Asks)
            depth = obtener_datos("/api/v3/depth", params={"symbol": simbolo, "limit": 20})
            if not depth or "bids" not in depth:
                continue
            
            # Analizar las ofertas de compra (bids = soportes/muros)
            bids = depth["bids"]
            for precio_str, cantidad_str in bids[:10]:  # Evaluar los 10 mejores niveles
                precio = float(precio_str)
                cantidad = float(cantidad_str)
                total_usdt = precio * cantidad
                
                if total_usdt >= UMBRAL_MURO_USDT:
                    clave_alerta = f"{simbolo}_{precio_str}"
                    tiempo_actual = time.time()
                    
                    # Notificar solo si no hemos enviado esta misma alerta en los últimos 15 minutos (900 seg)
                    if clave_alerta not in alertas_enviadas or (tiempo_actual - alertas_enviadas[clave_alerta]) > 900:
                        alertas_enviadas[clave_alerta] = tiempo_actual
                        
                        msg = (
                            f"🧱 *¡MURO DE SOPORTE DETECTADO!*\n\n"
                            f"📌 *Par:* `{simbolo}`\n"
                            f"💵 *Precio:* `{precio:,.4f} USDT`\n"
                            f"📊 *Volumen del Muro:* `{total_usdt:,.2f} USDT` (`{cantidad:,.2f}` monedas)\n\n"
                            f"⚡ _Posible zona de rebotador / fuerte demanda._"
                        )
                        print(f"🔔 Muro detectado en {simbolo} @ {precio}: {total_usdt} USDT")
                        enviar_telegram(msg)
                        
        time.sleep(30)  # Revisa el mercado cada 30 segundos

    except Exception as e:
        print(f"⚠️ Error durante el ciclo de escaneo: {e}")
        time.sleep(10)


