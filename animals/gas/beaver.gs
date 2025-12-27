// ===== ▽ 設定の読み込み (スクリプトの先頭) ▽ =====
// ★ スプレッドシート（SHEET_ID）は不要になった！
const PYTHON_SERVER_URL = PropertiesService.getScriptProperties().getProperty('PYTHON_SERVER_URL'); // サーバーのURL (必須)
const LINE_ACCESS_TOKEN = PropertiesService.getScriptProperties().getProperty('LINE_ACCESS_TOKEN'); // ビーバーのLINEトークン (必須)
const GEMINI_API_KEY = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');       // (予備) エラー時のGeminiキー

// ★ LINE_USER_ID は「エラー通知先」としてのみ利用（オプション）
const ADMIN_USER_ID = PropertiesService.getScriptProperties().getProperty('LINE_USER_ID');

// LINEのAPI URL
const LINE_REPLY_URL = 'https://api.line.me/v2/bot/message/reply';
const LINE_PUSH_URL = 'https://api.line.me/v2/bot/message/push';
// ===================================================


// ==========================================================
// ★★★ doPost(司令塔) と メモ処理関数群 ★★★
// ==========================================================

/**
 * LINEからのメッセージを受け付けるメイン関数 (doPost)
 * ★★★ マルチユーザー対応 ★★★
 */
/**
 * LINEからのメッセージを受け付けるメイン関数 (doPost)
 * ★★★ 強化版 ★★★
 */
function doPost(e) {
  const contents = JSON.parse(e.postData.contents);
  const events = contents.events[0];

  if (events.type !== 'message' || events.message.type !== 'text') {
    return;
  }

  const replyToken = events.replyToken;
  // ★ 前後の空白を削除して、判定しやすくする！
  const userMessage = events.message.text.trim();
  const userId = events.source.userId;

  if (!userId) return;

  let replyText = '';

  try {
    // ★★★ ここが分岐ポイント！ ★★★
    // 「メモ一覧」「予定一覧」「スケジュール」などに反応するようにする
    if (userMessage === 'メモ一覧' || userMessage === '予定一覧' || userMessage === 'スケジュール') {
      replyText = showMemoList(userId);

    } else if (userMessage.startsWith('メモ削除')) {
      replyText = deleteMemo(userId, userMessage);

    } else {
      // それ以外は、Geminiに渡して会話や登録をする
      replyText = processMessage(userId, userMessage);
    }
  } catch (err) {
    Logger.log('エラー: ' + err.message);
    replyText = 'エラーが起きたっぴ...💦';
  }

  replyLine(replyToken, replyText, LINE_ACCESS_TOKEN);

  return ContentService.createTextOutput(JSON.stringify({'content': 'post ok'})).setMimeType(ContentService.MimeType.JSON);
}
/**
 * 【改修】メモ一覧を表示する関数 (Firestore対応)
 */
function showMemoList(userId) {
  try {
    // 1. サーバーに、この人のメモを全部聞く
    const memos = callPython_GetMemos(userId);

    if (memos.length === 0) {
      return '🦫 メモは空っぽだビーバー！';
    }

    let memoListText = "🦫 今のメモ一覧だビーバー！\n";
    let cacheData = {}; // ★ 削除用の「番号」と「ID」の対応表

    // 2. 取得したデータを「番号付きリスト」に加工
    memos.forEach((memo, index) => {
      const displayIndex = index + 1; // ユーザーに見せる番号 (1始まり)
      const timeStr = memo.reminder_time ? memo.reminder_time : ' (時間指定なし)';

      memoListText += `\n${displayIndex}. [${timeStr}] ${memo.text}`;

      // 3. ★「番号: 1」は「FirestoreのID: abc-123」と紐付ける
      cacheData[displayIndex] = memo.memo_id;
    });

    memoListText += '\n\n削除したい場合は「メモ削除 1」のように番号で教えてビーバー！';

    // 4. ★ 紐付けた情報を「30分間」だけ一時保存する
    // ★ ユーザーごとに別々のキャッシュキーを使う
    const cache = CacheService.getScriptCache();
    cache.put(userId + '_memo_map', JSON.stringify(cacheData), 1800); // 1800秒 = 30分

    return memoListText;

  } catch (e) {
    Logger.log('メモ一覧の取得エラー: ' + e.message);
    // ★ エラーメッセージをユーザーに返す
    return '🦫 うぅ...メモ一覧の取得に失敗したビーバー...。管理人に聞いてみてほしいビーバー。\n(エラー: ' + e.message + ')';
  }
}


