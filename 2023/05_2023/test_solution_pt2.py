from solution_pt2 import (
    Span,
    _assess_overlap,
    _assess_containment,
    _purge_non_overlapping_ranges,
    _trim_overhangs,
    _fill_gaps,
    _apply_adjustments,
    _consolidate_maps,
)

def test_assess_overlap():
    core = Span(10,20,0)
    
    candidate_a = Span(0,5,0)
    assert not _assess_overlap(core, candidate_a)
    
    candidate_b = Span(5,10,0)
    assert not _assess_overlap(core, candidate_b)
    
    candidate_c = Span(5,12,0)
    assert _assess_overlap(core, candidate_c)

    candidate_d = Span(5,25,0)
    assert _assess_overlap(core, candidate_d)

    candidate_e = Span(10,20,0)
    assert _assess_overlap(core, candidate_e)

    candidate_f = Span(15,20,0)
    assert _assess_overlap(core, candidate_f)

    candidate_g = Span(15,18,0)
    assert _assess_overlap(core, candidate_g)

    candidate_h = Span(18,25,0)
    assert _assess_overlap(core, candidate_h)

    candidate_i = Span(20,25,0)
    assert not _assess_overlap(core, candidate_i)

    candidate_j = Span(22,25,0)
    assert not _assess_overlap(core, candidate_j)

def test_assess_containment():
    core = Span(10,20,0)

    candidate_a = Span(0,5,0)
    assert not _assess_containment(core, candidate_a)
    
    candidate_b = Span(5,10,0)
    assert not _assess_containment(core, candidate_b)
    
    candidate_c = Span(5,12,0)
    assert not _assess_containment(core, candidate_c)

    candidate_d = Span(5,25,0)
    assert not _assess_containment(core, candidate_d)

    candidate_e = Span(10,20,0)
    assert _assess_containment(core, candidate_e)

    candidate_f = Span(15,20,0)
    assert _assess_containment(core, candidate_f)

    candidate_g = Span(15,18,0)
    assert _assess_containment(core, candidate_g)

    candidate_h = Span(18,25,0)
    assert not _assess_containment(core, candidate_h)

    candidate_i = Span(20,25,0)
    assert not _assess_containment(core, candidate_i)

    candidate_j = Span(22,25,0)
    assert not _assess_containment(core, candidate_j)

def test_purge_non_overlapping_ranges():
    core = Span(10,20,0)
    candidates = [
        Span(0,5,0),
        Span(5,9,0),
        Span(5,10,0),
        
        Span(5,15,0),
        Span(10,15,0),
        Span(12,15,0),
        Span(12,19,0),
        Span(12,21,0),
        Span(19,20,0),
        Span(19,25,0),

        Span(20,25,0),
        Span(21,25,0),
        Span(25,30,0),
    ]
    snapshot = [ (obj.lower, obj.upper) for obj in candidates]
    expected = [
        (5,15),
        (10,15),
        (12,15),
        (12,19),
        (12,21),
        (19,20),
        (19,25),
    ]

    result = _purge_non_overlapping_ranges(core, candidates)

    # test that we don't alter the original:
    assert [ (obj.lower, obj.upper) for obj in candidates] == snapshot
    
    # test the content:
    assert [ (obj.lower, obj.upper) for obj in result] == expected

def test_trim_overhangs():
    core = Span(10,20,0)
    candidates = [
        Span(5,12,0),
        Span(15,17,0),
        Span(18,22,0),
    ]
    # snapshot = [ (obj.lower, obj.upper) for obj in candidates]
    expected = [
        (10, 12),
        (15, 17),
        (18, 20),
    ]
    result = _trim_overhangs(core, candidates)
    # assert [ (obj.lower, obj.upper) for obj in candidates] == snapshot
    # this one does modify in-place
    assert [ (obj.lower, obj.upper) for obj in candidates] == expected

def test_fill_gaps_a():
    core = Span(10,20,0)
    candidates = [
        Span(12,14,0),
        Span(16,19,0),
    ]
    expected = [
        (10, 12),
        (12, 14),
        (14, 16),
        (16, 19),
        (19, 20),
    ]
    result = _fill_gaps(core, candidates)
    assert [ (obj.lower, obj.upper) for obj in result] == expected

def test_fill_gaps_b():
    core = Span(10,20,0)
    candidates = [
        Span(10,15,0),
        Span(15,20,0),
    ]
    expected = [
        (10,15),
        (15,20),
    ]
    result = _fill_gaps(core, candidates)
    assert [ (obj.lower, obj.upper) for obj in result] == expected

def test_apply_adjustments():
    candidates = [
        Span(10,15,-5),
        Span(15,20,+3),
        Span(20,25,0)
    ]
    expected = [
        (5,10,0),
        (18,23,0),
        (20,25,0),
    ]
    result = _apply_adjustments(candidates)
    assert [ (obj.lower, obj.upper, obj.adjustment) for obj in result] == expected

def test_consolidate_maps():
    candidates_a = [
        Span(0,5,0),
        Span(5,12,0),
        Span(12,20,0),
        Span(25,30,0),
    ]
    expected_a = [
        (0,20),
        (25,30),
    ]
    result_a = _consolidate_maps(candidates_a)
    assert [ (obj.lower, obj.upper) for obj in result_a] == expected_a

    candidates_b = [
        Span(0,40,0),
        Span(5,12,0),
        Span(12,20,0),
        Span(25,30,0),
    ]
    expected_b = [
        (0,40),
    ]
    result_b = _consolidate_maps(candidates_b)
    assert [ (obj.lower, obj.upper) for obj in result_b] == expected_b
