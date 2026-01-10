
import sys
import os
import pytest

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.beaver import parse_delete_indices

def test_parse_single_index():
    """1つの番号指定"""
    # ユーザーは "メモ削除 1" (1番目) -> index 0
    assert parse_delete_indices("メモ削除 1") == [0]

def test_parse_multiple_indices():
    """複数の番号指定 (スペース区切り, カンマ区切り)"""
    # "1 3" -> index 0, 2
    assert parse_delete_indices("メモ削除 1 3") == [0, 2]
    # "1, 2" -> index 0, 1
    assert parse_delete_indices("メモ削除 1, 2") == [0, 1]

def test_parse_invalid_input():
    """無効な入力"""
    # 数字がない
    assert parse_delete_indices("メモ削除 あいう") == []
    # 0以下 (ありえない番号)
    assert parse_delete_indices("メモ削除 0") == [] # 1始まりなので0は除外 or無視

def test_parse_mixed_input():
    """余計な文字が入っている場合"""
    # 数字だけ拾う
    assert parse_delete_indices("メモ削除 1と3") == [0, 2] # "と" が区切り文字になれば[0,2]だが、現状の実装だと "1と3" は数字じゃないので無視されるはず
    # 検証：現在のsplit実装だと空白区切りなので、"1と3"は1つのトークンになり、digitじゃないので無視される
