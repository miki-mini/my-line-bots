
import sys
import os
import pytest

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.capybara import check_onsen_mode

def test_onsen_mode_positive():
    """温泉モードになるキーワードのテスト"""
    assert check_onsen_mode("あー疲れた") is True
    assert check_onsen_mode("しんどいので休みたい") is True
    assert check_onsen_mode("温泉行きたい") is True
    assert check_onsen_mode("癒やしてほしい") is True

def test_onsen_mode_negative():
    """通常のニュース検索になるケース"""
    assert check_onsen_mode("今日のAIニュース教えて") is False
    assert check_onsen_mode("Pythonの使い方") is False
    assert check_onsen_mode("疲れてないけど温泉は好き") is True # キーワードが含まれるのでTrueになるはず（仕様確認）
    assert check_onsen_mode("元気いっぱい！") is False
