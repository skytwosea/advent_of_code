import sys
from pathlib import Path

# Allow importing from the AoC 2023/05_2023 folder without making a package.
sys.path.insert(0, str(Path(__file__).resolve().parent / "2023" / "05_2023"))

try:
    # Preferred snake_case module name (as per prompt)
    from range_splice import RangeData, HalfRangeData, convert_to_hrd
except ModuleNotFoundError:
    # Fallback to the CamelCase file mentioned
    from RangeSplice import RangeData, HalfRangeData, convert_to_hrd


def test_convert_to_hrd_single_range():
    # Simple: single inclusive range -> single half-open range
    src = [RangeData(1, 3)]
    out = convert_to_hrd(src)
    assert isinstance(out, list)
    assert len(out) == 1
    assert isinstance(out[0], HalfRangeData)


def test_convert_to_hrd_multiple_ranges_mixed():
    # More complex: multiple ranges of varying lengths
    src = [RangeData(0, 0), RangeData(5, 7), RangeData(9, 12)]
    out = convert_to_hrd(src)
    assert isinstance(out, list)
    assert len(out) == len(src)
    assert all(isinstance(item, HalfRangeData) for item in out)
