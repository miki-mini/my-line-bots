
import sys
import os
import pytest
from unittest.mock import patch, MagicMock, ANY

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals import frog
from linebot.v3.webhooks import MessageEvent, TextMessageContent, LocationMessageContent, UserSource

# ==========================================
# 1. Helper Function Tests
# ==========================================

from animals.frog import extract_location_from_message, create_google_maps_link, get_place_details_with_api

def test_extract_location():
    """メッセージから場所名を抽出するテスト"""
    assert extract_location_from_message("東京タワーの場所教えて") == "東京タワー"
    assert extract_location_from_message("品川駅への行き方") == "品川駅"
    assert extract_location_from_message("スカイツリーってどこ？") == "スカイツリー"
    assert extract_location_from_message("おすすめのカフェを教えて") == "おすすめのカフェ"
    assert extract_location_from_message("こんにちは") == "こんにちは"

def test_create_google_maps_link_simple():
    """APIなしの簡易リンク生成"""
    link = create_google_maps_link("東京駅", use_api=False)
    assert "query=%E6%9D%B1%E4%BA%AC%E9%A7%85" in link
    assert link.startswith("https://www.google.com/maps/search/")

@patch("animals.frog.get_place_details_with_api")
def test_create_google_maps_link_with_api(mock_get_details):
    """APIを使用したリンク生成（モック）"""
    mock_get_details.return_value = {
        "lat": 35.6812,
        "lng": 139.7671,
        "name": "Tokyo Station"
    }
    link = create_google_maps_link("東京駅", use_api=True)
    assert "query=35.6812,139.7671" in link
    mock_get_details.assert_called_once_with("東京駅")

# ==========================================
# 2. Main Logic & Integration Tests (Mocked)
# ==========================================

@pytest.fixture
def mock_dependencies():
    """共通のモック依存関係"""
    mock_search_model = MagicMock()
    mock_text_model = MagicMock()
    mock_config = MagicMock()
    mock_app = MagicMock()
    mock_handler = MagicMock() # WebhookHandler

    return {
        "app": mock_app,
        "handler": mock_handler,
        "config": mock_config,
        "search_model": mock_search_model,
        "text_model": mock_text_model
    }

def test_register_frog_handler(mock_dependencies):
    """ハンドラー登録のテスト"""
    frog.register_frog_handler(
        mock_dependencies["app"],
        mock_dependencies["handler"],
        mock_dependencies["config"],
        mock_dependencies["search_model"],
        mock_dependencies["text_model"]
    )
    # グローバル変数が設定されたか確認
    assert frog._search_model == mock_dependencies["search_model"]
    assert frog._text_model == mock_dependencies["text_model"]
    # エンドポイント登録確認
    # エンドポイント登録確認
    assert mock_dependencies["app"].post.call_count >= 1 # /callback_frog, /trigger_morning_weather

@patch("animals.frog.send_reply")
@patch("animals.frog.get_place_details_with_api")
def test_handle_text_message_flow(mock_get_place, mock_send_reply, mock_dependencies):
    """テキストメッセージ受信時のフローテスト"""
    # 1. Initialize handler
    frog.register_frog_handler(
        mock_dependencies["app"],
        mock_dependencies["handler"],
        mock_dependencies["config"],
        mock_dependencies["search_model"],
        mock_dependencies["text_model"]
    )

    # 2. Mock Gemini Response
    mock_response = MagicMock()
    mock_response.text = "明日は晴れだケロ🐸"
    mock_dependencies["search_model"].generate_content.return_value = mock_response

    # 3. Test logic
    msg = frog.handle_text_message("明日の天気", mock_dependencies["search_model"], mock_dependencies["text_model"])

    assert "明日は晴れだケロ" in msg
    mock_dependencies["search_model"].generate_content.assert_called_once()

@patch("animals.frog.get_place_details_with_api")
def test_handle_location_logic(mock_get_place, mock_dependencies):
    """位置情報ロジックのテスト"""
    # Mock search model
    mock_resp = MagicMock()
    mock_resp.text = "現在地の天気は雨だケロ☔"
    mock_dependencies["search_model"].generate_content.return_value = mock_resp

    # Mock Reverse Geo (patched where used)
    with patch("animals.frog.get_location_name_from_coords") as mock_reverse_geo:
        mock_reverse_geo.return_value = "東京都千代田区"

        msg = frog.handle_location_message(
            35.68, 139.76, "東京駅", "場所",
            mock_dependencies["search_model"],
            mock_dependencies["text_model"]
        )

        assert msg == "現在地の天気は雨だケロ☔"
        assert "東京都千代田区" in mock_dependencies["search_model"].generate_content.call_args[0][0]

