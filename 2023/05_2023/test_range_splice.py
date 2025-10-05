from range_splice import (
    RangeData,
    HalfRangeData,
    _rd_to_hrd,
    _sort_rd,
    _sort_hrd,
    _fill_gaps,
    _get_minmax_bounds_rd,
    splice_ranges,
)


def test_get_minmax_bounds_rd_simple():
    # Expect lowest to be the minimum lower, highest to be the maximum upper
    src = [
        RangeData(2, 3, "a"),
        RangeData(0, 1, "b"),
        RangeData(5, 8, "c"),
    ]
    # NOTE: Current implementation of _get_minmax_bounds_rd appears buggy:
    # it constructs namedtuple("lowest", "highest") and then tries to pass two values,
    # which will raise at runtime. This test encodes the intended behavior.
    mm = _get_minmax_bounds_rd(src)
    assert mm.lowest == 0
    assert mm.highest == 8
    assert tuple(mm) == (0, 8)


def test_get_minmax_bounds_rd_complex_overlaps_and_points():
    # Mixed negatives, zero-length ranges, and overlaps
    src = [
        RangeData(5, 5, "p1"),      # zero-length at 5
        RangeData(-10, -5, "neg"),
        RangeData(-3, 0, "span1"),
        RangeData(0, 10, "span2"),
    ]
    # Intended: lowest = -10, highest = 10
    mm = _get_minmax_bounds_rd(src)
    assert mm.lowest == -10
    assert mm.highest == 10
    assert tuple(mm) == (-10, 10)


def test_sort_rd_basic_ordering():
    # Simple: unsorted by lower -> sorted ascending by lower
    src = [
        RangeData(5, 10, "a"),
        RangeData(1, 2, "b"),
        RangeData(3, 4, "c"),
    ]
    out = _sort_rd(src)

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

    out = _sort_rd(src)

    # Input must remain unchanged and a new list must be returned
    assert [(r.lower, r.upper, r.data) for r in src] == snapshot
    assert out is not src

    # Sorted order strictly by lower bound
    assert [r.lower for r in out] == [-10, -5, 0, 6, 7, 50, 100, 1_000_000]

    # Ensure we didn't accidentally create new objects; identities should match originals
    original_by_key = {(r.lower, r.data): r for r in src}
    for r in out:
        assert original_by_key[(r.lower, r.data)] is r


def test_fill_gaps_simple_prefix_and_suffix_gaps():
    # Single range strictly inside [lb, ub] should create:
    # - a leading gap from lb to first.lower
    # - a trailing gap from last.upper to ub
    src = [RangeData(2, 4, "x")]
    snapshot = [(r.lower, r.upper, r.data) for r in src]

    out = _fill_gaps(src, lb=0, ub=10, neutral_attr="")

    # Input must remain unchanged and a new list must be returned
    assert [(r.lower, r.upper, r.data) for r in src] == snapshot
    assert out is not src

    # Expect two gap ranges and the original one; sorted by lower
    assert [(r.lower, r.upper, r.data) for r in out] == [
        (0, 2, ""),   # leading gap uses first.lower
        (2, 4, "x"), # original
        (4, 10, ""),  # trailing gap from last.upper to ub
    ]


def test_fill_gaps_complex_multiple_internal_and_bounds():
    # Mixed ranges with negatives, zero-length, and unsorted input.
    # Should:
    # - add a leading gap from lb to first.lower
    # - add internal gaps where rd.upper < next.lower
    # - add a trailing gap from last.upper to ub
    src = [
        RangeData(5, 7, "a"),
        RangeData(12, 12, "z"),   # zero-length range at 12
        RangeData(-3, 0, "b"),
        RangeData(10, 12, "c"),
    ]
    snapshot = [(r.lower, r.upper, r.data) for r in src]

    lb, ub, neutral = -10, 20, ""
    out = _fill_gaps(src, lb=lb, ub=ub, neutral_attr=neutral)

    # Input must remain unchanged and a new list must be returned
    assert [(r.lower, r.upper, r.data) for r in src] == snapshot
    assert out is not src

    # Expected ranges after filling, sorted by lower (stable for ties at 12)
    expected = [
        (-10, -3, ""),   # leading gap uses first.upper (0)
        (-3, 0, "b"),
        (0, 5, ""),     # internal gap between [-3,0] and [5,7]
        (5, 7, "a"),
        (7, 10, ""),    # internal gap between [5,7] and [10,12]
        (10, 12, "c"),
        (12, 12, "z"),
        (12, 20, ""),   # trailing gap from last.upper to ub
    ]
    assert [(r.lower, r.upper, r.data) for r in out] == expected

    # Verify all gap objects carry the neutral attribute and originals preserved by identity
    originals = {(r.lower, r.upper, r.data): r for r in src}
    for r in out:
        if (r.lower, r.upper, r.data) in originals:
            assert originals[(r.lower, r.upper, r.data)] is r
        else:
            assert r.data == neutral


