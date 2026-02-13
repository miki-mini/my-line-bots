"""
test_rate_limiter.py - 使用回数制限ユーティリティのテスト
"""

from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone

import pytest

# conftest.py がGCPモジュールをモックしているので、その後にインポート
from core.rate_limiter import (
    check_and_increment,
    check_and_increment_by_ip,
    get_user_id_from_request,
    DAILY_LIMIT,
    LIMIT_MESSAGES,
    COLLECTION_NAME,
)


class TestCheckAndIncrement:
    """check_and_increment のテスト"""

    def test_first_usage_allowed(self):
        """初回利用は許可される"""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        allowed, msg = check_and_increment(mock_db, "user1", "fox")

        assert allowed is True
        assert msg is None
        mock_db.collection.return_value.document.return_value.set.assert_called_once()

    def test_under_limit_allowed(self):
        """制限未満なら許可される"""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"count": 5}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        allowed, msg = check_and_increment(mock_db, "user1", "fox")

        assert allowed is True
        assert msg is None

    def test_at_limit_denied(self):
        """制限到達で拒否される"""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"count": 10}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        allowed, msg = check_and_increment(mock_db, "user1", "fox")

        assert allowed is False
        assert msg == LIMIT_MESSAGES["fox"]

    def test_over_limit_denied(self):
        """制限超過で拒否される"""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"count": 15}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        allowed, msg = check_and_increment(mock_db, "user1", "bat")

        assert allowed is False
        assert msg == LIMIT_MESSAGES["bat"]

    def test_db_none_fail_open(self):
        """db=Noneの場合はfail open"""
        allowed, msg = check_and_increment(None, "user1", "fox")

        assert allowed is True
        assert msg is None

    def test_firestore_error_fail_open(self):
        """Firestoreエラー時はfail open"""
        mock_db = MagicMock()
        mock_db.collection.return_value.document.return_value.get.side_effect = Exception("Firestore down")

        allowed, msg = check_and_increment(mock_db, "user1", "fox")

        assert allowed is True
        assert msg is None

    def test_different_bots_independent(self):
        """ボット間のカウントは独立"""
        mock_db = MagicMock()

        # foxは10回到達
        mock_doc_fox = MagicMock()
        mock_doc_fox.exists = True
        mock_doc_fox.to_dict.return_value = {"count": 10}

        # batはまだ0回
        mock_doc_bat = MagicMock()
        mock_doc_bat.exists = False

        def side_effect(doc_id):
            mock_ref = MagicMock()
            if "fox" in doc_id:
                mock_ref.get.return_value = mock_doc_fox
            else:
                mock_ref.get.return_value = mock_doc_bat
            return mock_ref

        mock_db.collection.return_value.document = side_effect

        # foxは拒否
        allowed_fox, _ = check_and_increment(mock_db, "user1", "fox")
        assert allowed_fox is False

        # batは許可
        allowed_bat, _ = check_and_increment(mock_db, "user1", "bat")
        assert allowed_bat is True

    def test_document_id_contains_date(self):
        """ドキュメントIDに日付が含まれる（日次リセット）"""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        check_and_increment(mock_db, "user1", "fox")

        # document()に渡されたIDを取得
        call_args = mock_db.collection.return_value.document.call_args[0][0]
        assert "user1" in call_args
        assert "fox" in call_args
        # 日付のフォーマットチェック（YYYY-MM-DD）
        import re
        assert re.search(r"\d{4}-\d{2}-\d{2}", call_args)

    def test_uses_usage_limits_collection(self):
        """usage_limitsコレクションを使用する"""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        check_and_increment(mock_db, "user1", "fox")

        mock_db.collection.assert_called_with(COLLECTION_NAME)

    def test_unknown_bot_uses_default_message(self):
        """未知のボット名でもデフォルトメッセージで拒否"""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"count": 10}
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        allowed, msg = check_and_increment(mock_db, "user1", "unknown_bot")

        assert allowed is False
        assert "利用上限" in msg


class TestGetUserIdFromRequest:
    """get_user_id_from_request のテスト"""

    def test_ip_from_client_host(self):
        """client.hostからIPを取得"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.client.host = "192.168.1.1"

        result = get_user_id_from_request(mock_request)

        assert result.startswith("ip_")
        assert len(result) > 3

    def test_ip_from_x_forwarded_for(self):
        """X-Forwarded-ForヘッダーからIPを取得"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "10.0.0.1, 10.0.0.2"

        result = get_user_id_from_request(mock_request)

        assert result.startswith("ip_")

    def test_same_ip_same_id(self):
        """同じIPなら同じIDを返す"""
        mock_req1 = MagicMock()
        mock_req1.headers.get.return_value = None
        mock_req1.client.host = "1.2.3.4"

        mock_req2 = MagicMock()
        mock_req2.headers.get.return_value = None
        mock_req2.client.host = "1.2.3.4"

        assert get_user_id_from_request(mock_req1) == get_user_id_from_request(mock_req2)

    def test_different_ip_different_id(self):
        """異なるIPなら異なるIDを返す"""
        mock_req1 = MagicMock()
        mock_req1.headers.get.return_value = None
        mock_req1.client.host = "1.2.3.4"

        mock_req2 = MagicMock()
        mock_req2.headers.get.return_value = None
        mock_req2.client.host = "5.6.7.8"

        assert get_user_id_from_request(mock_req1) != get_user_id_from_request(mock_req2)


class TestCheckAndIncrementByIp:
    """check_and_increment_by_ip のテスト"""

    def test_delegates_to_check_and_increment(self):
        """check_and_incrementに委譲する"""
        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.client.host = "1.2.3.4"

        allowed, msg = check_and_increment_by_ip(mock_db, mock_request, "owl")

        assert allowed is True
        assert msg is None


class TestLimitMessages:
    """全ボットのメッセージが存在するか確認"""

    @pytest.mark.parametrize("bot_name", [
        "fox", "frog", "mole", "capybara", "bat", "beaver",
        "penguin", "voidoll", "whale", "owl", "raccoon",
        "butsubutsu", "alpaca", "butterfly", "flamingo",
    ])
    def test_all_bots_have_messages(self, bot_name):
        """全対象ボットにメッセージが設定されている"""
        assert bot_name in LIMIT_MESSAGES
        assert len(LIMIT_MESSAGES[bot_name]) > 0

    def test_daily_limit_is_10(self):
        """デイリー制限が10であること"""
        assert DAILY_LIMIT == 10
