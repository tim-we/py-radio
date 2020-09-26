class HourRange():
    def __init__(self, start: int, end: int):
        if start == end:
            raise ValueError("Start and end may not be equal.")
        if start < 0 or 23 < start:
            raise ValueError("Invalid start value: " + str(start))
        if end < 0 or 23 < end:
            raise ValueError("Invalid end value: " + str(end))

        if start < end:
            self._offset = 0
            self._start = start
            self._end = end
        else:
            self._offset = 24 - start
            self._start = 0
            self._end = end + self._offset
            assert self._end < 24

    def is_in(self, hour: int) -> bool:
        if hour < 0 or 23 < hour:
            raise ValueError("Invalid value for hour: " + str(hour))
        h = (hour + self._offset) % 24
        assert 0 <= h and h < 24
        return self._start <= h and h <= self._end
