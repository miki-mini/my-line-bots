
import sys
import os
import pytest

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.penguin import parse_email_request

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

def test_parse_multiline_body():
    """本文が複数行ある場合"""
    text = "メール：abc@example.com\n挨拶\nこんにちは。\n元気ですか？\nまたね。"
    to, sub, body = parse_email_request(text)

    assert to == "abc@example.com"
    assert sub == "挨拶"
    assert body == "こんにちは。\n元気ですか？\nまたね。"
