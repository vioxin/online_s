import websocket
import json
import threading
import time
import os
from keep_alive import keep_alive

# トークン取得
TOKEN = os.environ.get("DISCORD_TOKEN")

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def receive_json_response(ws):
    try:
        response = ws.recv()
        if response:
            return json.loads(response)
    except:
        return None

def heartbeat(interval, ws):
    print("心臓マッサージ開始！")
    while True:
        time.sleep(interval)
        try:
            send_json_request(ws, {"op": 1, "d": "null"})
            print("ドクン...（Discordに生存アピール完了）")
        except:
            print("心臓マッサージ失敗...ループを抜けます。")
            break

def connect_discord():
    while True:
        try:
            print("--- 制限回避のため30秒待機 ---")
            time.sleep(30)
            
            print("DiscordのGatewayに接続開始...")
            ws = websocket.WebSocket()
            ws.connect('wss://gateway.discord.gg/?v=9&encoding=json', timeout=10)
            
            event = receive_json_response(ws)
            if not event: continue

            interval = event['d']['heartbeat_interval'] / 1000
            t = threading.Thread(target=heartbeat, args=(interval, ws))
            t.daemon = True
            t.start()

            payload = {
                "op": 2,
                "d": {
                    "token": TOKEN,
                    "status": "online",
                    "properties": {
                        "$os": "windows",
                        "$browser": "chrome",
                        "$device": "pc"
                    }
                }
            }
            send_json_request(ws, payload)
            print("🔥 Discordに潜入成功！ログを見守れ！ 🔥")

            while True:
                if receive_json_response(ws) is None:
                    print("サーバーから通信が途絶えたぜ。")
                    break
        except Exception as e:
            print(f"接続エラー発生: {e}")

# --- ここからが超重要 ---

def main():
    if not TOKEN:
        print("⚠️ エラー: DISCORD_TOKENが設定されてないぞ！")
        return

    # 1. Webサーバーを起動
    keep_alive()
    
    # 2. Discord接続を別スレッドで開始（これでメイン処理が止まらない）
    threading.Thread(target=connect_discord, daemon=True).start()

    # 3. メインスレッドを「絶対に」終了させない
    # これがないとRenderが「アプリが終わった」と勘違いして終了させる
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main() # ← これが「実行ボタン」の役割！
