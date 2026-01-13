
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, ANY
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent
from linebot.v3.messaging import ButtonsTemplate, CarouselTemplate

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals import penguin
from animals.penguin import parse_email_request, register_penguin_handler, handle_penguin_message, handle_penguin_postback

# ==========================================
# Parsing Logic Tests (Existing)
# ==========================================
def test_parse_valid_email():
    """正常なメールリクエストのパース"""
    text = "メール：boss@example.com\n業務報告\nお疲れ様です。本日の報告です。"
    to, sub, body = parse_email_request(text)

    assert to == "boss@example.com"
    assert sub == "業務報告"
    assert body == "お疲れ様です。本日の報告です。"

def test_parse_invalid_format():
    """行数が足りない場合"""
    text = "メール：boss@example.com\n件名だけ"
    to, sub, body = parse_email_request(text)

    assert to is None
    assert sub is None
    assert body is None

# ==========================================
# Handler Tests
# ==========================================
class TestPenguinHandler(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        self.mock_handler = MagicMock()
        self.mock_config = MagicMock()
        self.mock_text_model = MagicMock()

        # グローバル変数をセットアップ
        register_penguin_handler(self.mock_app, self.mock_handler, self.mock_config, self.mock_text_model)

        # Pending emailsをクリア
        penguin.pending_emails = {}

    @patch('animals.penguin.MessagingApi')
    @patch('animals.penguin.ApiClient')
    def test_handle_email_request_flow(self, mock_client, mock_msg_api):
        """メール作成リクエストのフローテスト"""
        event = MagicMock()
        event.source.user_id = "user123"
        event.reply_token = "token123"
        event.message.text = "メール：test@example.com\n件名\n本文"

        # 実行
        handle_penguin_message(event)

        # 生成された保留データを確認
        assert "user123" in penguin.pending_emails
        assert penguin.pending_emails["user123"]["to"] == "test@example.com"

        # 返信が呼ばれたか (ButtonsTemplateが含まれているか)
        mock_msg_api_instance = mock_msg_api.return_value
        mock_msg_api_instance.reply_message.assert_called_once()
        args = mock_msg_api_instance.reply_message.call_args[0]
        messages = args[0].messages

        # 1つ目はテキスト、2つ目はテンプレートのはず
        assert len(messages) == 2
        assert isinstance(messages[1].template, ButtonsTemplate)

    @patch('animals.penguin.call_gemini_concierge_list')
    @patch('animals.penguin.MessagingApi')
    @patch('animals.penguin.ApiClient')
    def test_handle_concierge_request_flow(self, mock_client, mock_msg_api, mock_gemini):
        """お店検索リクエストのフローテスト"""
        event = MagicMock()
        event.reply_token = "token123"
        event.message.text = "お店：渋谷でランチ"

        # Geminiのモックレスポンス
        mock_gemini.return_value = (
            [
                {"name": "Shop A", "description": "Good shop", "search_keyword": "Shop A Shibuya"},
                {"name": "Shop B", "description": "Nice shop", "search_keyword": "Shop B Shibuya"}
            ],
            "候補を見つけたペン！"
        )

        # 実行
        handle_penguin_message(event)

        # 返信確認 (CarouselTemplateが含まれているか)
        mock_msg_api_instance = mock_msg_api.return_value
        mock_msg_api_instance.reply_message.assert_called_once()
        args = mock_msg_api_instance.reply_message.call_args[0]
        messages = args[0].messages

        assert len(messages) == 2
        assert isinstance(messages[1].template, CarouselTemplate)
        assert len(messages[1].template.columns) == 2

    @patch('animals.penguin.send_email_via_gas')
    @patch('animals.penguin.MessagingApi')
    @patch('animals.penguin.ApiClient')
    def test_handle_postback_send(self, mock_client, mock_msg_api, mock_send_gas):
        """送信ボタン押下時のテスト"""
        user_id = "user123"
        penguin.pending_emails[user_id] = {"to": "a", "subject": "b", "body": "c"}

        event = MagicMock()
        event.source.user_id = user_id
        event.reply_token = "token_postback"
        event.postback.data = "action=send"

        # GAS送信成功モック
        mock_send_gas.return_value = (True, "OK")

        # 実行
        handle_penguin_postback(event)

        # 送信関数が呼ばれたか
        mock_send_gas.assert_called_once_with("a", "b", "c")

        # 保留リストから消えているか
        assert user_id not in penguin.pending_emails

        # 完了メッセージ
        mock_msg_api_instance = mock_msg_api.return_value
        mock_msg_api_instance.reply_message.assert_called_once()
        args = mock_msg_api_instance.reply_message.call_args[0]
        assert "送信完了" in args[0].messages[0].text

    def test_web_api_endpoints(self):
        """Web API のテスト"""
        app = FastAPI()
        # ルーターを登録する必要があるが、penguin.pyではrouter変数が定義されている
        app.include_router(penguin.router)

        client = TestClient(app)

        # 1. Email Mock
        with patch('animals.penguin.call_gemini_email') as mock_email:
            mock_email.return_value = ("Refined Subject", "Refined Body")

            # Text Modelを設定しないとエラーになる箇所の回避のため、ここでもregisterを呼ぶか
            # あるいは _text_model を直接セットする
            penguin._text_model = MagicMock()

            res = client.post("/api/penguin/email", json={"to": "a", "subject": "s", "body": "b"})
            assert res.status_code == 200
            assert res.json()["subject"] == "Refined Subject"

        # 2. Concierge Mock
        with patch('animals.penguin.call_gemini_concierge_list') as mock_list:
            mock_list.return_value = ([], "Intro")

            res = client.post("/api/penguin/concierge", json={"query": "test"})
            assert res.status_code == 200
            assert res.json()["intro"] == "Intro"
