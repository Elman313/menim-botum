import requests

# Bura öz şəxsi Telegram bot məlumatlarını yazırsan
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
        print(f"Xəta baş verdi ({symbol} RSI):", e)
        return None

def get_live_price(symbol):
    try:
        # Binance-dən coin-in canlı qiymətini götürürük
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url).json()
        return float(response['price'])
    except Exception as e:
        print(f"Xəta baş verdi ({symbol} Qiymət):", e)
        return None

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload)
    except Exception as e:
        print("Telegram mesajı göndərilərkən xəta:", e)

def main():
    # Yoxlamaq istədiyimiz coinlər
    coins = {"BTCUSDT": "Bitcoin", "ETHUSDT": "Ethereum", "SOLUSDT": "Solana"}
    signals = []
    
    for symbol, name in coins.items():
        rsi = get_rsi(symbol)
        price = get_live_price(symbol)
        
        if rsi is not None and price is not None:
            clean_symbol = symbol.replace('USDT', '')
            
            # 🟢 ALIŞ (BUY) FÜRSƏTİ (RSI 35 və daha aşağı düşəndə)
            if rsi <= 40:
                sl = round(price * 0.98, 4 if price < 10 else 2)  # 2% aşağı stop loss
                tp = round(price * 1.04, 4 if price < 10 else 2)  # 4% yuxarı take profit
                
                msg = (
                    f"🟢 *{name} ({clean_symbol}) ALTI (BUY) FÜRSƏTİ!*\n"
                    f"📈 RSI səviyyəsi: `{rsi}`\n"
                    f"💵 *Giriş Qiyməti (Entry):* `{price} USDT`\n"
                    f"🛑 *Stop Loss (SL):* `{sl} USDT`\n"
                    f"🎯 *Take Profit (TP):* `{tp} USDT`"
                )
                signals.append(msg)
                
            # 🔴 SATIŞ (SELL / SHORT) FÜRSƏTİ (RSI 65 və daha yuxarı qalxanda)
            elif rsi >= 65:
                sl = round(price * 1.02, 4 if price < 10 else 2)  # 2% yuxarı stop loss (Futures üçün)
                tp = round(price * 0.96, 4 if price < 10 else 2)  # 4% aşağı take profit (Futures üçün)
                
                msg = (
                    f"🔴 *{name} ({clean_symbol}) SATIŞ (SELL) FÜRSƏTİ!*\n"
                    f"📉 RSI səviyyəsi: `{rsi}`\n"
                    f"💵 *Giriş Qiyməti (Entry):* `{price} USDT`\n"
                    f"🛑 *Stop Loss (SL):* `{sl} USDT`\n"
                    f"🎯 *Take Profit (TP):* `{tp} USDT`"
                )
                signals.append(msg)

    # Əgər hər hansı bir coində əməliyyat yeri varsa, Telegram-a göndər
    if signals:
        final_message = "🚨 *YENİ ƏMƏLİYYAT FÜRSƏTİ TAPILDI!*\n\n" + "\n\n---\n\n".join(signals)
        send_telegram_message(final_message)
    else:
        # Əgər yaxşı fürsət yoxdursa, bot tamamilə səssiz qalır
        print("Yaxşı əməliyyat yeri yoxdur, monitorinq davam edir.")

if __name__ == "__main__":
    main()
