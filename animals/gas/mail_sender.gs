function doPost(e) {

  try {
    const data = JSON.parse(e.postData.contents);
    const to = data.to;
    const subject = data.subject;
    const body = data.body;

    // Gmailを送信する
    GmailApp.sendEmail(to, subject, body);

    // --- ▼▼▼ ここを「平文テキスト」に変更 ▼▼▼ ---
    return ContentService.createTextOutput("SUCCESS");
    // --- ▲▲▲ ---

  } catch (error) {
    // --- ▼▼▼ ここも「平文テキスト」に変更 ▼▼▼ ---
    // エラー内容をテキストとして返す
    return ContentService.createTextOutput("ERROR: " + error.message);
    // --- ▲▲▲ ---
  }
}