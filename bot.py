import requests
import pandas as pd
import datetime
from ta.momentum import RSIIndicator

TELEGRAM_TOKEN = "8884012328:AAEZiHEPUI5LpyXARCPUSQD-fq1_cIjTgM0"  
CHAT_ID = "8570681347"                  

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram xətası:", e)

def run_analysis():
    coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    today_signals = []
    wait_signals = []
    
    for coin in coins:
        try:
            # GitHub Actions birbaşa Binance-ə qoşula bilir, limitsizdir
            url = f"https://api.binance.com/api/v3/klines?symbol={coin}&interval=1d&limit=50"
            res = requests.get(url, timeout=10)
            data = res.json()
            
            # Əgər data boş gələrsə xəta verməsin deyə yoxlama
            if not data or isinstance(data, dict):
                wait_signals.append(coin)
                continue
                
            df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'tbbav', 'tbqav', 'ignore'])
            df['close'] = df['close'].astype(float)
            
            rsi_series = RSIIndicator(close=df['close'], window=14).rsi()
            
            if rsi_series.empty or len(rsi_series) < 1:
                wait_signals.append(coin)
                continue
                
            rsi_value = rsi_series.iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if rsi_value < 35:
                stop_loss = round(current_price * 0.97, 2)
                take_profit = round(current_price * 1.07, 2)
                today_signals.append(f"🟢 {coin} - ALIŞ SİQNALI!\n🎯 Giriş: {current_price}\n🛑 Stop-Loss: {stop_loss}\n💰 Take-Profit: {take_profit}")
            elif rsi_value > 65:
                today_signals.append(f"🔴 {coin} - SATIŞ VAXTIDIR!\n🎯 Qiymət: {current_price}\n⚠️ Bazar aşırı şişib.")
            else:
                wait_signals.append(coin)
        except Exception as e:
            print(f"{coin} analizində xəta:", e)
            wait_signals.append(coin)

    final_message = f"📅 Analiz Tarixi: {datetime.date.today()}\n\n"
    if today_signals:
        final_message += "\n\n".join(today_signals)
    if wait_signals:
        final_message += f"⚪ {', '.join(wait_signals)} - UYĞUN ŞƏRAIT YOXDUR (GÖZLƏ)."
        
    send_telegram_message(final_message)

if __name__ == "__main__":
    run_analysis()
