
import sys
import os
import pytest

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.fox import extract_youtube_id

def test_extract_normal_url():
    """通常のYouTube URL"""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert extract_youtube_id(url) == "dQw4w9WgXcQ"

def test_extract_short_url():
    """短縮URL"""
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert extract_youtube_id(url) == "dQw4w9WgXcQ"

def test_extract_url_in_text():
    """文章中のURL"""
    text = "これ面白いよ！ https://youtu.be/abc123XYZ 見てね"
    assert extract_youtube_id(text) == "abc123XYZ"

def test_extract_no_url():
    """URLなし"""
    text = "こんにちは、キツネさん"
    assert extract_youtube_id(text) is None

def test_extract_invalid_input():
    """無効な入力"""
    assert extract_youtube_id("") is None
    assert extract_youtube_id(None) is None
    # 完全に無関係なURL
    assert extract_youtube_id("https://google.com") is None
