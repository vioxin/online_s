from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    # GASがアクセスしてきたときに返す言葉（画面に表示される）
    return "GASからのツンツン確認！Renderは元気に稼働中だぜ！"

def run():
    # RenderはWeb用のポート（基本は10000番など）を自動で割り当てる
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Webサーバーを別スレッド（裏っかわ）で動かし続けるおまじない
    t = Thread(target=run)
    t.start()
