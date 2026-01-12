
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.voidoll_service import VoidollService

@patch("google.cloud.storage.Client")
@patch("vertexai.init")
@patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project", "VOICEVOX_URL": "http://test-voicevox", "GCS_BUCKET_NAME": "test-bucket"})
def test_voidoll_init(mock_vertex_init, mock_storage_client):
    """初期化のテスト"""
    service = VoidollService()
    assert service.use_vertex is True
    assert service.voicevox_url == "http://test-voicevox"
    # Vertex AI init called
    mock_vertex_init.assert_called_once_with(project="test-project", location="us-central1")

@patch("core.voidoll_service.GenerativeModel")
@patch("vertexai.init")
@patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"})
def test_generate_chat_reply(mock_vertex_init, mock_gen_model_cls):
    """チャット生成のテスト"""
    # モックの設定
    mock_model_instance = MagicMock()
    mock_gen_model_cls.return_value = mock_model_instance

    mock_response = MagicMock()
    mock_response.text = "こんにちはだにゃ"
    mock_model_instance.generate_content.return_value = mock_response

    service = VoidollService()
    reply = service.generate_chat_reply("おはよう")

    # アサーション
    assert reply == "こんにちはだにゃ"
    mock_model_instance.generate_content.assert_called_once()

    # プロンプトの内容確認
    call_args = mock_model_instance.generate_content.call_args[0][0]
    assert "ネコ型アンドロイド" in call_args[0] # System prompt
    assert "ユーザーの入力: おはよう" in call_args[1]

@patch("requests.post")
@patch("core.voidoll_service.storage.Client")
@patch("vertexai.init")
@patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project", "VOICEVOX_URL": "http://test-voicevox", "GCS_BUCKET_NAME": "test-bucket"})
def test_generate_voice_url_success(mock_vertex_init, mock_storage_cls, mock_post):
    """音声URL生成の成功テスト"""
    # 1. Audio Query Mock
    mock_resp_query = MagicMock()
    mock_resp_query.status_code = 200
    mock_resp_query.json.return_value = {"query": "data"}

    # 2. Synthesis Mock
    mock_resp_synth = MagicMock()
    mock_resp_synth.status_code = 200
    mock_resp_synth.content = b"audio_data"

    # requests.post の side_effect で順にレスポンスを返す
    mock_post.side_effect = [mock_resp_query, mock_resp_synth]

    # 3. GCS Mock
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.public_url = "https://storage.googleapis.com/test-bucket/voice.wav"

    mock_client_instance = MagicMock()
    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_storage_cls.return_value = mock_client_instance

    service = VoidollService()
    url = service.generate_voice_url("テスト")

    # アサーション
    assert url == "https://storage.googleapis.com/test-bucket/voice.wav"
    assert mock_post.call_count == 2
    mock_blob.upload_from_string.assert_called_once_with(b"audio_data", content_type="audio/wav")

@patch.dict(os.environ, {}, clear=True) # 環境変数を空にする
def test_voidoll_missing_env():
    """環境変数が足りない場合の挙動"""
    with patch("vertexai.init") as mock_init:
        service = VoidollService()
        assert service.use_vertex is False # Project IDがないのでFalse

        reply = service.generate_chat_reply("test")
        assert "システムエラー" in reply

        url = service.generate_voice_url("test")
        assert url is None