/**
 * 【改修】指定された番号のメモを削除する関数 (Firestore対応)
 */
function deleteMemo(userId, message) {
  const indexStr = message.replace('メモ削除', '').trim();
  const displayIndex = parseInt(indexStr, 10); // ユーザーが指定した「番号」

  if (isNaN(displayIndex) || displayIndex <= 0) {
    return '🦫 え？どのメモを削除するビーバー？\n「メモ削除 1」のように番号で教えてほしいビーバー！';
  }

  // 1. ★ 一時保存した「紐付け情報」をキャッシュから取り出す
  const cache = CacheService.getScriptCache();
  const cacheKey = userId + '_memo_map';
  const cachedData = cache.get(cacheKey);

  if (!cachedData) {
    return '🦫 あれ？さっき「メモ一覧」で表示したリストが見つからないビーバー...。\nもう一度「メモ一覧」と送ってから、削除を試してみてほしいビーバー。';
  }

  const memoMap = JSON.parse(cachedData);

  // 2. ユーザーが指定した「番号」に対応する「FirestoreのID」を探す
  const memoIdToDelete = memoMap[displayIndex];

  if (!memoIdToDelete) {
    return '🦫 あれ？その番号のメモはもう無いみたいだビーバー！';
  }

  try {
    // 3. ★ サーバーに「このIDのメモを消して！」と依頼
    callPython_DeleteMemo(memoIdToDelete);

    // 4. 削除に成功したら、キャッシュをクリアする
    cache.remove(cacheKey);

    return `🦫 メモ ${displayIndex} 番を削除したビーバー！`;

  } catch (e) {
    Logger.log('メモ削除エラー: ' + e.message);
    return '🦫 うぅ...メモの削除に失敗したビーバー...。管理人に聞いてみてほしいビーバー。\n(エラー: ' + e.message + ')';
  }
}


/**
 * 【改修】ユーザーからのメッセージを処理し、メモを追加する関数 (Firestore対応)
 */
/**
 * 【最終形態】ユーザーからのメッセージを処理し、メモを追加する関数 (日付・時刻完全対応版)
 */
function processMessage(userId, message) {
  try {
    // 1. ★ 現在の「日付と時刻」を取得する (例: 2025-11-11 19:30)
    const nowStr = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm');

    // 2. ★ AIへの依頼文をアップデート
    const prompt = `
あなたは優秀なスケジューラーAIです。
現在の日時は【 ${nowStr} 】です。

以下のユーザーのメッセージから、通知すべき日時を「yyyy-MM-dd HH:mm」の形式で計算・抽出してください。

【ルール】
1. 「10分後」などは、現在日時から計算してください。
2. 「土曜日の10時」などは、最も近い未来の日付を計算してください。
3. 「明日」「来週」などもカレンダー通りに計算してください。
4. 時間指定がない場合は「NO_TIME」とだけ答えてください。
5. 返答は「yyyy-MM-dd HH:mm」または「NO_TIME」のみです。

【メッセージ】
${message}`;

    const timeResult = callPython_GenerateText(prompt).trim();

    let reminderTime = '';
    let reply = '';

    // 結果が "2025-11-12 10:00" のような形式かをチェック
    const timeMatch = timeResult.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2})/);

    if (timeResult !== 'NO_TIME' && timeMatch) {
      reminderTime = timeMatch[1]; // "2025-11-12 10:00"
      reply = `🦫 OKビーバー！\n『${message}』を**${reminderTime}**に通知するよう設定しました。`;
    } else {
      reminderTime = '';
      reply = `🦫 メモ完了したビーバー！\n『${message}』をリストに書き留めました。後でまとめて整理しますね。`;
    }

    // 3. サーバーに保存を依頼
    callPython_AddMemo(userId, message, reminderTime);

    return reply;

  } catch (e) {
    Logger.log('メモ追加処理エラー: ' + e.message);
    return '🦫 うぅ...メモの追加に失敗したビーバー...。管理人に聞いてみてほしいビーバー。\n(エラー: ' + e.message + ')';
  }
}


