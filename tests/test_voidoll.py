
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, ANY
from fastapi import FastAPI
from fastapi.testclient import TestClient

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals import voidoll
from linebot.v3.webhooks import MessageEvent, TextMessageContent, AudioMessageContent
from linebot.v3.messaging import TextMessage

class TestVoidoll(unittest.TestCase):

    def setUp(self):
        # 依存関係のモック
        self.mock_app = MagicMock(spec=FastAPI)
        self.mock_handler = MagicMock()
        self.mock_config = MagicMock()

        # FastAPIアプリ（統合テスト用）
        self.app = FastAPI()

    def test_register_voidoll_handler(self):
        """ハンドラー登録とグローバル変数の設定確認"""
        voidoll.register_voidoll_handler(
            self.mock_app,
            self.mock_handler,
            self.mock_config,
            self.mock_config # text_model mockup
        )

        # グローバル変数が設定されたか
        assert voidoll._configuration_voidoll == self.mock_config

        # ハンドラーが登録されたか（音声・テキスト）
        # handler.add(...) はデコレータとして機能するため、add(...) が呼ばれたか確認
        assert self.mock_handler.add.call_count >= 2

    @patch('animals.voidoll.voidoll_service.generate_chat_reply')
    @patch('animals.voidoll.ApiClient')
    @patch('animals.voidoll.MessagingApi')
    def test_handle_voidoll_text(self, mock_msg_api, mock_api_client, mock_gen_reply):
        """テキストメッセージ処理のテスト"""
        # セットアップ
        voidoll.register_voidoll_handler(self.mock_app, self.mock_handler, self.mock_config, self.mock_config)

        # イベント作成
        mock_event = MagicMock() # spec removed
        mock_event.message.text = "こんにちは"
        mock_event.reply_token = "reply_token_123"

        # 振る舞い定義
        mock_gen_reply.return_value = "こんにちはだにゃ"

        # 実行
        voidoll.handle_voidoll_text(mock_event)

        # アサーション
        mock_gen_reply.assert_called_once_with("こんにちは")

        # API呼び出し確認
        mock_msg_api_instance = mock_msg_api.return_value
        mock_msg_api_instance.reply_message.assert_called_once()
        args = mock_msg_api_instance.reply_message.call_args[0]
        # 引数の中身確認
        assert args[0].reply_token == "reply_token_123"
        assert args[0].messages[0].text == "こんにちはだにゃ"

    @patch('animals.voidoll.voidoll_service.generate_voice_url')
    @patch('google.generativeai.GenerativeModel') # ローカルのimportもmock可能
    @patch('animals.voidoll.MessagingApiBlob')
    @patch('animals.voidoll.ApiClient')
    @patch('animals.voidoll.MessagingApi')
    def test_handle_voidoll_audio(self, mock_msg_api, mock_api_client, mock_blob_api, mock_gen_model, mock_gen_voice):
        """音声メッセージ処理のテスト"""
        # セットアップ
        voidoll.register_voidoll_handler(self.mock_app, self.mock_handler, self.mock_config, self.mock_config)

        # イベント
        mock_event = MagicMock() # spec removed
        mock_event.message.id = "msg_id_456"
        mock_event.reply_token = "reply_token_456"

        # Mock Gemini
        mock_model_instance = MagicMock()
        mock_gen_model.return_value = mock_model_instance
        mock_model_instance.generate_content.return_value.text = "音声返答だにゃ"

        # Mock Voice URL
        mock_gen_voice.return_value = "https://example.com/voice.wav"

        # Mock Blob (Content)
        mock_blob_api.return_value.get_message_content.return_value = b"fake_audio_content"

        # 実行
        voidoll.handle_voidoll_audio(mock_event)

        # Gemini呼び出し確認
        mock_gen_model.assert_called_with("gemini-2.5-flash") # 内部で呼ばれているか
        mock_model_instance.generate_content.assert_called_once()

        # VoiceVoxサービス呼び出し確認
        mock_gen_voice.assert_called_once_with("音声返答だにゃ")

        # 返信確認 (音声メッセージになっているか)
        mock_msg_api.return_value.reply_message.assert_called_once()
        sent_req = mock_msg_api.return_value.reply_message.call_args[0][0]

        # ちゃんとAudioMessageで返しているか
        assert sent_req.messages[0].type == "audio"
        assert sent_req.messages[0].original_content_url == "https://example.com/voice.wav"

    def test_web_api_endpoint(self):
        """Web API エンドポイント /api/voidoll/chat のテスト"""
        # Setup
        # テスト用に一時的にアプリ登録
        # グローバル変数依存があるため、registerを呼んでおく
        voidoll.register_voidoll_handler(self.app, self.mock_handler, self.mock_config, self.mock_config)

        client = TestClient(self.app)

        with patch('animals.voidoll.voidoll_service.generate_chat_reply') as mock_reply:
            with patch('animals.voidoll.voidoll_service.generate_voice_url') as mock_voice:

                mock_reply.return_value = "Webからの返信だにゃ"
                mock_voice.return_value = "http://voice/url"

                response = client.post("/api/voidoll/chat", json={"text": "hello"})

                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
                assert data["message"] == "Webからの返信だにゃ"
                assert data["audio_url"] == "http://voice/url"

    @patch('animals.voidoll.voidoll_service.generate_voice_url')
    @patch('google.generativeai.GenerativeModel')
    @patch('animals.voidoll.MessagingApiBlob')
    @patch('animals.voidoll.ApiClient')
    @patch('animals.voidoll.MessagingApi')
    def test_handle_voidoll_audio_fallback_to_text(self, mock_msg_api, mock_api_client, mock_blob_api, mock_gen_model, mock_gen_voice):
        """音声生成失敗時にテキストで返信するテスト"""
        # セットアップ
        voidoll.register_voidoll_handler(self.mock_app, self.mock_handler, self.mock_config, self.mock_config)

        # イベント
        mock_event = MagicMock()
        mock_event.message.id = "msg_id_fail"
        mock_event.reply_token = "reply_token_fail"

        # Mock Gemini
        mock_model_instance = MagicMock()
        mock_gen_model.return_value = mock_model_instance
        mock_model_instance.generate_content.return_value.text = "返信テキストだにゃ"

        # Mock Voice URL (Noneを返す = 失敗)
        mock_gen_voice.return_value = None

        # Mock Blob
        mock_blob_api.return_value.get_message_content.return_value = b"audio"

        # 実行
        voidoll.handle_voidoll_audio(mock_event)

        # 検証
        if mock_msg_api.return_value.reply_message.call_count == 0:
            print("[DEBUG] reply_message NOT CALLED")
        else:
            args = mock_msg_api.return_value.reply_message.call_args[0][0]
            print(f"[DEBUG] Sent Message Type: {type(args.messages[0])}")
            if isinstance(args.messages[0], TextMessage):
                print(f"[DEBUG] Sent Text: {args.messages[0].text}")

        mock_msg_api.return_value.reply_message.assert_called_once()
        sent_req = mock_msg_api.return_value.reply_message.call_args[0][0]

        # テキストメッセージになっているか確認
        assert len(sent_req.messages) == 1
        assert isinstance(sent_req.messages[0], TextMessage)
        assert sent_req.messages[0].text == "返信テキストだにゃ"

    def test_callback_invalid_signature(self):
        """Webhook署名エラーのテスト"""
        # ハンドラーのhandleメソッドがInvalidSignatureErrorを投げるようにモック
        self.mock_handler.handle.side_effect = voidoll.InvalidSignatureError("Invalid signature")

        voidoll.register_voidoll_handler(self.app, self.mock_handler, self.mock_config, self.mock_config)
        client = TestClient(self.app)

        # 実行
        response = client.post(
            "/callback_voidoll",
            headers={"X-Line-Signature": "invalid_sig"},
            content=b"body"
        )

        # 400エラーになるか
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"

    def test_callback_general_error(self):
        """Webhook一般エラーのテスト"""
        # ハンドラーが一般例外を投げる
        self.mock_handler.handle.side_effect = Exception("General Error")

        voidoll.register_voidoll_handler(self.app, self.mock_handler, self.mock_config, self.mock_config)
        client = TestClient(self.app)

        # 実行
        response = client.post(
            "/callback_voidoll",
            headers={"X-Line-Signature": "valid_sig"},
            content=b"body"
        )

        # 500エラーになるか
        assert response.status_code == 500
        assert "General Error" in response.json()["detail"]
