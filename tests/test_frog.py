
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.frog import extract_location_from_message, create_google_maps_link, get_place_details_with_api

def test_extract_location():
    """メッセージから場所名を抽出するテスト"""
    # パターン1: 〜の場所
    assert extract_location_from_message("東京タワーの場所教えて") == "東京タワー"
    # パターン2: 〜への行き方
    assert extract_location_from_message("品川駅への行き方") == "品川駅"
    # パターン3: 〜ってどこ
    assert extract_location_from_message("スカイツリーってどこ？") == "スカイツリー"
    # パターン4: 単純な「教えて」
    assert extract_location_from_message("おすすめのカフェを教えて") == "おすすめのカフェ"

    # 抽出できないパターン（そのまま返す仕様）
    assert extract_location_from_message("こんにちは") == "こんにちは"

def test_create_google_maps_link_simple():
    """APIなしの簡易リンク生成"""
    link = create_google_maps_link("東京駅", use_api=False)
    # URLエンコードされているか確認
    assert "query=%E6%9D%B1%E4%BA%AC%E9%A7%85" in link # 東京駅
    assert link.startswith("https://www.google.com/maps/search/")

@patch("animals.frog.get_place_details_with_api")
def test_create_google_maps_link_with_api(mock_get_details):
    """APIを使用したリンク生成（モック）"""
    # モックの戻り値設定
    mock_get_details.return_value = {
        "lat": 35.6812,
        "lng": 139.7671,
        "name": "Tokyo Station"
    }

    link = create_google_maps_link("東京駅", use_api=True)

    # 座標が含まれているか確認
    assert "query=35.6812,139.7671" in link
    # モックが呼ばれたか
    mock_get_details.assert_called_once_with("東京駅")
