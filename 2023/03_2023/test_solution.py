from solution import *
from io import StringIO

test_data = """467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598.."""


def test_data_read():
    with StringIO(test_data) as tf:
        first_line = tf.readline()
        assert first_line == "467..114..\n"
        _ = tf.readline()
        third_line = tf.readline()
        assert third_line == "..35..633.\n"


def test_generate_halo_a():
    # test_halo_data_a = """
    # ........
    # ...456..
    # ........
    # """
    element = NumberElement(value=456, length=3, anchor_row=1, anchor_col=3)
    assert (
        generate_halo(element, max_cols=8, max_rows=3).difference(
            {
                (2, 0),
                (3, 0),
                (4, 0),
                (5, 0),
                (6, 0),
                (2, 1),
                (6, 1),
                (2, 2),
                (3, 2),
                (4, 2),
                (5, 2),
                (6, 2),
            }
        )
        == set()
    )


def test_generate_halo_b():
    # test_halo_data_b = """
    # ........
    # 123.....
    # ........
    # """
    element = NumberElement(value=123, length=3, anchor_row=1, anchor_col=0)
    assert (
        generate_halo(element, max_cols=8, max_rows=3).difference(
            {
                (0, 0),
                (1, 0),
                (2, 0),
                (3, 0),
                (3, 1),
                (0, 2),
                (1, 2),
                (2, 2),
                (3, 2),
            }
        )
        == set()
    )


def test_generate_halo_c():
    # test_halo_data_c = """
    # ..345...
    # ........
    # ........
    # """
    element = NumberElement(value=345, length=3, anchor_row=0, anchor_col=2)
    assert (
        generate_halo(element, max_cols=8, max_rows=3).difference(
            {
                (1, 0),
                (5, 0),
                (1, 1),
                (2, 1),
                (3, 1),
                (4, 1),
                (5, 1),
            }
        )
        == set()
    )


def test_generate_halo_d():
    # test_halo_data_d = """
    # ........
    # ........
    # ...45...
    # """
    element = NumberElement(value=45, length=2, anchor_row=2, anchor_col=3)
    assert (
        generate_halo(element, max_cols=8, max_rows=3).difference(
            {
                (2, 1),
                (3, 1),
                (4, 1),
                (5, 1),
                (2, 2),
                (5, 2),
            }
        )
        == set()
    )


def test_parse_line_a():
    # test_data = """467..114..
    # ...*......
    # ..35..633.
    # ......#...
    # 617*......
    # .....+.58.
    # ..592.....
    # ......755.
    # ...$.*....
    # .664.598.."""
    line = "......755."
    assert parse_line(line, row=7) == ParsedLine(
        {
            NumberElement(value=755, length=3, anchor_col=6, anchor_row=7),
        },
        set(),
        set(),
    )


def test_parse_line_b():
    # test_data = """467..114..
    # ...*......
    # ..35..633.
    # ......#...
    # 617*......
    # .....+.58.
    # ..592.....
    # ......755.
    # ...$.*....
    # .664.598.."""
    line = "..35..633."
    assert parse_line(line, row=2) == ParsedLine(
        {
            NumberElement(value=35, length=2, anchor_col=2, anchor_row=2),
            NumberElement(value=633, length=3, anchor_col=6, anchor_row=2),
        },
        set(),
        set(),
    )


def test_parse_line_c():
    # test_data = """467..114..
    # ...*......
    # ..35..633.
    # ......#...
    # 617*......
    # .....+.58.
    # ..592.....
    # ......755.
    # ...$.*....
    # .664.598.."""
    line = "......#..."
    assert parse_line(line, row=3) == ParsedLine(
        set(), {SymbolElement(col=6, row=3)}, set()
    )


def test_parse_line_d():
    # test_data = """467..114..
    # ...*......
    # ..35..633.
    # ......#...
    # 617*......
    # .....+.58.
    # ..592.....
    # ......755.
    # ...$.*....
    # .664.598.."""
    line = "...$.*...."
    assert parse_line(line, row=8) == ParsedLine(
        set(),
        {SymbolElement(col=3, row=8), SymbolElement(col=5, row=8)},
        {SymbolElement(col=5, row=8)},
    )


def test_parse_line_e():
    # test_data = """467..114..
    # ...*......
    # ..35..633.
    # ......#...
    # 617*......
    # .....+.58.
    # ..592.....
    # ......755.
    # ...$.*....
    # .664.598.."""
    line = ".....+.58."
    assert parse_line(line, row=5) == ParsedLine(
        {
            NumberElement(value=58, length=2, anchor_col=7, anchor_row=5),
        },
        {SymbolElement(col=5, row=5)},
        set(),
    )


def test_parse_line_f():
    # test_data = """467..114..
    # ...*......
    # ..35..633.
    # ......#...
    # 617*......
    # .....+.58.
    # ..592.....
    # ......755.
    # ...$.*....
    # .664+598.."""
    line = ".664+598.."
    assert parse_line(line, row=9) == ParsedLine(
        {
            NumberElement(value=664, length=3, anchor_col=1, anchor_row=9),
            NumberElement(value=598, length=3, anchor_col=5, anchor_row=9),
        },
        {SymbolElement(col=4, row=9)},
        set(),
    )


def test_parse_text_part_1():
    with StringIO(test_data) as tf:
        assert parse_text(tf).part_1 == 4361


def test_parse_text_part_2():
    with StringIO(test_data) as tf:
        assert parse_text(tf).part_2 == 467835


def test_hasbability_of_symbol_elements():
    basket = set()
    for i in range(0, 5):
        for j in range(5, 0):
            basket.add(SymbolElement(col=i, row=j))