// ==========================================================
// ★★★ タイマー実行関数群（マルチユーザー対応） ★★★
// ==========================================================

/**
 * 【改修版】5分おきに自動実行。エラー時は空気を見て静かにします。
 */
function sendReminder() {
  Logger.log('🔔 5分タイマー (sendReminder) 実行開始');
  try {
    const dueMemos = callPython_GetDueMemos();

    if (dueMemos.length === 0) {
      Logger.log('🔔 通知するメモはありませんでした。');
      return;
    }

    Logger.log(`🔔 ${dueMemos.length} 件のメモが通知対象です。`);

    dueMemos.forEach(memo => {
      const notificationText = `🔔 【時間指定メモ】 ${memo.text}`;
      try {
        pushLine(memo.user_id, notificationText, LINE_ACCESS_TOKEN);
        callPython_DeleteMemo(memo.memo_id);
        Logger.log(`🔔 送信＆削除成功 (ID: ${memo.memo_id})`);
      } catch (pushOrDeleteError) {
        Logger.log(`🔔 (ID: ${memo.memo_id}) の処理中エラー: ${pushOrDeleteError.message}`);
      }
    });

  } catch (e) {
    // ★★★ ここが「空気読み」ポイント！ ★★★
    // エラーメッセージに「502」「503」「500」などが含まれていたら、
    // これは「サーバー工事中」なので、LINEを送らずにログだけ残して終了する。
    const errorMsg = e.message;
    if (errorMsg.includes('503') || errorMsg.includes('502') || errorMsg.includes('500') || errorMsg.includes('Service Unavailable')) {
      Logger.log('⚠️ サーバーがデプロイ中またはダウン中のため、今回の通知はスキップします。');
      return; // ここで静かに帰る
    }

// それ以外の本当にヤバいエラー（プログラムミスなど）の時だけLINEする
    Logger.log('❌ sendReminder 関数自体で重大なエラー: ' + e.message);

    // ★ ↓ここを「//」でコメントアウトして、LINEを送らないようにする！
    // if (ADMIN_USER_ID) {
    //   pushLine(ADMIN_USER_ID, '【緊急エラー】sendReminder タイマーが停止しました: ' + e.message, LINE_ACCESS_TOKEN);
    // }
  }
}

/**
 * 【改修版】毎日自動実行。Geminiに「嘘をつくな」と教育済み。
 */