@patch("animals.frog.ApiClient")
@patch("animals.frog.MessagingApi")
@patch("animals.frog.datetime")
def test_broadcast_morning_weather(mock_datetime, mock_msg_api_cls, mock_api_client_cls, mock_dependencies):
    """朝の天気配信のテスト（抽出した関数を使用）"""

    # Mock time
    mock_now = MagicMock()
    mock_now.strftime.return_value = "2024年1月1日"
    mock_datetime.now.return_value = mock_now

    # Mock Gemini
    mock_resp = MagicMock()
    mock_resp.text = "おはようケロ！"
    mock_dependencies["search_model"].generate_content.return_value = mock_resp

    # Mock Line Broadcast
    mock_line_api = MagicMock()
    mock_msg_api_cls.return_value = mock_line_api

    # Execute
    res = frog.broadcast_morning_weather(mock_dependencies["search_model"], mock_dependencies["config"])

    assert res["status"] == "ok"
    mock_line_api.broadcast.assert_called_once()

    # Verify prompt content
    call_args = mock_dependencies["search_model"].generate_content.call_args[0][0]
    assert "2024年1月1日" in call_args

# ==========================================
# 3. Real Helper Execution Tests (Mocking requests)
# ==========================================

@patch("animals.frog.requests.get")
@patch.dict(os.environ, {"GMAPS_API_KEY": "test_key"})
def test_get_place_details_real(mock_get):
    """Google Places API呼び出しの実際のロジックをテスト"""
    # Mock successful response
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "status": "OK",
        "candidates": [{
            "name": "Tokyo Station",
            "formatted_address": "Tokyo",
            "geometry": {"location": {"lat": 35.0, "lng": 139.0}},
            "place_id": "123",
            "rating": 4.5,
            "user_ratings_total": 100
        }]
    }
    mock_get.return_value = mock_resp

    res = frog.get_place_details_with_api("東京駅")
    assert res["name"] == "Tokyo Station"
    assert res["lat"] == 35.0

@patch("animals.frog.requests.get")
@patch.dict(os.environ, {"GMAPS_API_KEY": "test_key"})
def test_get_location_name_from_coords_real(mock_get):
    """Reverse Geocoding呼び出しの実際のロジックをテスト"""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "status": "OK",
        "results": [{
            "address_components": [{"long_name": "Minato City", "types": ["locality"]}],
            "formatted_address": "Minato City, Tokyo"
        }]
    }
    mock_get.return_value = mock_resp

    name = frog.get_location_name_from_coords(35.0, 139.0)
    assert name == "Minato City"

# ==========================================
# 4. Webhook Entry Point Tests
# ==========================================

from fastapi import FastAPI
from fastapi.testclient import TestClient

def test_callback_frog_integration(mock_dependencies):
    """FastAPI TestClientを使った統合テスト"""
    real_app = FastAPI()

    # Mock handler.handle to avoid real signature check issue or mock signature
    mock_dependencies["handler"].handle = MagicMock()

    frog.register_frog_handler(
        real_app,
        mock_dependencies["handler"],
        mock_dependencies["config"],
        mock_dependencies["search_model"],
        mock_dependencies["text_model"]
    )

    client = TestClient(real_app)

    # Valid flow mock
    headers = {"X-Line-Signature": "dummy"}
    mock_dependencies["handler"].handle.return_value = None

    res = client.post("/callback_frog", content=b"{}", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    mock_dependencies["handler"].handle.assert_called_once()

# ==========================================
# 5. Top-Level Event Handler Tests (Refactored)
# ==========================================

@patch("animals.frog.send_reply")
@patch("animals.frog.handle_text_message")
def test_handle_frog_message_event(mock_handle_text, mock_send_reply, mock_dependencies):
    """テキストイベントハンドラーの直接テスト"""
    # Setup globals
    frog.register_frog_handler(
        mock_dependencies["app"],
        mock_dependencies["handler"],
        mock_dependencies["config"],
        mock_dependencies["search_model"],
        mock_dependencies["text_model"]
    )

    # Mock Event
    mock_event = MagicMock()
    mock_event.message.text = "こんにちは"
    mock_event.reply_token = "token"
    mock_event.source.user_id = "user123"

    mock_handle_text.return_value = "返信"

    # Execute
    frog.handle_frog_message_event(mock_event)

    # Construct expected call. Globals are set.
    mock_handle_text.assert_called_once_with("こんにちは", mock_dependencies["search_model"], mock_dependencies["text_model"])
    mock_send_reply.assert_called_once_with("token", "返信", mock_dependencies["config"])

@patch("animals.frog.send_reply")
@patch("animals.frog.handle_location_message")
def test_handle_frog_location_event(mock_handle_loc, mock_send_reply, mock_dependencies):
    """位置情報イベントハンドラーの直接テスト"""
    # Setup globals
    frog.register_frog_handler(
        mock_dependencies["app"],
        mock_dependencies["handler"],
        mock_dependencies["config"],
        mock_dependencies["search_model"],
        mock_dependencies["text_model"]
    )

    # Mock Event
    mock_event = MagicMock()
    mock_event.message.title = "Place"
    mock_event.message.address = "Addr"
    mock_event.message.latitude = 35.0
    mock_event.message.longitude = 139.0
    mock_event.reply_token = "token"

    mock_handle_loc.return_value = "返信"

    # Execute
    frog.handle_frog_location_event(mock_event)

    # Verify
    mock_handle_loc.assert_called_once()
    mock_send_reply.assert_called_once_with("token", "返信", mock_dependencies["config"])
