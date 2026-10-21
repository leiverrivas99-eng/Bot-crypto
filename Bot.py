import os
import time
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Servidor web invisible para Render (Mantiene el servicio gratuito activo 24/7)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot SUI Activo")
    def log_message(self, format, *args):
        return

def start_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Credenciales y Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "AAGW4GcUn9m17jysrT9CG1E50jPaD3jMSK")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8721042176")

SYMBOL = "SUIUSDT"
MIN_WALL_SUI = 170000   # El muro de 170k tokens que buscas
TAKE_PROFIT_PCT = 0.8   # 0.8% de ganancia
CHECK_INTERVAL = 15     # Revisión cada 15 segundos

last_alert_price = 0    

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=8)
    except Exception as e:
        print(f"Error Telegram: {e}")

def monitor():
    global last_alert_price
    print("Iniciando escáner de muros SUI...")
    send_telegram_message("🟢 *BOT SUI INICIADO*\nEscaneando libros en busca de muros >= 170,000 SUI.")

    while True:
        try:
            # Consultar libro de Spot en Binance
            url = f"https://api.binance.com/api/v3/depth?symbol={SYMBOL}&limit=20"
            res = requests.get(url, timeout=5).json()
            
            bids = res.get("bids", []) # Órdenes de compra (Muros abajo)
            
            if bids:
                best_price = float(bids[0][0])
                
                # Revisar cada nivel del libro de órdenes
                for price_str, qty_str in bids:
                    price = float(price_str)
                    qty = float(qty_str)
                    
                    # Si encontramos un muro que supere los 170k SUI
                    if qty >= MIN_WALL_SUI:
                        # Evitar repetir la alerta si es casi el mismo precio
                        if abs(price - last_alert_price) > 0.002:
                            tp_price = price * (1 + (TAKE_PROFIT_PCT / 100))
                            
                            mensaje = (
                                f"🔥 *¡MURO DE LIQUIDEZ DETECTADO!* 🔥\n\n"
                                f"🪙 *Token:* SUI / USDT\n"
                                f"🧱 *Tamaño del Muro:* `{qty:,.0f} SUI`\n"
                                f"📍 *Precio del Muro (Zona de Compra):* `{price:.4f}`\n"
                                f"💲 *Precio Actual:* `{best_price:.4f}`\n"
                                f"🎯 *Take Profit (+0.8%):* `{tp_price:.4f}`\n\n"
                                f"⚡ *¡Atentos a la reacción del precio en este nivel!*"
                            )
                            send_telegram_message(mensaje)
                            last_alert_price = price
                            break
        except Exception as e:
            print(f"Error en bucle: {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    threading.Thread(target=start_dummy_server, daemon=True).start()
    monitor()
