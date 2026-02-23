import websocket
import json
import threading
import time
import os
from keep_alive import keep_alive

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
    print("心臓マッサージ（ハートビート）開始！")
    while True:
        time.sleep(interval)
        heartbeatJSON = {"op": 1, "d": "null"}
        try:
            send_json_request(ws, heartbeatJSON)
            print("ドクン...（Discordに生存アピール完了）")
        except:
            print("心臓マッサージ失敗...ループを抜けます。")
            break

def main():
    if not TOKEN:
        print("⚠️ エラー: DISCORD_TOKENが設定されてないぞ！")
        return

    keep_alive()

    while True:
        try:
            print("--- 次の接続まで30秒待機します（制限回避のため） ---")
            time.sleep(30) # 接続の試行自体に余裕を持たせる

            print("DiscordのGatewayに接続開始...")
            ws = websocket.WebSocket()
            ws.connect('wss://gateway.discord.gg/?v=9&encoding=json', timeout=10)
            
            event = receive_json_response(ws)
            if not event: continue

            heartbeat_interval = event['d']['heartbeat_interval'] / 1000
            t = threading.Thread(target=heartbeat, args=(heartbeat_interval, ws))
            t.daemon = True # スレッドが残らないようにする
            t.start()

            payload = {
                "op": 2,
                "d": {
                    "token": TOKEN,
                    "status": "online", # 明示的にオンラインを指定
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
                event = receive_json_response(ws)
                if event is None:
                    print("サーバーから通信が途絶えたぜ。")
                    break
        
        except Exception as e:
            print(f"接続エラー発生: {e}")

if __name__ == "__main__":
    main() # ← これが「実行ボタン」の役割！
