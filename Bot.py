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

TOKENS = ["DODOUSDT", "SAGAUSDT", "EULUSDT", "TUTUSDT"]

MIN_VOLUMEN_USDT = 100.0  
DISTANCIA_MIN_PCT = 0.2
DISTANCIA_MAX_PCT = 3.5

print("🚀 Bot iniciado correctamente en la nube. Monitoreando Binance 24/7...")

# --- PRUEBA INMEDIATA DE TELEGRAM ---
requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🔔 ¡Bot encendido y conectado con éxito!"})

# --- BUCLE INFINITO PARA ANALIZAR CADA 2 MINUTOS ---
while True:
    try:
        mejor_oportunidad = None

        for symbol in TOKENS:
            try:
                url_ticker = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                url_depth = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=100"

                r_ticker = requests.get(url_ticker, timeout=10)
                precio_actual = float(r_ticker.json()['price'])
                
                r_depth = requests.get(url_depth, timeout=10)
                depth = r_depth.json()

                muros_detectados = []

                for price_str, qty_str in depth['bids']:
                    p = float(price_str)
                    q = float(qty_str)
                    vol_usdt = p * q
                    distancia_pct = ((precio_actual - p) / precio_actual) * 100

                    if vol_usdt >= MIN_VOLUMEN_USDT and DISTANCIA_MIN_PCT <= distancia_pct <= DISTANCIA_MAX_PCT:
                        muros_detectados.append({
                            "precio": p,
                            "volumen": vol_usdt,
                            "distancia": distancia_pct
                        })

                if muros_detectados:
                    muros_detectados.sort(key=lambda x: x['volumen'], reverse=True)
                    mejor_muro = muros_detectados[0]
                    
                    candidato = {
                        "simbolo": symbol,
                        "precio_actual": precio_actual,
                        "soporte": mejor_muro['precio'],
                        "volumen": mejor_muro['volumen'],
                        "distancia": mejor_muro['distancia']
                    }
                    
                    if not mejor_oportunidad or candidato['volumen'] > mejor_oportunidad['volumen']:
                        mejor_oportunidad = candidato

            except Exception as e:
                print(f"⚠️ Error consultando {symbol}: {e}")

        if mejor_oportunidad:
            sym = mejor_oportunidad['simbolo']
            precio_actual = mejor_oportunidad['precio_actual']
            soporte = mejor_oportunidad['soporte']
            volumen = mejor_oportunidad['volumen']
            distancia = mejor_oportunidad['distancia']

            take_profit = round(soporte * 1.008, 4)
            piso_1 = round(soporte * 0.985, 4)
            piso_2 = round(soporte * 0.965, 4)

            mensaje = (
                f"🎯 ¡MEJOR OPORTUNIDAD DEL MOMENTO!\n\n"
                f"📌 Par: {sym}\n"
                f"💵 Precio Actual: ${precio_actual}\n\n"
                f"🧱 Muro Fuerte: ${soporte}\n"
                f"💰 Volumen en Muro: ${round(volumen, 2):,} USDT\n"
                f"📏 Distancia: -{round(distancia, 2)}%\n\n"
                f"🎯 Take Profit (+0.8%): ${take_profit}\n"
                f"📉 Pisos DCA Sugeridos:\n"
                f"• Piso 1 (-1.5%): ${piso_1}\n"
                f"• Piso 2 (-3.5%): ${piso_2}"
            )

            url_tg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url_tg, json={"chat_id": CHAT_ID, "text": mensaje}, timeout=10)
            print(f"✅ ¡Alerta enviada a Telegram! Ganador: {sym}")
        else:
            print("⏳ Ningún token cumple el filtro en este ciclo.")

    except Exception as e:
        print(f"❌ Error en el bucle principal: {e}")

    # Esperar 2 minutos (120 segundos) antes de volver a revisar
    time.sleep(120)
