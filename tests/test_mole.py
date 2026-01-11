
import sys
import os
import pytest

# パスを通す
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animals.mole import filter_upcoming_trains

def test_filter_upcoming():
    """未来の電車だけフィルタリングしてソートするか"""
    current_time = "10:00"

    # モックデータ: APIのレスポンス構造を簡略化して模倣
    mock_timetables = [
        {
            "odpt:railwayDirection": "odpt.RailDirection:Outbound",
            "odpt:stationTimetableObject": [
                {"odpt:departureTime": "09:50", "odpt:destinationStation": ["odpt.Station:Test.A"]}, # 過去
                {"odpt:departureTime": "10:05", "odpt:destinationStation": ["odpt.Station:Test.B"]}, # 未来 (1)
                {"odpt:departureTime": "10:15", "odpt:destinationStation": ["odpt.Station:Test.C"]}, # 未来 (2)
            ]
        },
        {
            # 別の方面（混ぜてソートされるか確認）
            "odpt:railwayDirection": "odpt.RailDirection:Inbound",
            "odpt:stationTimetableObject": [
                {"odpt:departureTime": "10:10", "odpt:destinationStation": ["odpt.Station:Test.D"]}, # 未来 (間に入る)
            ]
        }
    ]

    result = filter_upcoming_trains(mock_timetables, current_time)

    # 期待される順序: 10:05 -> 10:10 -> 10:15
    assert len(result) == 3
    assert result[0]["time"] == "10:05"
    assert result[0]["dest"] == "B"

    assert result[1]["time"] == "10:10"
    assert result[1]["dest"] == "D"

    assert result[2]["time"] == "10:15"
    assert result[2]["dest"] == "C"

def test_filter_no_upcoming():
    """未来の電車がない場合"""
    current_time = "23:55"
    mock_timetables = [
        {
            "odpt:stationTimetableObject": [
                {"odpt:departureTime": "23:50"},
            ]
        }
    ]
    result = filter_upcoming_trains(mock_timetables, current_time)
    assert result == []

def test_filter_exact_match():
    """時刻が同時刻の場合（仕様によるが、 > なので含まれないはず）"""
    current_time = "10:00"
    mock_timetables = [
        {
            "odpt:stationTimetableObject": [
                {"odpt:departureTime": "10:00"},
            ]
        }
    ]
    result = filter_upcoming_trains(mock_timetables, current_time)
    # 現在の実装は > current_time なので含まれない
    assert result == []
