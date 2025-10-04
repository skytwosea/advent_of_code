import sys
from pathlib import Path
from range_splice import RangeData, HalfRangeData, convert_to_hrd


def test_convert_to_hrd_single_range():
    # Simple: single inclusive range -> single half-open range
    src = [RangeData(1, 3, 10)]
    out = convert_to_hrd(src)
    assert isinstance(out, list)
    assert len(out) == 2
    for obj in out:
        assert isinstance(obj, HalfRangeData)
        assert obj.data == 10
        if obj.position == 1:
            assert obj.end == False
        elif obj.position == 3:
            assert obj.end == True


def test_convert_to_hrd_multiple_ranges_mixed():
    # More complex: multiple ranges of varying lengths
    src = [RangeData(0, 1, 10), RangeData(5, 7, 10), RangeData(9, 12, 10)]
    out = convert_to_hrd(src)
    assert isinstance(out, list)
    assert len(out) == len(src) * 2
    assert all(isinstance(item, HalfRangeData) for item in out)
    for obj in out:
        assert obj.data == 10
        if obj.position == 9:
            assert obj.end == False
        if obj.position == 7:
            assert obj.end == True
