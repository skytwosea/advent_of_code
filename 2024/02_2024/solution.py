def get_data(src):
    sink = []
    with open(src, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            sink.append([int(n) for n in line.split()])
    return sink


def _validate_exact(report) -> bool:
    if not report:
        return False
    direction = True if report[0] - report[1] < 0 else False
    for n in range(len(report) - 1):
        step = report[n] - report[n + 1]
        if (step == 0 or (step < 0) != direction or abs(step) > 3):
            return False
    return True

def _validate_tolerant(report) -> bool:
    if _validate_exact(report):
        return True
    for i in range(len(report)):
        _report = report.copy()
        _ = _report.pop(i)
        if _validate_exact(_report):
            return True
    return False

def safety_check(src, fn):
    sink = get_data(src)
    safe_count = 0
    for report in sink:
        if fn(report):
            safe_count += 1
    return safe_count

if __name__ == "__main__":
    print(f"safe reports no tolerance  : {safety_check("data.txt", _validate_exact)}")
    print(f"safe reports with tolerance: {safety_check("data.txt", _validate_tolerant)}")



# TESTS

def test_get_data():
    sink = get_data("test_data.txt")
    assert len(sink) == 5
    assert sink[0][2] == 47
    assert sink[4][5] == 47

def test_validate_exact():
    assert not _validate_exact([44, 44, 47, 48, 30, 51])  # fail: both
    assert not _validate_exact([62, 59, 63, 65, 66, 68, 70, 67])  # fail: stepping
    assert not _validate_exact([25, 27, 30, 31, 37])  # fail: spacing
    assert _validate_exact([7, 10, 13, 14, 17, 19])  # pass
    assert _validate_exact([19, 17, 14, 13, 10, 7])  # pass
    assert not _validate_exact([])  # fail

def test_validate_with_tolerance():
    assert _validate_tolerant([1,3,5,6,7,]) # pass
    assert _validate_tolerant([1,3,5,4,7,]) # pass when 4 is removed
    assert not _validate_tolerant([1,3,5,4,9]) # fail when 4 is removed: 9 - 5 > 3
    assert _validate_tolerant([9,8,7,6,5,]) # pass
    assert _validate_tolerant([8,9,7,6,5,]) # pass when 9 or 8 is removed
    assert _validate_tolerant([8,9,8,6,5,]) # pass when first 8 is removed only
    assert _validate_tolerant([1,2,3,4,5,]) # pass
    assert _validate_tolerant([1,2,3,4,9,]) # pass when 9 is removed
    assert not _validate_tolerant([1,2,3,3,9,]) # fail whether a 3 or the 9 is removed

def test_safety_check():
    ans = safety_check("test_data.txt", _validate_exact)
    assert ans == 1
