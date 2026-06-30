import requests

# Sənin düzgün məlumatların birbaşa bura quraşdırıldı
TOKEN = "8884012328:AAEZiHEPUI5LpyXARCPUSQD-fq1_cIjTgM0"
CHAT_ID = "8570681347"  # Bot bu ID-yə mesaj göndərəcək

def get_rsi(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
        response = requests.get(url).json()
        closes = [float(candle[4]) for candle in response]
        
        gains, losses = [], []
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
    except:
        return None

def get_live_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url).json()
        return float(response['price'])
    except:
        return None

def main():
    coins = {"BTCUSDT": "Bitcoin", "ETHUSDT": "Ethereum", "SOLUSDT": "Solana"}
    signals = []
    
    for symbol, name in coins.items():
        rsi = get_rsi(symbol)
        price = get_live_price(symbol)
        
        if rsi is not None and price is not None:
            clean_symbol = symbol.replace('USDT', '')
            
            # Real işlək limitlər (Səhər danışdığımız kimi)
            if rsi <= 35:
                sl = round(price * 0.98, 2)
                tp = round(price * 1.04, 2)
                msg = f"🟢 *{name} ({clean_symbol}) ALTI FÜRSƏTİ!*\n📈 RSI: `{rsi}`\n💵 Qiymət: `{price} USDT`"
                signals.append(msg)
            elif rsi >= 65:
                sl = round(price * 1.02, 2)
                tp = round(price * 0.96, 2)
                msg = f"🔴 *{name} ({clean_symbol}) SATIŞ FÜRSƏTİ!*\n📉 RSI: `{rsi}`\n💵 Qiymət: `{price} USDT`"
                signals.append(msg)

    # Əgər limitlər ödənməsə belə, botun işlədiyini sübut etmək üçün HƏMİŞƏ bura mesaj atacaq!
    if not signals:
        test_msg = "🤖 *Bot uğurla işlədi!*\n\nBax bura, hazırda limitlər (35 vəya 65) ödənmədiyi üçün sakit rejimdəyəm. Amma sistem saat kimi aktivdir!"
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(telegram_url, json={"chat_id": CHAT_ID, "text": test_msg, "parse_mode": "Markdown"})
    else:
        final_message = "🚨 *YENİ SİGNAL TAPILDI!*\n\n" + "\n\n---\n\n".join(signals)
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(telegram_url, json={"chat_id": CHAT_ID, "text": final_message, "parse_mode": "Markdown"})

if __name__ == "__main__":
    main()
