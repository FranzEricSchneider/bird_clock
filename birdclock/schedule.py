"""Timing rules: which hours chime and when the screen wakes. No pygame, so it is easy to test."""


def folder_for_hour(hour):
    """24-hour clock hour -> bird folder name, "01".."12"."""
    return f"{(hour - 1) % 12 + 1:02d}"


def is_quiet(hour, cfg):
    start, end = cfg["quiet_start"], cfg["quiet_end"]
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end


def play_count(sound_seconds, cfg, rng):
    """How many times to play a sound: random within the plays range, capped to fit max_sound_seconds."""
    fits = max(1, int(cfg["max_sound_seconds"] // sound_seconds))
    return min(rng.randint(cfg["plays_min"], cfg["plays_max"]), fits)


def should_chime(prev, now, cfg, input_present):
    """True once, when the clock first reaches the top of an hour.

    Quiet hours chime only while a keyboard is plugged in (and then silently, see Chime).
    """
    if prev.hour == now.hour or now.minute != 0:
        return False
    return input_present or not is_quiet(now.hour, cfg)


def upcoming_chime_hour(now, cfg):
    """The next hour if its chime is within wake_before seconds, else None."""
    seconds_left = 3600 - (now.minute * 60 + now.second)
    next_hour = (now.hour + 1) % 24
    if seconds_left <= cfg["wake_before"] and not is_quiet(next_hour, cfg):
        return next_hour
    return None