def test_sort_hrd_basic_ordering():
    # Simple: ordering by position ascending
    src = [
        HalfRangeData(position=5, data="x", end=True),
        HalfRangeData(position=1, data="a", end=False),
        HalfRangeData(position=3, data="b", end=True),
    ]
    snapshot = [(h.position, h.data, h.end) for h in src]

    out = _sort_hrd(src)

    # Should not mutate input and should return new list
    assert [(h.position, h.data, h.end) for h in src] == snapshot
    assert out is not src

    # Sorted strictly by position
    assert [h.position for h in out] == [1, 3, 5]
    # Ensure the full objects are in expected order
    assert [(h.position, h.data, h.end) for h in out] == [
        (1, "a", False),
        (3, "b", True),
        (5, "x", True),
    ]


def test_sort_hrd_complex_tie_break_on_end_flag():
    # Complex: includes ties on position; end=False should come before end=True
    src = [
        HalfRangeData(position=5, data="A_end", end=True),
        HalfRangeData(position=5, data="A_start", end=False),
        HalfRangeData(position=-1, data="B_end", end=True),
        HalfRangeData(position=-1, data="B_start", end=False),
        HalfRangeData(position=0, data="C_end", end=True),
        HalfRangeData(position=0, data="C_start", end=False),
    ]
    snapshot = [(h.position, h.data, h.end) for h in src]

    out = _sort_hrd(src)

    # Input must remain unchanged and a new list must be returned
    assert [(h.position, h.data, h.end) for h in src] == snapshot
    assert out is not src

    # Expected order: by position, then by end flag (False before True)
    expected = [
        (-1, "B_start", False),
        (-1, "B_end", True),
        (0, "C_start", False),
        (0, "C_end", True),
        (5, "A_start", False),
        (5, "A_end", True),
    ]
    assert [(h.position, h.data, h.end) for h in out] == expected

    # Ensure identities are preserved (no new objects created)
    originals = {(h.position, h.data, h.end): h for h in src}
    for h in out:
        assert originals[(h.position, h.data, h.end)] is h


def test_rd_to_hrd_single_range():
    # Simple: single inclusive range -> single half-open range
    src = [RangeData(1, 3, 10)]
    out = _rd_to_hrd(src)
    assert isinstance(out, list)
    assert len(out) == 2
    for obj in out:
        assert isinstance(obj, HalfRangeData)
        assert obj.data == 10
        if obj.position == 1:
            assert obj.end == False
        elif obj.position == 3:
            assert obj.end == True


def test_rd_to_hrd_multiple_ranges_mixed():
    # More complex: multiple ranges of varying lengths
    src = [RangeData(0, 1, 10), RangeData(5, 7, 10), RangeData(9, 12, 10)]
    out = _rd_to_hrd(src)
    assert isinstance(out, list)
    assert len(out) == len(src) * 2
    assert all(isinstance(item, HalfRangeData) for item in out)
    for obj in out:
        assert obj.data == 10
        if obj.position == 9:
            assert obj.end == False
        if obj.position == 7:
            assert obj.end == True


def testsplice_ranges_simple_lists():
    l1 = [RangeData(2, 4, 1)]
    l2 = [RangeData(5, 6, 2)]

    lb = min(r.lower for r in l1 + l2)
    ub = max(r.upper for r in l1 + l2)
    na = 0

    l1_filled = _fill_gaps(l1, lb=lb, ub=ub, neutral_attr=na)
    l2_filled = _fill_gaps(l2, lb=lb, ub=ub, neutral_attr=na)
    expected = _rd_to_hrd(l1_filled + l2_filled)

    out = splice_ranges(l1, l2, 0)
    assert isinstance(out, list)
    # Compare via a projection to simple tuples for robustness
    proj = lambda seq: [(h.position, h.data, h.end) for h in seq]
    assert proj(out) == proj(expected)


def test_prep_and_convert_complex_negatives_zero_length_and_overlaps():
    l1 = [
        RangeData(-2, 1, "A"),
        RangeData(3, 3, "A0"),  # zero-length at 3
    ]
    l2 = [
        RangeData(-5, -3, "B"),
        RangeData(0, 4, "B2"),
    ]

    lb = min(r.lower for r in l1 + l2)
    ub = max(r.upper for r in l1 + l2)
    na = ""
    
    l1_filled = _fill_gaps(l1, lb=lb, ub=ub, neutral_attr=na)
    l2_filled = _fill_gaps(l2, lb=lb, ub=ub, neutral_attr=na)
    expected = _rd_to_hrd(l1_filled + l2_filled)

    out = splice_ranges(l1, l2, "")
    assert isinstance(out, list)
    # Compare via a projection to simple tuples for robustness
    proj = lambda seq: [(h.position, h.data, h.end) for h in seq]
    assert proj(out) == proj(expected)
