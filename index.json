const { Client } = require('discord.js-selfbot-v13');
const express = require('express');

const app = express();
const client = new Client({
    checkUpdate: false // アップデート確認の警告を消すため
});

// Renderが生きてるか確認するためのダミーページ
app.get('/', (req, res) => {
  res.send('Discord Account is Online!');
});

// Renderが指定するポート（または3000番）で待機
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

// Discordへのログイン成功時の処理
client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
});

// 環境変数に設定したトークンを使ってログイン
// ※コード内に直接トークンを書くのは危険なため、環境変数を使用します
client.login(process.env.TOKEN);
