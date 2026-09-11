const { Client } = require('discord.js-selfbot-v13');
const { joinVoiceChannel, getVoiceConnection, VoiceConnectionStatus, entersState } = require('@discordjs/voice');
const express = require('express');

const app = express();
const client = new Client({ checkUpdate: false });

app.get('/', (req, res) => res.send('Discord Account is Online!'));
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));

// --- 🔽 追加：切断されたときに「自動でしがみつく」処理 🔽 ---
function handleVoiceConnection(connection) {
  connection.on(VoiceConnectionStatus.Disconnected, async () => {
    console.log('⚠️ VCの通信が切断されました。Discord側のサーバー変更の可能性があります。再接続を試みます...');
    try {
      // 5秒間、再接続（Signalling / Connecting）ができるか粘る
      await Promise.race([
        entersState(connection, VoiceConnectionStatus.Signalling, 5000),
        entersState(connection, VoiceConnectionStatus.Connecting, 5000),
      ]);
      console.log('✅ VCへの再接続（しがみつき）に成功しました！');
    } catch (error) {
      console.log('🛑 再接続に失敗しました。Renderの再起動などの理由で完全に切断されました。');
      connection.destroy();
    }
  });
}
// -----------------------------------------------------------

client.on('ready', () => {
  console.log(`✅ Logged in as ${client.user.tag}!`);
  console.log('🎧 あなたが手動でVCに入るのを待機しています...');
});

client.on('voiceStateUpdate', (oldState, newState) => {
  if (newState.id !== client.user.id) return;

  // 1. 新しくVCに入った、または別のVCに移動した場合
  if (newState.channelId) {
    const currentConnection = getVoiceConnection(newState.guild.id);
    if (currentConnection && currentConnection.joinConfig.channelId === newState.channelId) {
      return;
    }

    console.log(`🎤 VCに参加しました: ${newState.channel.name}`);
    
    // VC接続を開始
    const connection = joinVoiceChannel({
      channelId: newState.channelId,
      guildId: newState.guild.id,
      adapterCreator: newState.guild.voiceAdapterCreator,
      selfDeaf: true,
      selfMute: false
    });

    // ここで上で作った「しがみつき処理」をセットする
    handleVoiceConnection(connection);
  }
  // 2. Discordアプリから「切断」を押して退出した場合
  else if (!newState.channelId && oldState.channelId) {
    console.log(`🛑 VCから手動で退出しました。Render側の接続も解除します。`);
    const currentConnection = getVoiceConnection(oldState.guild.id);
    if (currentConnection) {
      currentConnection.destroy();
    }
  }
});

process.on('unhandledRejection', error => {
  console.error('Unhandled promise rejection:', error);
});

client.login(process.env.TOKEN).catch(err => {
  console.error('❌ ログインエラー:', err.message);
});