function sendDailySummary() {
  Logger.log('🗓️ 日次要約 (sendDailySummary) 実行開始');
  try {
    const memosByUser = callPython_GetDailySummaryMemos();
    const userIds = Object.keys(memosByUser);

    if (userIds.length === 0) {
      Logger.log('🗓️ 要約するメモはありませんでした。');
      // ビーバーが寂しがるなら、ここでも自分宛て通知はOFFにしてもいいかもです
      return;
    }

    userIds.forEach(userId => {
      const userMemos = memosByUser[userId];
      if (userMemos.length === 0) return;

      const tasksToSummarize = userMemos.map(memo => memo.text);
      const tasksString = tasksToSummarize.join('\n');

      // ★★★ ここが「正直者教育」ポイント！ ★★★
      // プロンプトをガチガチに厳しくしました。
      const prompt = `
あなたは「まめなビーバー」です。
以下の【今日のメモ】に書かれている内容 **だけ** を元に、タスクリストを作ってください。

【絶対的なルール】
1. 【今日のメモ】に書かれていないこと（歯医者、牛乳、スニーカーなど）は **絶対に** 創作しないでください。
2. もしメモの内容が空っぽ、または意味のない言葉だけの場合は、「今日は特に予定はないみたいだビーバー！ゆっくり休んでね💤」とだけ答えてください。
3. やるべきことがあれば、3つのカテゴリ（緊急・重要、その他、買い物）に分けて、絵文字を使って可愛く箇条書きにしてください。

【今日のメモ】
${tasksString}`;

      try {
        const summaryText = callPython_GenerateText(prompt);
        const notificationText =
`【🦫 今日のまめなビーバー・未整理メモリスト】
${summaryText}

✅ リストを整理しました！`;

        pushLine(userId, notificationText, LINE_ACCESS_TOKEN);

        userMemos.forEach(memo => {
          callPython_DeleteMemo(memo.memo_id);
        });
        Logger.log(`🗓️ ${userId} への送信完了`);

      } catch (summaryOrDeleteError) {
        Logger.log(`🗓️ (User: ${userId}) の処理中エラー: ${summaryOrDeleteError.message}`);
      }
    });

  } catch (e) {
    // ★★★ こちらも「空気読み」対応 ★★★
    const errorMsg = e.message;
    if (errorMsg.includes('503') || errorMsg.includes('502') || errorMsg.includes('500')) {
      Logger.log('⚠️ サーバーメンテナンス中のため、日次要約をスキップします。');
      return;
    }

    Logger.log('❌ sendDailySummary 関数自体で重大なエラー: ' + e.message);
    if (ADMIN_USER_ID) {
      pushLine(ADMIN_USER_ID, '【緊急エラー】sendDailySummary タイマーが停止しました: ' + e.message, LINE_ACCESS_TOKEN);
    }
  }
}


// ==========================================================
// ★★★ 道具箱（ヘルパー関数群） ★★★
// ==========================================================

// --- ▽ LINEに「返信」「Push」する関数群 (変更なし) ▽ ---
function replyLine(replyToken, text, token) {
  const messages = [{'type': 'text', 'text': text}];
  const payload = {'replyToken': replyToken, 'messages': messages};
  const options = {
    'method': 'post', 'contentType': 'application/json',
    'headers': {'Authorization': 'Bearer ' + token},
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true // ★ エラー時もGASを止めない
  };
  UrlFetchApp.fetch(LINE_REPLY_URL, options);
}
function pushLine(userId, text, token) {
  const messages = [{'type': 'text', 'text': text}];
  const payload = {'to': userId, 'messages': messages};
  const options = {
    'method': 'post', 'contentType': 'application/json',
    'headers': {'Authorization': 'Bearer ' + token},
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true // ★ エラー時もGASを止めない
  };
  UrlFetchApp.fetch(LINE_PUSH_URL, options);
}
// --- △ LINEに「返信」「Push」する関数群 (変更なし) △ ---


// --- ▽ サーバー（Python）を呼び出す関数群（Firestore対応）▽ ---

/**
 * 道具1：AIの頭脳（Gemini）で文章を考えてもらう
 * (callPythonServer -> callPython_GenerateText に名前変更)
 */

function callPython_GenerateText(prompt) {
  if (!PYTHON_SERVER_URL) {
    throw new Error('PYTHON_SERVER_URLが設定されていません。');
  }

  // ★ ここを変更！ GET ではなく POST で送る
  const url = PYTHON_SERVER_URL + '/check_reminders';
  const payload = JSON.stringify({ "prompt": prompt }); // 封筒に入れる

  const options = {
    'method': 'post', // POSTに変更
    'contentType': 'application/json',
    'payload': payload,
    'muteHttpExceptions': true
  };

  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  const responseText = response.getContentText();

  if (responseCode === 200) {
    // ★ 修正後のPythonに合わせて response_text を受け取る
    const json = JSON.parse(responseText);
    // Python側が {"response_text": "..."} または {"text": "..."} で返してくる想定
    return json.response_text || json.text || responseText;
  } else {
    Logger.log('Pythonサーバー(Gemini)エラー: ' + responseText);
    throw new Error('AI（Gemini）が応答しませんでした。');
  }
}

/**
 * 道具2：【新規】サーバーに「メモ追加」を依頼 (/add-memo)
 */
