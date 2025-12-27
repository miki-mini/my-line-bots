// ===============================================
// ▽ 設定の読み込み ▽
// ===============================================
const PYTHON_SERVER_URL = PropertiesService.getScriptProperties().getProperty('PYTHON_SERVER_URL');
const LINE_ACCESS_TOKEN = PropertiesService.getScriptProperties().getProperty('LINE_TOKEN');
const GEMINI_API_KEY = PropertiesService.getScriptProperties().getProperty('GEMINI_API');

// LINEのAPI URL
const LINE_REPLY_URL = 'https://api.line.me/v2/bot/message/reply';
const LINE_PUSH_URL = 'https://api.line.me/v2/bot/message/push';

// GeminiのAPI URL
const GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=" + GEMINI_API_KEY;


// ===============================================
// ▽ メイン処理 (doPost) ▽
// ===============================================
/**
 * メイン関数：LINEからの全メッセージをここで受け付けます
 */
function doPost(e) {
  const contents = JSON.parse(e.postData.contents);
  const event = contents.events[0];

  const replyToken = event.replyToken;
  const userId = event.source.userId;
  const message = event.message;

  // ▽ 1. 画像が送られてきたとき
  if (message.type === 'image') {
    handleImageAnalysis(replyToken, userId, message.id);

  // ▽ 2. テキストが送られてきたとき
  } else if (message.type === 'text') {
    const userMessage = message.text;

    // ①「描いて：」から始まるとき
    if (userMessage.startsWith("描いて：")) {
      handleImageGeneration(replyToken, userId, userMessage);

    // ②「グラフ」という言葉が入っているとき (体重)
    } else if (userMessage.includes("グラフ")) {
      handleGraphRequest(replyToken);

    // ③「カロリー」という言葉が入っているとき (今回追加！)
    } else if (userMessage.includes("カロリー")) {
      handleCalorieGraphRequest(replyToken);

    // ④ 数字だけのとき (体重記録)
    } else if (!isNaN(userMessage)) {
      handleWeightRecord(replyToken, userId, userMessage);

    // ⑤ それ以外 (普通のおしゃべり) ★これが必ず最後！
    } else {
      handleOldOwlLogic(replyToken, userMessage);
    }
  }

  return ContentService.createTextOutput(JSON.stringify({'content': 'post ok'})).setMimeType(ContentService.MimeType.JSON);
}


// ===============================================
// ▽ 各機能の関数たち ▽
// ===============================================

/**
 * ★新機能 (グラフ表示)
 */
function handleGraphRequest(replyToken) {
  // 1. Pythonサーバーのグラフ用URL
  var graphEndpoint = "/graph/weight";

  // キャッシュ対策
  var timestamp = new Date().getTime();
  var imageUrl = PYTHON_SERVER_URL + graphEndpoint + "?t=" + timestamp;

  // 2. メッセージ作成
  var messages = [{
    "type": "image",
    "originalContentUrl": imageUrl,
    "previewImageUrl": imageUrl
  }];

  // 3. 送信設定
  var replyOptions = {
    "method": "post",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + LINE_ACCESS_TOKEN
    },
    "payload": JSON.stringify({
      "replyToken": replyToken,
      "messages": messages
    })
  };

  // 4. 送信実行
  try {
    UrlFetchApp.fetch(LINE_REPLY_URL, replyOptions);
  } catch (e) {
    Logger.log("グラフ送信エラー: " + e.message);
  }
}

/**
 * ★新機能 (画像認識)
 */
function handleImageAnalysis(replyToken, userId, messageId) {
  try {
    replyText(replyToken, "🦉 (ふむふむ、この写真ですね... 教授に分析してもらいます...)");
    const imageBlob = fetchImageFromLine(messageId);
    const analysisResult = callPythonVisionServer(imageBlob);
    pushText(userId, "🦉 教授の分析結果です：\n「" + analysisResult + "」");
  } catch (e) {
    Logger.log('★画像分析エラー発生★: ' + e.message);
    pushText(userId, "🦉エラー発生！ 教授が写真を分析できませんでした。\n" + e.message);
  }
}

/**
 * ★既存機能 (画像生成)
 */
