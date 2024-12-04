import pytest
from collections import Counter

def get_data(file_handle):
    sink = {"left": [], "right": [],}
    while True:
        line = file_handle.readline()
        if not line:
            break
        line = [int(n.strip()) for n in line.split()]
        sink["left"].append(line[0])
        sink["right"].append(line[-1])
    return sink

def _dist_fn(sink):
    sink["left"].sort()
    sink["right"].sort()
    sink["dists"] = []
    for i in range(len(sink["left"])):
        sink["dists"].append(abs(sink["left"][i] - sink["right"][i]))
    ans = sum(sink["dists"])
    return ans

def _simscore_fn(sink):
    ans = 0
    rc = Counter(sink["right"])
    for n in set(sink["left"]):
        if n not in rc.keys():
            continue
        ans += n * rc[n]
    return ans

def calculate(src, fn):
    with open(src, 'r') as f:
        data = get_data(f)
    ans = fn(data)
    return ans

if __name__ == "__main__":
    print(f"sum of distances: {calculate('data.txt', _dist_fn)}")
    print(f"similarity score: {calculate('data.txt', _simscore_fn)}")





def test_get_data():
    with open("test_data.txt", 'r') as tf:
        data = get_data(tf)
    assert data["left"][0] == 15131
    assert data["right"][0] == 78158
    assert data["left"][-1] == 57168
    assert data["right"][-1] == 71761

def test_dist_fn():
    test_data = {
        "left": [15131,32438,12503,73808,57168,],
        "right":[78158,35057,57702,43128,71761,],
    }
    correct_distances = [22554, 27997, 25264, 14593, 4350]
    ans = _dist_fn(test_data)
    assert ans == sum(correct_distances)

def test_simscore_fn():
    test_data = {
        "left": [15131,57702,12503,73808,57168,98765,98765,],
        "right":[78158,35057,57702,42908,71761,],
    }
    correct_counts = {78158: 1, 35057: 1, 57702: 1, 12503: 1, 71761: 1}
    assert correct_counts[test_data["left"][2]] == 1
    with pytest.raises(KeyError):
        assert correct_counts[test_data["left"][5]] == 0
    ans = _simscore_fn(test_data)
    assert ans == 57702

def test_calculate_calculate_distance():
    n = calculate("test_data.txt", _dist_fn)
    assert n == 64133

def test_calculate_similarity_score_with_dit():
    n = calculate("test_data.txt", _simscore_fn)
    assert n == 12503
