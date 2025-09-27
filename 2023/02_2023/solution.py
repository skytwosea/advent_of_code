from dataclasses import dataclass
import dataclasses
import sys
from typing import TextIO
from io import StringIO


@dataclass
class ParsedValues:
    red: int = 0
    green: int = 0
    blue: int = 0


LIMIT = ParsedValues(red=12, green=13, blue=14)


def get_game_number(sequence: str) -> int:
    return int(sequence.split(" ")[-1])


def parse_draw(draw: str) -> ParsedValues:
    parsed_draw = ParsedValues()
    for _block in draw.split(","):
        _components = _block.strip().split(" ")
        setattr(parsed_draw, _components[1], int(_components[0]))
    return parsed_draw


def compare_draw(draw: ParsedValues) -> bool:
    for field in dataclasses.fields(draw):
        if getattr(draw, field.name) > getattr(LIMIT, field.name):
            return False
    return True


def check_and_set_min_values(
    game_tally: ParsedValues, parsed_draw: ParsedValues
) -> None:
    for field in dataclasses.fields(parsed_draw):
        if getattr(parsed_draw, field.name) > getattr(game_tally, field.name):
            setattr(game_tally, field.name, getattr(parsed_draw, field.name))


def get_power_set(game_tally: ParsedValues) -> int:
    pset = 1
    for field in dataclasses.fields(game_tally):
        pset *= getattr(game_tally, field.name)
    return pset


def parse_line(line: str) -> tuple[int, int]:
    all_components = line.split(":")
    game_number = int(get_game_number(all_components[0].strip()))
    block_draws = all_components[1].strip().split(";")

    game_tally = ParsedValues()
    impossible = False

    for _draw in block_draws:
        parsed_draw = parse_draw(_draw)
        check_and_set_min_values(game_tally, parsed_draw)
        if not impossible and not compare_draw(parsed_draw):
            game_number = 0
            impossible = True

    power_set = get_power_set(game_tally)

    return (game_number, power_set)


def assess_games(file: TextIO) -> tuple[int, int]:
    game_1_result = 0
    game_2_result = 0
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        _parsed = parse_line(line)
        game_1_result += _parsed[0]
        game_2_result += _parsed[1]
    return (game_1_result, game_2_result)


def main():
    file = sys.argv[1]
    with open(file, "r") as f:
        print(assess_games(f))


if __name__ == "__main__":
    main()


full_test_data = """Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green"""

game_component_data = """Game 1
Game 2
Game 3
Game 4
Game 5"""

draw_test_data = """3 blue, 4 red
3 green, 4 blue
4 red, 13 green
8 green, 6 blue, 20 red
3 red"""


def test_get_game_number():
    for n, item in enumerate(game_component_data.split("\n")):
        assert isinstance(get_game_number(item), int)
        assert get_game_number(item) == n + 1


def test_parse_draw():
    draws = [
        ParsedValues(blue=3, red=4, green=0),
        ParsedValues(green=3, blue=4, red=0),
        ParsedValues(red=4, green=13, blue=0),
        ParsedValues(green=8, blue=6, red=20),
        ParsedValues(red=3, blue=0, green=0),
    ]
    for n, draw in enumerate(draw_test_data.split("\n")):
        assert parse_draw(draw) == draws[n]


def test_compare_draw():
    draws = [
        (ParsedValues(red=4, green=0, blue=3), True),
        (ParsedValues(red=0, green=3, blue=4), True),
        (ParsedValues(red=4, green=13, blue=0), True),
        (ParsedValues(red=20, green=8, blue=6), False),
        (ParsedValues(red=3, green=0, blue=0), True),
        (ParsedValues(red=2, green=8, blue=16), False),
    ]
    for draw in draws:
        assert compare_draw(draw[0]) == draw[1]


def test_assess_games():
    with StringIO(full_test_data) as tf:
        results = assess_games(tf)
        assert results[0] == 8
        assert results[1] == 2286
