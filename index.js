const { Client } = require('discord.js-selfbot-v13');
const { joinVoiceChannel, VoiceConnectionStatus, getVoiceConnection } = require('@discordjs/voice');
const express = require('express');

const app = express();
const client = new Client({
  checkUpdate: false
});

// Renderが生きてるか確認するためのダミーページ
app.get('/', (req, res) => {
  res.send('Discord Account is Online!');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

// 設定項目
const GUILD_ID = process.env.GUILD_ID; // サーバID
const CHANNEL_ID = process.env.CHANNEL_ID; // ボイスチャンネルID

// 手動切断フラグ（自分が手動で退出したかを追跡）
let isManuallyDisconnected = false;

// ボイスチャンネルに接続する関数
function connectVoiceChannel() {
  const guild = client.guilds.cache.get(GUILD_ID);
  if (!guild) return console.error('指定されたサーバーが見つかりません。');

  const connection = joinVoiceChannel({
    channelId: CHANNEL_ID,
    guildId: GUILD_ID,
    adapterCreator: guild.voiceAdapterCreator,
    selfDeaf: true, // 自動でスピーカーミュート（負荷軽減）
    selfMute: false
  });

  // 状態変化の監視
  connection.on(VoiceConnectionStatus.Disconnected, async () => {
    // 手動で抜けた場合（Destroyed）は再接続しない
    if (isManuallyDisconnected) {
      console.log('手動でVCを退出したため、自動再接続を停止します。');
      return;
    }

    // 回線落ちやKickなどの場合は再接続を試みる
    console.log('VCから切断されました。再接続を試みます...');
    try {
      await Promise.race([
        connection.reconnect(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))
      ]);
    } catch (e) {
      // 再接続失敗時は新しく接続を作り直す
      connection.destroy();
      connectVoiceChannel();
    }
  });

  connection.on(VoiceConnectionStatus.Destroyed, () => {
    // 手動でVCを切断した場合に発火
    isManuallyDisconnected = true;
  });
}

// ログイン成功時
client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
  isManuallyDisconnected = false; // ログイン時に初期化
  connectVoiceChannel();
});

client.login(process.env.TOKEN);
