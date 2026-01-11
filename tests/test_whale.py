
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.whale import calculate_past_date, _get_nasa_apod_image

def test_calculate_past_date():
    """日付計算のロジックテスト"""
    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    assert calculate_past_date(0) == today

    # 計算ロジック自体の検証はPython標準ライブラリの信頼性によるが、
    # 呼び出し形式が変わっていないかの確認
    result = calculate_past_date(10)
    assert len(result) == 10 # "YYYY-MM-DD" は10文字
    assert result.count("-") == 2

@patch("requests.get")
def test_get_nasa_apod_image_success(mock_get):
    """API呼び出し成功時のテスト"""
    # モックレスポンスの準備
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "media_type": "image",
        "url": "http://example.com/image.jpg",
        "title": "Test Image"
    }
    mock_get.return_value = mock_response

    # 固定日付で実行
    target_date = "2023-01-01"
    result = _get_nasa_apod_image(target_date)

    # 検証
    assert result is not None
    # http -> https 自動変換の確認
    assert result["url"] == "https://example.com/image.jpg"
    assert result["title"] == "Test Image"

    # requests.get が正しい引数で呼ばれたか確認
    args, kwargs = mock_get.call_args
    assert kwargs["params"]["date"] == target_date

@patch("requests.get")
def test_get_nasa_apod_image_failure(mock_get):
    """API呼び出し失敗時のテスト"""
    mock_get.side_effect = Exception("API Error")

    result = _get_nasa_apod_image("2023-01-01")
    assert result is None
