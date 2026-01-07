
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.bat import process_bat_command

class TestBat(unittest.TestCase):

    def setUp(self):
        # 共通のモック作成
        self.mock_db = MagicMock()
        self.mock_search_model = MagicMock()
        self.user_id = "test_user_001"

    @patch('animals.bat._add_to_watch_list')
    def test_add_command(self, mock_add):
        """「追加:」コマンドが正しく動くか"""
        text = "追加: ポケモン"
        reply = process_bat_command(text, self.user_id, self.mock_db, self.mock_search_model)

        # 関数が呼ばれたかチェック
        mock_add.assert_called_once_with(self.mock_db, self.user_id, "ポケモン")
        # 返信文言のチェック
        self.assertIn("監視リストに入れたモリ！", reply)
        self.assertIn("ポケモン", reply)

    @patch('animals.bat._add_to_watch_list')
    def test_add_command_empty(self, mock_add):
        """「追加:」だけで中身がない場合"""
        text = "追加:"
        reply = process_bat_command(text, self.user_id, self.mock_db, self.mock_search_model)

        mock_add.assert_not_called()
        self.assertIn("追加したい番組名を入れてモリ！", reply)

    @patch('animals.bat._get_user_watch_list')
    def test_list_command(self, mock_get_list):
        """「リスト」コマンドのテスト"""
        # DBから帰ってくる値を偽装
        mock_get_list.return_value = ["ポケモン", "ニュース"]

        text = "リスト"
        reply = process_bat_command(text, self.user_id, self.mock_db, self.mock_search_model)

        self.assertIn("ポケモン", reply)
        self.assertIn("ニュース", reply)

    @patch('animals.bat._search_tv_schedule_with_gemini')
    def test_normal_search(self, mock_search):
        """普通の会話はGemini検索に回されるか"""
        text = "今夜の面白い番組教えて"
        process_bat_command(text, self.user_id, self.mock_db, self.mock_search_model)

        # 検索関数が呼ばれたはず
        mock_search.assert_called_once()
