// ----- ▽ 設定 ▽ -----
// PythonサーバーのURL (必須)
const PYTHON_SERVER_URL = PropertiesService.getScriptProperties().getProperty('PYTHON_SERVER_URL');

/**
 * 朝のニュース配信トリガー
 * Pythonサーバーの /trigger_morning_news を叩くだけのシンプルな関数
 */
function sendMorningNews() {
  Logger.log('🦫 朝のニュース配信トリガーを実行します...');

  if (!PYTHON_SERVER_URL) {
    Logger.log('❌ PYTHON_SERVER_URL が設定されていません。スクリプトプロパティを確認してください。');
    return;
  }

  // Python側のエンドポイント
  const url = PYTHON_SERVER_URL + '/trigger_morning_news';

  const options = {
    'method': 'post',
    'muteHttpExceptions': true
  };

  try {
    // リクエスト送信
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();

    if (responseCode === 200) {
      Logger.log('✅ ニュース配信リクエスト成功: ' + responseText);
    } else {
      Logger.log('⚠️ ニュース配信リクエスト失敗 (Code: ' + responseCode + '): ' + responseText);
    }

  } catch (e) {
    Logger.log('❌ 通信エラー: ' + e);
  }
}