function callPython_AddMemo(userId, memoText, reminderTime) {
  const url = PYTHON_SERVER_URL + '/add-memo';
  const payload = JSON.stringify({
    "user_id": userId,
    "memo_text": memoText,
    "reminder_time": reminderTime
  });
  const options = {
    'method': 'post', 'contentType': 'application/json',
    'payload': payload, 'muteHttpExceptions': true
  };
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  const responseText = response.getContentText();
  if (responseCode === 200) {
    return JSON.parse(responseText); // (例: {"status": "success", "memo_id": "..."})
  } else {
    Logger.log('Pythonサーバー(AddMemo)エラー: ' + responseText);
    throw new Error('メモの追加に失敗しました。');
  }
}

/**
 * 道具3：【新規】サーバーに「メモ一覧」を要求 (/get-memos)
 */
function callPython_GetMemos(userId) {
  const url = PYTHON_SERVER_URL + '/get-memos/' + userId;
  const options = {'method': 'get', 'muteHttpExceptions': true};
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  const responseText = response.getContentText();
  if (responseCode === 200) {
    return JSON.parse(responseText).memos; // (例: [{memo_id, text, reminder_time}, ...])
  } else {
    Logger.log('Pythonサーバー(GetMemos)エラー: ' + responseText);
    throw new Error('メモ一覧の取得に失敗しました。');
  }
}

/**
 * 道具4：【新規】サーバーに「メモ削除」を依頼 (/delete-memo)
 */
function callPython_DeleteMemo(memoId) {
  const url = PYTHON_SERVER_URL + '/delete-memo/' + memoId;
  const options = {'method': 'delete', 'muteHttpExceptions': true};
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  const responseText = response.getContentText();
  if (responseCode === 200) {
    return JSON.parse(responseText); // (例: {"status": "success"})
  } else {
    Logger.log('Pythonサーバー(DeleteMemo)エラー: ' + responseText);
    throw new Error('メモの削除に失敗しました。');
  }
}

/**
 * 道具5：【新規】サーバーに「時間になったメモ」を要求 (タイマー用, /get-due-memos)
 */
function callPython_GetDueMemos() {
  const url = PYTHON_SERVER_URL + '/get-due-memos';
  const options = {'method': 'get', 'muteHttpExceptions': true};
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  const responseText = response.getContentText();
  if (responseCode === 200) {
    return JSON.parse(responseText).due_memos; // (例: [{memo_id, user_id, text}, ...])
  } else {
    Logger.log('Pythonサーバー(GetDueMemos)エラー: ' + responseText);
    throw new Error('「時間指定メモ」の取得に失敗しました。');
  }
}

/**
 * 道具6：【新規】サーバーに「日次要約メモ」を要求 (タイマー用, /get-daily-summary-memos)
 */
function callPython_GetDailySummaryMemos() {
  const url = PYTHON_SERVER_URL + '/get-daily-summary-memos';
  const options = {'method': 'get', 'muteHttpExceptions': true};
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  const responseText = response.getContentText();
  if (responseCode === 200) {
    return JSON.parse(responseText).memos_by_user; // (例: {"user_id_A": [{memo_id, text}], ...})
  } else {
    Logger.log('Pythonサーバー(GetDailySummary)エラー: ' + responseText);
    throw new Error('「日次要約メモ」の取得に失敗しました。');
  }
}

/**
 * 道具7：【新規】毎朝実行！前日＆当日通知トリガー
 * Python側の /trigger-check-reminders を叩くだけのスイッチ
 */
function triggerDailyCheck() {
  Logger.log('⏰ 前日＆当日通知チェック (triggerDailyCheck) 実行開始');

  if (!PYTHON_SERVER_URL) {
    Logger.log('❌ PYTHON_SERVER_URL が設定されていません');
    return;
  }

  // Python側のエンドポイント
  const url = PYTHON_SERVER_URL + '/trigger-check-reminders';

  const options = {
    'method': 'get',
    'muteHttpExceptions': true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const code = response.getResponseCode();
    const text = response.getContentText();

    Logger.log(`⏰ 結果: ${code} - ${text}`);

  } catch (e) {
    Logger.log(`❌ トリガー実行エラー: ${e.message}`);
  }
}