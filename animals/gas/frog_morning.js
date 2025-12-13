// ----- ▽ ここから設定 ▽ -----

// 準備1: チャンネルアクセストークン
const CHANNEL_ACCESS_TOKEN = PropertiesService.getScriptProperties().getProperty('LINE_ACCESS_TOKEN');

// 準備2: あなたのLINEユーザーID
const YOUR_USER_ID = PropertiesService.getScriptProperties().getProperty('LINE_USER_ID');

// 準備3: 天気を知りたい地点の緯度経度（東京）
const LATITUDE = 35.6895;
const LONGITUDE = 139.6917;
const LOCATION_NAME = '東京';

// 準備4: Gemini APIキー
const GEMINI_API_KEY = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');

// ----- △ ここまで設定 △ -----


/**
 * メインの関数（この関数をトリガーで呼び出します）
 */
function sendWeatherForecast() {
  try {
    // 1. Open-Meteo APIから天気データを取得
    const weatherData = fetchWeatherFromOpenMeteo(LATITUDE, LONGITUDE);

    // データが取れなかった場合は、ログを出して終了（エラーにはしない）
    if (!weatherData) {
      Logger.log('⚠️ 天気データが取得できなかったため、送信を中止しました。');
      return;
    }

    // 2. Geminiで服装アドバイスを取得
    const advice = getFashionAdviceWithGemini(weatherData, GEMINI_API_KEY);

    // 3. データをLINE用のメッセージに整形
    const message = formatWeatherMessage(weatherData, advice);

    // 4. メッセージをLINEに送信
    sendLinePush(message, CHANNEL_ACCESS_TOKEN, YOUR_USER_ID);
    Logger.log('✅ 天気予報をLINEに送信しました。');

  } catch (e) {
    Logger.log('❌ 全体エラーが発生しました: ' + e);
  }
}


/**
 * 1. Open-Meteo APIから天気データを取得する関数
 * エラー対策強化版🛡️
 */
function fetchWeatherFromOpenMeteo(lat, lon) {
  const weatherUrl = 'https://api.open-meteo.com/v1/forecast?' +
    'latitude=' + lat +
    '&longitude=' + lon +
    '&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max' +
    '&hourly=relative_humidity_2m,apparent_temperature,wind_speed_10m' +
    '&timezone=Asia%2FTokyo' +
    '&forecast_days=2';

  const pollenUrl = 'https://air-quality-api.open-meteo.com/v1/air-quality?' +
    'latitude=' + lat +
    '&longitude=' + lon +
    '&hourly=alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,olive_pollen,ragweed_pollen' +
    '&timezone=Asia%2FTokyo' +
    '&forecast_days=2';

  try {
    // APIリクエスト
    const weatherResponse = UrlFetchApp.fetch(weatherUrl, { muteHttpExceptions: true });
    const pollenResponse = UrlFetchApp.fetch(pollenUrl, { muteHttpExceptions: true });

    // ステータスコードの確認（200以外なら失敗とみなす）
    if (weatherResponse.getResponseCode() !== 200) {
      Logger.log('⚠️ 天気APIエラー: ' + weatherResponse.getContentText());
      return null;
    }

    const weatherJson = JSON.parse(weatherResponse.getContentText());
    let pollenJson = null;

    // 花粉APIはたまに失敗するので、失敗しても天気だけで進めるようにする
    if (pollenResponse.getResponseCode() === 200) {
      pollenJson = JSON.parse(pollenResponse.getContentText());
    } else {
      Logger.log('⚠️ 花粉APIエラー（天気のみで続行します）');
    }

    // 🚨 ここが修正ポイント！データの中身が空っぽじゃないかチェック
    if (!weatherJson || !weatherJson.daily || !weatherJson.daily.time) {
      Logger.log('⚠️ 天気データが不正です（dailyデータなし）');
      return null;
    }

    const now = new Date();
    const currentHour = now.getHours();

    // 花粉データの集計（データがあれば）
    let todayPollenMax = { levelText: 'データなし', total: 0 };
    if (pollenJson && pollenJson.hourly) {
      todayPollenMax = getMaxPollenToday(pollenJson.hourly, currentHour);
    }

    // データを整理して返す
    return {
      location: LOCATION_NAME,
      today: {
        date: weatherJson.daily.time[0],
        weatherCode: weatherJson.daily.weather_code[0],
        weatherText: getWeatherText(weatherJson.daily.weather_code[0]),
        tempMax: weatherJson.daily.temperature_2m_max[0],
        tempMin: weatherJson.daily.temperature_2m_min[0],
        precipitationProb: weatherJson.daily.precipitation_probability_max[0],
        uvIndex: weatherJson.daily.uv_index_max[0],
        humidity: weatherJson.hourly.relative_humidity_2m[currentHour],
        apparentTemp: weatherJson.hourly.apparent_temperature[currentHour],
        windSpeed: weatherJson.hourly.wind_speed_10m[currentHour],
        windSpeedMax: weatherJson.daily.wind_speed_10m_max[0],
        windGustMax: weatherJson.daily.wind_gusts_10m_max[0],
        pollen: todayPollenMax
      },
      tomorrow: {
        date: weatherJson.daily.time[1],
        weatherCode: weatherJson.daily.weather_code[1],
        weatherText: getWeatherText(weatherJson.daily.weather_code[1]),
        tempMax: weatherJson.daily.temperature_2m_max[1],
        tempMin: weatherJson.daily.temperature_2m_min[1],
        precipitationProb: weatherJson.daily.precipitation_probability_max[1],
        uvIndex: weatherJson.daily.uv_index_max[1],
        windSpeedMax: weatherJson.daily.wind_speed_10m_max[1],
        windGustMax: weatherJson.daily.wind_gusts_10m_max[1]
      }
    };

  } catch (e) {
    Logger.log('❌ fetchWeatherFromOpenMeteo エラー: ' + e);
    return null;
  }
}

