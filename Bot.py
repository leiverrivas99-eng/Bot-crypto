import requests
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- SERVIDOR PARA MANTENER RENDER ACTIVO 24/7 ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Binance Spot & Futuros Activo 24/7")

def run_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("🌐 Servidor interno iniciado en puerto 10000...")
    httpd.serve_forever()

Thread(target=run_server, daemon=True).start()

# --- CONFIGURACIÓN DE TELEGRAM ---
TOKEN = "8721042176:AAGW4GcUn9mN17jysrT9CGlE50jPaD3jMSk"
CHAT_ID = "1828560047"

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Error enviando mensaje a Telegram: {e}")
        return False

# --- OBTENER DATOS SPOT Y FUTUROS ---
def obtener_libro_spot(simbolo):
    try:
        url = f"https://api.binance.com/api/v3/depth?symbol={simbolo}&limit=10"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def obtener_libro_futuros(simbolo):
    try:
        url = f"https://fapi.binance.com/fapi/v1/depth?symbol={simbolo}&limit=10"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def sumar_volumen_usdt(lista_ordenes):
    total = 0.0
    for precio, cantidad in lista_ordenes:
        total += float(precio) * float(cantidad)
    return total

# Criptomonedas a monitorear
SIMBOLOS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", 
    "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", 
    "LINKUSDT", "NEARUSDT", "SUIUSDT", "PEPEUSDT"
]

# Umbral de filtro por orden individual ($5,000 USDT)
UMBRAL_MURO_USDT = 5000 

alertas_enviadas = {}

print("🚀 Bot Spot + Futuros iniciando en la nube...")

# --- MENSAJE DE PRUEBA ---
mensaje_prueba = "⚡ *BOT ACTUALIZADO: SPOT Y FUTUROS*\n\n🎯 Vigilando libros de ordenes en Spot y Perpetuos para detectar presion de compra/venta."
enviar_telegram(mensaje_prueba)

# --- BUCLE DE RASTREO ---
while True:
    try:
        for simbolo in SIMBOLOS:
            spot_data = obtener_libro_spot(simbolo)
            futuros_data = obtener_libro_futuros(simbolo)
            
            if not spot_data or not futuros_data:
                continue

            # Evaluar compras (Bids) y ventas (Asks) en Spot
            bids_spot_total = sumar_volumen_usdt(spot_data.get("bids", []))
            asks_spot_total = sumar_volumen_usdt(spot_data.get("asks", []))

            # Evaluar compras (Bids) y ventas (Asks) en Futuros
            bids_fut_total = sumar_volumen_usdt(futuros_data.get("bids", []))
            asks_fut_total = sumar_volumen_usdt(futuros_data.get("asks", []))

            # Buscar muros individuales de soporte en Spot (Bids)
            for precio_str, cantidad_str in spot_data.get("bids", [])[:5]:
                precio = float(precio_str)
                total_usdt = precio * float(cantidad_str)
                
                if total_usdt >= UMBRAL_MURO_USDT:
                    clave_alerta = f"{simbolo}_{precio_str}"
                    tiempo_actual = time.time()
                    
                    if clave_alerta not in alertas_enviadas or (tiempo_actual - alertas_enviadas[clave_alerta]) > 900:
                        alertas_enviadas[clave_alerta] = tiempo_actual
                        
                        # Determinar tendencia por presion general de libros
                        presion_spot = "🟢 COMPRA" if bids_spot_total > asks_spot_total else "🔴 VENTA"
                        presion_fut = "🟢 COMPRA" if bids_fut_total > asks_fut_total else "🔴 VENTA"

                        msg = (
                            f"📊 *ANÁLISIS DE MERCADO: {simbolo}*\n\n"
                            f"🧱 *Muro Spot Detectado:* `{precio:,.4f} USDT` (`${total_usdt:,.2f} USDT`)\n\n"
                            f"📈 *Presión en Libros (Top 10):*\n"
                            f"🔹 *Spot:* {presion_spot} (Bids: `${bids_spot_total:,.0f}` | Asks: `${asks_spot_total:,.0f}`)\n"
                            f"🔹 *Futuros:* {presion_fut} (Bids: `${bids_fut_total:,.0f}` | Asks: `${asks_fut_total:,.0f}`)\n\n"
                            f"💡 _Si ambos mercados muestran presión de COMPRA, aumenta la probabilidad de subida del 1%._"
                        )
                        print(f"🔔 Alerta enviada para {simbolo}")
                        enviar_telegram(msg)
                        
        time.sleep(30)

    except Exception as e:
        print(f"⚠️ Error en el ciclo: {e}")
        time.sleep(10)
