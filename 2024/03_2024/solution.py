import re
import pytest

mul_pattern = re.compile(r"mul\((\d+),(\d+)\)")
cond_mul_pattern = re.compile(r"(?:\A|do\(\))[\s\S]*?(?:don't\(\)|\Z)")
# tricky: [\s\S] matches everything _and_ line terminators, whereas the
# dot <.> matches everything _except_ line terminators

def _get_data(src):
    with open(src, 'r') as f:
        sink = f.read()
    return sink

def _sum_multiplies(sink):
    ans = 0
    re_obj = re.finditer(mul_pattern, sink)
    for item in iter(re_obj):
        ans += int(item.group(1)) * int(item.group(2))
    return ans

def _sum_valid_multiplies(sink):
    ans = 0
    valid_domains = re.finditer(cond_mul_pattern, sink)
    for block in iter(valid_domains):
        ans += _sum_multiplies(block.group())
    return ans


def compute(src, fn):
    sink = _get_data(src)
    return fn(sink)

def main():
    print(f"sum of multiplies: {compute("data.txt", _sum_multiplies)}")
    print(f"sum of multiplies: {compute("data.txt", _sum_valid_multiplies)}")

if __name__ == "__main__":
    main()



# TESTS

def test_get_data():
    sink = _get_data("test_data.txt")
    assert isinstance(sink, str)
    assert len(sink) == 268

def test_mul_capture_groups():
    test_str_a = "860)[mul(886,453))mul(168,7)"
    re_obj_a = re.finditer(mul_pattern, test_str_a)
    first = next(re_obj_a)
    assert first.group(1) == "886"
    assert first.group(2) == "453"
    second = next(re_obj_a)
    assert second.group(1) == "168"
    assert second.group(2) == "7"
    test_str_b = "@mul(677,760)*mul(846,234)$from()%what()"
    re_obj_b = re.finditer(mul_pattern, test_str_b)
    first = next(re_obj_b)
    assert int(first.group(1)) == 677
    assert first.group(2) == "760"
    second = next(re_obj_b)
    assert second.group(1) == "846"
    assert int(second.group(2)) == 234

def test_cond_mul_capture_groups():
    test_str_a = "860)[mul(886,453))mul(168,7)"
    re_obj_a = re.findall(cond_mul_pattern, test_str_a)
    assert len(re_obj_a) == 1
    assert test_str_a == re_obj_a[0]

    test_str_b = "don't()860)[mul(886,453))mul(168,7)"
    re_obj_b = re.findall(cond_mul_pattern, test_str_b)
    assert len(re_obj_b) == 1
    assert re_obj_b[0] == "don't()"

    test_str_c = "do()86don't()0)[mul(886,453))mul(168,7)"
    re_obj_c = re.findall(cond_mul_pattern, test_str_c)
    assert len(re_obj_c) == 1
    assert re_obj_c[0] == "do()86don't()"

    test_str_d = "do()86don't0)[mul(886,453))mul(168,7)"
    re_obj_d = re.findall(cond_mul_pattern, test_str_d)
    assert len(re_obj_d) == 1
    assert re_obj_d[0] == test_str_d

    test_str_e = (
        "do()860)[mul(886,453))mul(168,7)"
        "oipqwnrgdon't()linwgrmul(32,4)0923utgh"
        "9835qhguhtmul(xy,9)do()lnvq3p9845mul(987,2)284h"
    )
    re_obj_e = re.findall(cond_mul_pattern, test_str_e)
    assert len(re_obj_e) == 2
    assert len(re_obj_e[0]) == 47
    assert len(re_obj_e[1]) == 28

def test_sum_all_multiplies():
    sink = _get_data("test_data.txt")
    assert _sum_multiplies(sink,) == 2226020

def test_sum_valid_multiplies():
    sink = _get_data("test_data.txt")
    assert _sum_valid_multiplies(sink) == 1836940
