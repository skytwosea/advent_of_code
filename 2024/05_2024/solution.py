import pytest

class Node:
    def __init__(self, value: int, children: list):
        self.value = value
        self.children = children
        self.before = None
        self.after = None
    
    def get_value(self):
        return self.value

    def is_this_my_child(self, value):
        return value in self.children

    def add(self, node, line_number=None):
        if self.is_this_my_child(node.get_value()):
            self._add_after(node)
        elif node.is_this_my_child(self.value):
            self._add_before(node)
        else:
            # not reached in this exercise
            raise ValueError(
                "could not add node with value "
                f"{node.get_value()}: input line {line_number}"
            )

    def _add_before(self, node):
        if not self.before:
            self.before = node
        else:
            self.before.add(node)

    def _add_after(self, node):
        if not self.after:
            self.after = node
        else:
            self.after.add(node)

    def walk_in_order(self):
        if self.before is not None:
            yield from self.before.walk_in_order()
        yield self.value
        if self.after is not None:
            yield from self.after.walk_in_order() 

def _get_data(src):
    priorities = {}
    updates = []
    with open(src, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            if '|' in line:
                a,b = [int(n) for n in line.split('|')]
                priorities.setdefault(a, []).append(b)
            elif ',' in line:
                updates.append([int(n) for n in line.split(',')])
    return (priorities, updates)

def _get_children_for_value(value, priorities):
    if value not in priorities.keys():
        return []
    return priorities[value]

def _sort_line(line, priorities, line_number=None):
    value = line[0]
    children = _get_children_for_value(value, priorities)
    head = Node(value, children)
    for v in line[1:]:
        new_node = Node(v, _get_children_for_value(v, priorities))
        head.add(new_node, line_number)
    return [v for v in head.walk_in_order()]

def _compute_median_sum(updates):
    ans = 0
    for n, line in enumerate(updates):
        if len(line) % 2 != 0:
            ans += line[len(line)//2]
        else:
            # don't think this will be reached; jic
            print(f"line {n}: even length")
            ans += line[(len(line)//2)-1]
    return ans

def sort_update_pages(src):
    priorities, updates = _get_data(src)
    unchanged_updates = []
    corrected_updates = []
    for n, line in enumerate(updates):
        processed = _sort_line(line, priorities, n)
        if line == processed:
            unchanged_updates.append(processed)
        else:
            corrected_updates.append(processed)
    sum_unchanged = _compute_median_sum(unchanged_updates)
    sum_corrected = _compute_median_sum(corrected_updates)
    return (sum_unchanged, sum_corrected)

def main():
    unch, corr = sort_update_pages("data.txt")
    print(f"median sum unchanged: {unch}\nmedian sum corrected: {corr}")

if __name__ == "__main__":
    main()



# TESTS

@pytest.fixture
def get_test_data():
    return _get_data("test_data.txt")

def test_get_data(get_test_data):
    p, u = get_test_data
    assert len(p) == len(u)
    assert len(p) == 6
    assert len(p[47]) == 4
    assert len(p[75]) == 5
    assert 47 in p[97]
    assert len(u) == 6
    assert len(u[2]) == 3
    assert len(u[5]) == 5
    assert 97 in u[3]

def test_make_a_node_from_raw():
    head = Node(75, [75,47,61,53,29])
    assert head.get_value() == 75
    assert head.is_this_my_child(53)

def test_make_a_node_from_data(get_test_data):
    p, u = get_test_data
    head = Node(u[0][0], p[u[0][0]])
    assert head.get_value() == 75
    assert head.is_this_my_child(53)

def test_node_is_this_my_child_fn(get_test_data):
    p, u = get_test_data
    head = Node(u[0][0], p[u[0][0]])
    assert head.is_this_my_child(13)
    assert head.is_this_my_child(29)
    assert head.is_this_my_child(47)
    assert head.is_this_my_child(53)
    assert head.is_this_my_child(61)
    assert not head.is_this_my_child(5)

def test_make_a_tree_from_data_src_already_sorted(get_test_data):
    p, u = get_test_data
    head = Node(u[0][0], p[u[0][0]])
    for n in u[0][1:]:
        node = Node(n, p[n])
        head.add(node)
    processed = []
    for v in head.walk_in_order():
        processed.append(v)
    assert processed == u[0]

def test_make_another_tree_from_data_src_not_sorted(get_test_data):
    p, u = get_test_data
    head = Node(u[3][0], p[u[3][0]])
    for n in u[3][1:]:
        node = Node(n, p[n])
        head.add(node)
    processed = []
    for v in head.walk_in_order():
        processed.append(v)
    # input: [75,97,47,61,53]
    assert processed == [97,75,47,61,53]

def test_make_yet_another_tree_from_unsorted(get_test_data):
    p, u = get_test_data
    head = Node(u[5][0], p[u[5][0]])
    for n in u[5][1:]:
        if n not in p.keys():
            children = []
        else:
            children = p[n]
        node = Node(n, children)
        head.add(node)
    processed = []
    for v in head.walk_in_order():
        processed.append(v)
    # input: [97,13,75,29,47]
    assert processed == [97, 75, 47, 29, 13]

def test_line_sorter_fn(get_test_data):
    p, u = get_test_data
    reordered = _sort_line(u[5], p)
    # input: [97,13,75,29,47]
    assert reordered == [97, 75, 47, 29, 13]

def test_sorting_all_test_updates(get_test_data):
    p, u = get_test_data
    reordered = []
    for line in u:
        reordered.append(_sort_line(line, p))
    assert reordered[0] == [75,47,61,53,29]
    assert reordered[1] == [97,61,53,29,13]
    assert reordered[2] == [75,29,13]
    assert reordered[3] == [97,75,47,61,53]
    assert reordered[4] == [61,29,13]
    assert reordered[5] == [97,75,47,29,13]
    assert _compute_median_sum(reordered) == 266

def test_compute_median_sum():
    test_data = [
        [75,47,61,53,29],
        [97,61,53,29,13],
        [75,29,13],
    ]
    median_sum = _compute_median_sum(test_data)
    assert median_sum == 143
