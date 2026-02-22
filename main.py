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
    response = ws.recv()
    if response:
        return json.loads(response)

def heartbeat(interval, ws):
    print("心臓マッサージ（ハートビート）開始！")
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": "null"
        }
        try:
            send_json_request(ws, heartbeatJSON)
            print("ドクン...（Discordに生存アピール完了）")
        except Exception as e:
            # パイプが切れたらエラーを出してこのループを終わらせる（本体側で再接続する）
            print(f"心臓マッサージ失敗...パイプが切断されたぜ！: {e}")
            break

def main():
    if not TOKEN:
        print("⚠️ エラー: Renderの環境変数に『DISCORD_TOKEN』が設定されてないぞ！")
        return

    # GAS受け止め用のWebサーバーを起動（これは最初に1回やればOK）
    keep_alive()

    # 🔥 不死鳥ループ（切断されても無限に再接続する）🔥
    while True:
        try:
            print("DiscordのGatewayに接続開始...")
            ws = websocket.WebSocket()
            ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')
            event = receive_json_response(ws)

            # ハートビートの間隔を取得して別スレッドで動かす
            heartbeat_interval = event['d']['heartbeat_interval'] / 1000
            threading.Thread(target=heartbeat, args=(heartbeat_interval, ws)).start()

            # 潜入用の偽装データ
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

            # 無限にDiscordからの通信を受け取る
            while True:
                event = receive_json_response(ws)
                if not event:
                    print("Discord側から通信を切られたぜ！再接続の準備をする...")
                    break
        
        except Exception as e:
            print(f"接続エラー発生！: {e}")
        
        # すぐに再接続するとスパム判定されるから、10秒待ってから復活する
        print("10秒後に再接続するぜ...")
        time.sleep(10)

if __name__ == '__main__':
    main()
