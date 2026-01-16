
import unittest
from unittest.mock import MagicMock
from animals.bat import (
    process_bat_command,
    _search_tv_schedule_with_gemini,
    _check_schedule_strict
)

class TestBatCoverage(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_search_model = MagicMock()
        self.user_id = "test_user_coverage"

    def test_process_bat_command_add_empty(self):
        """Line 38-39: Empty keyword after '追加:' """
        # Only "追加:" or "追加："
        for cmd in ["追加:", "追加："]:
            reply = process_bat_command(cmd, self.user_id, self.mock_db, self.mock_search_model)
            self.assertIn("追加したい番組名を入れてモリ！", reply)

    def test_process_bat_command_remove_not_found(self):
        """Line 47-48: Removing non-existent keyword"""
        # Mock _remove_from_watch_list to return False
        # We need to mock the helper function inside the module or mock DB behavior
        # Since _remove_from_watch_list uses db, let's mock the DB to return exists=True but keyword not in list

        # However, process_bat_command calls _remove_from_watch_list.
        # Easier to patch the function itself in the context of process_bat_command if we were patching.
        # But here we want to test the full flow or just hit the lines.
        # Let's trust the logic inside process_bat_command calls _remove_from_watch_list.
        # We will assume _remove_from_watch_list is working (tested elsewhere)
        # and focus on mocking its return if we could patch.
        # Without patching, we need to set up DB mock to result in False.

        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"keywords": ["A", "B"]}
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        # Try to remove "C" (not in list)
        reply = process_bat_command("削除: C", self.user_id, self.mock_db, self.mock_search_model)
        self.assertIn("リストになかったモリ", reply)

    def test_process_bat_command_remove_empty(self):
        """Line 49-50: Empty keyword after '削除:'"""
        for cmd in ["削除:", "削除："]:
            reply = process_bat_command(cmd, self.user_id, self.mock_db, self.mock_search_model)
            self.assertIn("削除したい番組名を入れてモリ！", reply)

    def test_process_bat_command_list_empty(self):
        """Line 58-59: Empty list"""
        # Mock empty list return
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"keywords": []}
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        reply = process_bat_command("リスト", self.user_id, self.mock_db, self.mock_search_model)
        self.assertIn("今は何もチェックしてないモリ", reply)

    def test_search_tv_schedule_with_gemini_error(self):
        """Line 300-301: Exception handling"""
        self.mock_search_model.generate_content.side_effect = Exception("API Down")
        reply = _search_tv_schedule_with_gemini("test", self.mock_search_model)
        self.assertIn("電波が悪くて", reply)

    def test_check_schedule_strict_false(self):
        """Line 329-330: False response"""
        self.mock_search_model.generate_content.return_value.text = "false"
        result = _check_schedule_strict("test", "query", self.mock_search_model)
        self.assertIsNone(result)

    def test_check_schedule_strict_error(self):
        """Line 335-337: Exception handling"""
        self.mock_search_model.generate_content.side_effect = Exception("Error")
        result = _check_schedule_strict("test", "query", self.mock_search_model)
        self.assertIsNone(result)
