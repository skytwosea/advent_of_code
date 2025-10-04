import sys
from pathlib import Path
from range_splice import RangeData, HalfRangeData, convert_to_hrd, sort_rd


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


def test_sort_rd_basic_ordering():
    # Simple: unsorted by lower -> sorted ascending by lower
    src = [
        RangeData(5, 10, "a"),
        RangeData(1, 2, "b"),
        RangeData(3, 4, "c"),
    ]
    out = sort_rd(src)

    assert isinstance(out, list)

    # sort_rd should not mutate the input list
    assert [r.lower for r in src] == [5, 1, 3]

    # Sorted strictly by the lower bound
    assert [r.lower for r in out] == [1, 3, 5]
    # Ensure the full objects are in expected order
    assert [(r.lower, r.upper, r.data) for r in out] == [
        (1, 2, "b"),
        (3, 4, "c"),
        (5, 10, "a"),
    ]


def test_sort_rd_complex_mixed_values():
    # Complex: negatives, zero-length, overlaps, gaps, and a very large range
    src = [
        RangeData(100, 200, "big"),
        RangeData(-5, 5, "span"),
        RangeData(50, 60, "mid"),
        RangeData(-10, -1, "neg"),
        RangeData(0, 0, "point"),
        RangeData(7, 7, "point2"),
        RangeData(6, 9, "overlap"),
        RangeData(1_000_000, 1_000_001, "huge"),
    ]
    snapshot = [(r.lower, r.upper, r.data) for r in src]

    out = sort_rd(src)

    # Input must remain unchanged and a new list must be returned
    assert [(r.lower, r.upper, r.data) for r in src] == snapshot
    assert out is not src

    # Sorted order strictly by lower bound
    assert [r.lower for r in out] == [-10, -5, 0, 6, 7, 50, 100, 1_000_000]

    # Ensure we didn't accidentally create new objects; identities should match originals
    original_by_key = {(r.lower, r.data): r for r in src}
    for r in out:
        assert original_by_key[(r.lower, r.data)] is r