function handleImageGeneration(replyToken, userId, userMessage) {
  const prompt = userMessage.replace("描いて：", "").trim();
  try {
    replyText(replyToken, "🦉 ...フクロウ教授、ただいま描いています...（最大1分ほどかかります）");
    const imageUrl = callPythonImageServer(prompt);
    pushImage(userId, imageUrl);
  } catch (e) {
    Logger.log('★画像生成エラー発生★: ' + e.message);
    pushText(userId, "🦉エラー発生！ 教授が絵を描けませんでした。\n" + e.message);
  }
}

/**
 * ★既存機能 (おしゃべり)
 */
function handleOldOwlLogic(replyToken, userMessage) {
  var replyMessages = [];
  var fileIdPositive = "1rGV-i0wOi0hnknmLosADNQsuuH8wc-9q";
  var fileIdNegative = "1uHal6xFb4jRFOTigdV0YYWraO7epx-YE";
  var fileIdNeutral  = "1fRHfs6kn7JNw4i8S5PdKW11eviAa1Rki";
  var fileIdQuestion = "1voWkLYrDsnB6hXQ9Pzu9_7t6iDJerveI";

  var imageUrlPositive = "https://drive.google.com/uc?export=view&id=" + fileIdPositive;
  var imageUrlNegative = "https://drive.google.com/uc?export=view&id=" + fileIdNegative;
  var imageUrlNeutral  = "https://drive.google.com/uc?export/view&id=" + fileIdNeutral;
  var imageUrlQuestion = "https://drive.google.com/uc?export/view&id=" + fileIdQuestion;

  var selectedImageUrl = imageUrlNeutral;
  var geminiReply = "";

  try {
    var prompt = userMessage + "\n\n上記のメッセージに対する返答を生成し、最後に必ず改行を入れて [感情: ポジティブ/ネガティブ/ニュートラル] の形式で感情分析結果を付けてください。";
    var payload = { "contents": [{"parts": [{"text": prompt}]}] };
    var options = {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload)
    };
    var response = UrlFetchApp.fetch(GEMINI_API_URL, options);
    var jsonResponse = JSON.parse(response.getContentText());
    var fullReply = jsonResponse.candidates[0].content.parts[0].text;

    var emotion = "ニュートラル";
    var emotionMatch = fullReply.match(/\[感情: (ポジティブ|ネガティブ|ニュートラル)\]$/);
    if (emotionMatch) {
      emotion = emotionMatch[1];
      geminiReply = fullReply.replace(/\[感情: (ポジティブ|ネガティブ|ニュートラル)\]$/, "").trim();
    } else {
      geminiReply = fullReply;
    }

    if (userMessage.includes("？") || userMessage.includes("?")) {
        selectedImageUrl = imageUrlQuestion;
    } else if (emotion === "ポジティブ") {
      selectedImageUrl = imageUrlPositive;
    } else if (emotion === "ネガティブ") {
      selectedImageUrl = imageUrlNegative;
    } else {
      selectedImageUrl = imageUrlNeutral;
    }

    replyMessages = [
      { "type": "text", "text": geminiReply },
      { "type": "image", "originalContentUrl": selectedImageUrl, "previewImageUrl": selectedImageUrl }
    ];

  } catch (error) {
    replyMessages = [{ "type": "text", "text": "【エラーが発生しました】\n" + error.toString() }];
  }

  var replyOptions = {
    "method": "post",
    "headers": { "Content-Type": "application/json", "Authorization": "Bearer " + LINE_ACCESS_TOKEN },
    "payload": JSON.stringify({ "replyToken": replyToken, "messages": replyMessages })
  };
  UrlFetchApp.fetch(LINE_REPLY_URL, replyOptions);
}


// ===============================================
// ▽ ツール（ヘルパー関数） ▽
// ===============================================

function fetchImageFromLine(messageId) {
  const url = `https://api-data.line.me/v2/bot/message/${messageId}/content`;
  const options = {
    "method": "get",
    "headers": { "Authorization": "Bearer " + LINE_ACCESS_TOKEN },
    "muteHttpExceptions": true
  };
  const response = UrlFetchApp.fetch(url, options);
  if (response.getResponseCode() === 200) {
    return response.getBlob();
  } else {
    throw new Error('LINEサーバーから画像の取得に失敗しました。');
  }
}

