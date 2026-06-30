import requests

# Bura öz məlumatlarını yazırsan
TOKEN = "8884012328:AAEZiHEPUI5LpyXARCPUSQD-fq1_cIjTgM0"
CHAT_ID = "8570681347"

def get_rsi(symbol):
    try:
        # Binance API-dən son 100 şamın məlumatını götürürük
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
        response = requests.get(url).json()
        
        closes = [float(candle[4]) for candle in response]
        
        # RSI Hesablanması (14 dövrlük)
        gains = []
        losses = []
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
                
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    except Exception as e:
        print(f"Xəta baş verdi ({symbol}):", e)
        return None

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(telegram_url, json=payload)

def main():
    coins = {"BTCUSDT": "Bitcoin", "ETHUSDT": "Ethereum", "SOLUSDT": "Solana"}
    report_message = "🤖 *RSI Bot Canlı Hesabatı*\n\n"
    signals = []
    
    for symbol, name in coins.items():
        rsi = get_rsi(symbol)
        if rsi is not None:
            # Hesabata əlavə et
            report_message += f"📊 *{name} ({symbol.replace('USDT', '')})* -> RSI: `{rsi}`\n"
            
            # Siqnalları yoxla (Limitlər: 35 və 65)
            if rsi <= 35:
                signals.append(f"🟢 *{name}* üçün ALTI (BUY) fürsəti! RSI çox düşüb: `{rsi}`")
            elif rsi >= 65:
                signals.append(f"🔴 *{name}* üçün SATIŞ (SELL) fürsəti! RSI çox qalxıb: `{rsi}`")
        else:
            report_message += f"❌ *{name}* məlumatı alına bilmədi.\n"

    report_message += "\n"
    
    # Əgər əməliyyat siqnalı varsa, onları mesajın başına qoy
    if signals:
        final_message = "🚨 *TƏCİLİ SİQNAL VAR!*\n\n" + "\n".join(signals) + "\n\n" + report_message
    else:
        final_message = report_message + "😴 *Vəziyyət:* Hazırda güclü siqnal yoxdur, bazar ortadadır. Səbirlə gözləyirik."

    send_telegram_message(final_message)

if __name__ == "__main__":
    main()
    
