
import pytest
import sys
import os

# プロジェクトルートをパスに追加してインポートできるようにする
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.rabbit import get_rabbit_reply

def test_rabbit_default_reply():
    """デフォルトの返信を確認"""
    reply = get_rabbit_reply("こんにちは")
    assert reply == "うさぎは月で餅をついています...🐇🌕"

def test_rabbit_morning_reply():
    """おはようメッセージへの返信を確認"""
    reply = get_rabbit_reply("おはよう")
    assert reply == "おはよう！今日もキラキラ光る月のかけらを集めよう✨"

def test_rabbit_morning_reply_contained():
    """文章に完了が含まれる場合の返信を確認"""
    reply = get_rabbit_reply("皆さんおはようございます")
    assert reply == "おはよう！今日もキラキラ光る月のかけらを集めよう✨"