function callPythonVisionServer(imageBlob) {
  if (!PYTHON_SERVER_URL) throw new Error('PYTHON_SERVER_URLが設定されていません。');
  const url = PYTHON_SERVER_URL + '/analyze_image/';
  imageBlob.setName("image_file");
  const payload = { "image_file": imageBlob };
  const options = {
    "method": "post",
    "payload": payload,
    "muteHttpExceptions": true
  };
  const response = UrlFetchApp.fetch(url, options);
  if (response.getResponseCode() === 200) {
    return JSON.parse(response.getContentText()).analysis;
  } else {
    throw new Error('Pythonサーバー（教授）がエラーを返しました: ' + response.getContentText());
  }
}

function callPythonImageServer(prompt) {
  if (!PYTHON_SERVER_URL) throw new Error('PYTHON_SERVER_URLが設定されていません。');
  const url = PYTHON_SERVER_URL + '/generate-image';
  const payload = JSON.stringify({"prompt": prompt});
  const options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': payload,
    'muteHttpExceptions': true,
  };
  const response = UrlFetchApp.fetch(url, options);
  if (response.getResponseCode() === 200) {
    return JSON.parse(response.getContentText()).image_url;
  } else {
    throw new Error('Pythonサーバー（教授）がエラーを返しました: ' + response.getContentText());
  }
}

function pushImage(userId, imageUrl) {
  const messages = [{'type': 'image', 'originalContentUrl': imageUrl, 'previewImageUrl': imageUrl}];
  UrlFetchApp.fetch(LINE_PUSH_URL, {
    'method': 'post',
    'contentType': 'application/json',
    'headers': {'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN},
    'payload': JSON.stringify({'to': userId, 'messages': messages})
  });
}

function pushText(userId, text) {
  const messages = [{'type': 'text', 'text': text}];
  UrlFetchApp.fetch(LINE_PUSH_URL, {
    'method': 'post',
    'contentType': 'application/json',
    'headers': {'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN},
    'payload': JSON.stringify({'to': userId, 'messages': messages})
  });
}

function replyText(replyToken, text) {
  const messages = [{'type': 'text', 'text': text}];
  UrlFetchApp.fetch(LINE_REPLY_URL, {
    'method': 'post',
    'contentType': 'application/json',
    'headers': {'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN},
    'payload': JSON.stringify({'replyToken': replyToken, 'messages': messages})
  });
}

/**
 * ★★★ 新機能 (体重記録) ★★★
 * 数字を受け取ってPythonサーバーに送る関数
 */
function handleWeightRecord(replyToken, userId, text) {
  // 1. ユーザーが送ってきた数字 (例: "64.5")
  var weight = parseFloat(text);

  // 2. Pythonサーバーに送信
  try {
    var url = PYTHON_SERVER_URL + "/record/weight";
    var payload = JSON.stringify({ "weight": weight });

    var options = {
      "method": "post",
      "contentType": "application/json",
      "payload": payload,
      "muteHttpExceptions": true
    };

    var response = UrlFetchApp.fetch(url, options);

    // 3. 成功したら返事をLINEに送る
    if (response.getResponseCode() === 200) {
      var json = JSON.parse(response.getContentText());
      replyText(replyToken, "🦉 記録しました！\n" + json.message);
    } else {
      replyText(replyToken, "🦉 記録に失敗しました...\n" + response.getContentText());
    }

  } catch (e) {
    replyText(replyToken, "🦉 エラーが発生しました。\n" + e.message);
  }
}
/**
 * ★★★ 新機能 (カロリーグラフ) ★★★
 */
function handleCalorieGraphRequest(replyToken) {
  // 1. Pythonサーバーのカロリーグラフ用URL
  var graphEndpoint = "/graph/calories";

  var timestamp = new Date().getTime();
  var imageUrl = PYTHON_SERVER_URL + graphEndpoint + "?t=" + timestamp;

  var messages = [{
    "type": "image",
    "originalContentUrl": imageUrl,
    "previewImageUrl": imageUrl
  }];

  var replyOptions = {
    "method": "post",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + LINE_ACCESS_TOKEN
    },
    "payload": JSON.stringify({
      "replyToken": replyToken,
      "messages": messages
    })
  };

  try {
    UrlFetchApp.fetch(LINE_REPLY_URL, replyOptions);
  } catch (e) {
    Logger.log("グラフ送信エラー: " + e.message);
  }
}