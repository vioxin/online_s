import websocket
import json
import threading
import time
import os
from keep_alive import keep_alive

# 【超重要】トークンはコードに直書きせず、Renderの「環境変数」から読み込む！
# 万が一GitHubがバレてもトークンが漏れないための絶対の防衛線だ。
TOKEN = os.environ.get("DISCORD_TOKEN")

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def receive_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)

def heartbeat(interval, ws):
    print("心臓マッサージ（ハートビート）開始！")
    while True:
        # Discordから指定された間隔（ミリ秒を秒に直す）で生存報告を送る
        time.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": "null"
        }
        send_json_request(ws, heartbeatJSON)
        print("ドクン...（Discordに生存アピール完了）")

def main():
    if not TOKEN:
        print("⚠️ エラー: Renderの環境変数に『DISCORD_TOKEN』が設定されてないぞ！")
        return

    # GAS受け止め用のWebサーバーを裏で起動！
    keep_alive()

    # DiscordのGateway（通信の入り口）に接続！
    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')
    event = receive_json_response(ws)

    # Discord側から「〇〇秒ごとに生存報告（ハートビート）してね」って指示が来るから受け取る
    heartbeat_interval = event['d']['heartbeat_interval'] / 1000
    threading.Thread(target=heartbeat, args=(heartbeat_interval, ws)).start()

    # 君のトークンを使って「俺はWindowsのChromeからログインしてるPCユーザーだぜ」と偽装して潜入！
    payload = {
        "op": 2,
        "d": {
            "token": TOKEN,
            "properties": {
                "$os": "windows",
                "$browser": "chrome",
                "$device": "pc"
            }
        }
    }
    send_json_request(ws, payload)
    print("🔥 Discordに潜入成功！永遠のオンライン状態に突入したぜ！ 🔥")

    # 接続が切れないように、Discordからの通信を無限に受け取り続ける
    while True:
        event = receive_json_response(ws)
        if not event:
            break

if __name__ == '__main__':
    main()
