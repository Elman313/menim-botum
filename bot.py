import datetime
import requests
import pandas as pd

# --- SİZİN TELEGRAM MƏLUMATLARINIZ ---
TELEGRAM_TOKEN = "8884012328:AAEZiHEPUI5LpyXARCPUSQD-fq1_cIjTgM0"
CHAT_ID = "8570681347"
# -------------------------------------

COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

def get_crypto_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&limit=50"
    try:
        response = requests.get(url).json()
        df = pd.DataFrame(response, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'q_av', 'trades', 't_b_b', 't_b_q', 'ignore'])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print(f"Məlumat xətası ({symbol}):", e)
        return None

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

def run_analysis():
    print("Analiz başladı...")
    today_signals = []
    wait_signals = []

    for coin in COINS:
        df = get_crypto_data(coin)
        if df is None: continue
        
        df = calculate_rsi(df)
        last_row = df.iloc[-1]
        current_price = last_row['close']
        rsi_value = last_row['RSI']
        
        if rsi_value < 35:  # Alış şərti
            stop_loss = round(current_price * 0.97, 2)
            take_profit = round(current_price * 1.07, 2)
            today_signals.append(f"🟢 {coin} - ALIŞ SİQNALI!\n🎯 Giriş: {current_price}\n🛑 Stop-Loss: {stop_loss}\n💰 Take-Profit: {take_profit}")
        elif rsi_value > 65:  # Satış şərti
            today_signals.append(f"🔴 {coin} - SATIŞ VAXTIDIR!\n🎯 Qiymət: {current_price}\n⚠️ Bazar aşırı şişib.")
        else:
            wait_signals.append(coin)

    final_message = f"📅 Analiz Tarixi: {datetime.date.today().strftime('%d.%m.%Y')}\n\n"
    if today_signals:
        final_message += "\n\n".join(today_signals)
    if wait_signals:
        final_message += f"⚪ {', '.join(wait_signals)} üçün bu gün uyğun şərait yoxdur. GÖZLƏ."

    send_telegram_message(final_message)
    print("Mesaj Telegram-a göndərildi!")
if __name__ == "__main__":
    run_analysis()
    run_analysis()