// 〜〜〜 以下、ヘルパー関数（そのまま変更なしでOK） 〜〜〜

function getMaxPollenToday(hourlyPollen, currentHour) {
  const endHour = 24;
  let maxGrass = 0, maxBirch = 0, maxAlder = 0, maxMugwort = 0, maxRagweed = 0;

  for (let i = currentHour; i < endHour; i++) {
    if (hourlyPollen.grass_pollen) maxGrass = Math.max(maxGrass, hourlyPollen.grass_pollen[i] || 0);
    if (hourlyPollen.birch_pollen) maxBirch = Math.max(maxBirch, hourlyPollen.birch_pollen[i] || 0);
    if (hourlyPollen.alder_pollen) maxAlder = Math.max(maxAlder, hourlyPollen.alder_pollen[i] || 0);
    if (hourlyPollen.mugwort_pollen) maxMugwort = Math.max(maxMugwort, hourlyPollen.mugwort_pollen[i] || 0);
    if (hourlyPollen.ragweed_pollen) maxRagweed = Math.max(maxRagweed, hourlyPollen.ragweed_pollen[i] || 0);
  }

  const totalMax = Math.max(maxGrass, maxBirch, maxAlder, maxMugwort, maxRagweed);
  return {
    total: totalMax,
    levelText: getPollenLevelText(totalMax)
  };
}

function getPollenLevelText(value) {
  if (value <= 10) return '少ない 😊';
  if (value <= 30) return 'やや多い 😐';
  if (value <= 60) return '多い 😷';
  if (value <= 100) return '非常に多い 🤧';
  return '極めて多い 🚨';
}

function getWeatherText(code) {
  const weatherCodes = {
    0: '快晴 ☀️', 1: '晴れ 🌤️', 2: '一部曇り ⛅', 3: '曇り ☁️',
    45: '霧 🌫️', 48: '霧氷 🌫️', 51: '小雨 🌧️', 53: '雨 🌧️',
    55: '強い雨 🌧️', 61: '小雨 🌧️', 63: '雨 🌧️', 65: '大雨 🌧️',
    80: 'にわか雨 🌦️', 81: 'にわか雨 🌦️', 82: '激しいにわか雨 ⛈️',
    95: '雷雨 ⛈️', 96: '雷雨（ひょう）⛈️', 99: '激しい雷雨（ひょう）⛈️'
  };
  return weatherCodes[code] || '不明';
}

function getFashionAdviceWithGemini(weatherData, apiKey) {
  try {
    const today = weatherData.today;
    const weatherInfo = `
    - 場所: ${weatherData.location}
    - 今日の天気: ${today.weatherText}
    - 気温: 最高${today.tempMax}℃ / 最低${today.tempMin}℃
    - 降水確率: ${today.precipitationProb}%
    - 風速: ${today.windSpeed} km/h (最大${today.windSpeedMax} km/h)
    - 花粉: ${today.pollen.levelText}
    `;

    const prompt = `
    あなたは天気予報士のカエル「ケロくん」です。
    以下のデータを見て、今日の服装アドバイスをしてください。
    【データ】${weatherInfo}
    【指示】
    - 「〜だケロ」「〜ケロよ」という語尾で、親しみやすく。
    - 200文字以内で絵文字も入れて。
    - 暑さ、寒さ、雨、風、花粉への対策を含めて。
    `;

    const url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=' + apiKey;
    const payload = { 'contents': [{'parts': [{'text': prompt}]}] };
    const options = {
      'method': 'post',
      'contentType': 'application/json',
      'payload': JSON.stringify(payload),
      'muteHttpExceptions': true
    };

    const response = UrlFetchApp.fetch(url, options);
    const responseData = JSON.parse(response.getContentText());

    if (responseData && responseData.candidates) {
      return responseData.candidates[0].content.parts[0].text;
    }
    return 'アドバイスが取得できなかったケロ...';
  } catch (e) {
     return 'エラーが発生したケロ...';
  }
}

function formatWeatherMessage(data, advice) {
  return `🐸 ${data.location}の天気 🐸\n\n` +
         `📅 今日：${data.today.weatherText}\n` +
         `🌡️ ${data.today.tempMin}℃ 〜 ${data.today.tempMax}℃\n` +
         `☔ 降水: ${data.today.precipitationProb}%\n` +
         `💨 最大風速: ${data.today.windSpeedMax}km/h\n` +
         `🌸 花粉: ${data.today.pollen.levelText}\n\n` +
         `👕 ${advice}\n\n` +
         `🔗 詳細: https://www.google.com/search?q=天気+${data.location}`;
}

function sendLinePush(message, token, userId) {
  const url = 'https://api.line.me/v2/bot/message/push';
  const payload = {
    'to': userId,
    'messages': [{'type': 'text','text': message}]
  };
  const options = {
    'method': 'post',
    'contentType': 'application/json',
    'headers': {'Authorization': 'Bearer ' + token},
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  UrlFetchApp.fetch(url, options);
}