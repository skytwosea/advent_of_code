from solution import *


def test_parse_line():
    with open("test_data.txt", "r") as tf:
        line = tf.readline()
        assert parse_line(line) == Card(
            id=1,
            winners={41, 48, 83, 86, 17},
            choices={83, 86, 6, 31, 17, 9, 48, 53},
        )


def test_card_parser_a():
    card = Card(
        id=1,
        winners={41, 48, 83, 86, 17},
        choices={83, 86, 6, 31, 17, 9, 48, 53},
    )
    assert card_parser(card).points == 8


def test_card_parser_b():
    card = Card(
        id=2,
        winners={13, 32, 20, 16, 61},
        choices={61, 30, 68, 82, 17, 32, 24, 19},
    )
    assert card_parser(card).points == 2


def test_card_parser_c():
    card = Card(
        id=6,
        winners={31, 18, 13, 56, 72},
        choices={74, 77, 10, 23, 35, 67, 36, 11},
    )
    assert card_parser(card).points == 0


def test_process_text():
    with open("test_data.txt", "r") as tf:
        results = process_text(tf)
    assert results.part_1 == 13
    assert results.part_2 == 30
