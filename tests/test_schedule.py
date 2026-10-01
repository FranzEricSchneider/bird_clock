import random
from datetime import datetime

from birdclock.schedule import folder_for_hour, is_quiet, play_count, should_chime, upcoming_chime_hour

CFG = {"quiet_start": 21, "quiet_end": 7, "wake_before": 60}


def at(hour, minute=0, second=0):
    return datetime(2026, 1, 1, hour, minute, second)


def test_folder_for_hour():
    assert folder_for_hour(0) == "12"
    assert folder_for_hour(1) == "01"
    assert folder_for_hour(12) == "12"
    assert folder_for_hour(13) == "01"
    assert folder_for_hour(23) == "11"


def test_quiet_hours_across_midnight():
    assert [h for h in range(24) if is_quiet(h, CFG)] == [0, 1, 2, 3, 4, 5, 6, 21, 22, 23]


def test_quiet_hours_same_day():
    assert [h for h in range(24) if is_quiet(h, {"quiet_start": 1, "quiet_end": 3})] == [1, 2]


def test_quiet_hours_disabled():
    assert not any(is_quiet(h, {"quiet_start": 5, "quiet_end": 5}) for h in range(24))


def test_chimes_once_at_top_of_hour():
    assert should_chime(at(7, 59, 59), at(8), CFG, False)
    assert not should_chime(at(8), at(8, 0, 1), CFG, False)


def test_no_chime_in_quiet_hours():
    assert not should_chime(at(21, 59, 59), at(22), CFG, False)
    assert should_chime(at(6, 59, 59), at(7), CFG, False)


def test_quiet_hours_chime_with_keyboard():
    assert should_chime(at(21, 59, 59), at(22), CFG, True)
    assert not should_chime(at(22), at(22, 0, 1), CFG, True)


def test_no_chime_when_clock_is_set_mid_hour():
    assert not should_chime(at(8, 10), at(14, 37), CFG, False)
    assert not should_chime(at(8, 10), at(14, 37), CFG, True)


def test_play_count_capped_by_length():
    cfg = {"plays_min": 1, "plays_max": 3, "max_sound_seconds": 30}
    rng = random.Random(0)
    assert {play_count(5, cfg, rng) for _ in range(100)} == {1, 2, 3}
    assert {play_count(12, cfg, rng) for _ in range(100)} == {1, 2}
    assert {play_count(45, cfg, rng) for _ in range(100)} == {1}  # long clips still play once


def test_upcoming_chime():
    assert upcoming_chime_hour(at(7, 58, 59), CFG) is None
    assert upcoming_chime_hour(at(7, 59), CFG) == 8
    assert upcoming_chime_hour(at(20, 59, 30), CFG) is None  # 21:00 is quiet
