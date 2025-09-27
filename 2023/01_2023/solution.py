from pathlib import Path
import string
from dataclasses import dataclass
import sys
from enum import StrEnum
import re
from typing import Generator

# On each line, the calibration value can be found by
# combining the first digit and the last digit (in
# that order) to form a single two-digit number.


class SpelledNumbers(StrEnum):
    one = ("1",)
    two = ("2",)
    three = ("3",)
    four = ("4",)
    five = ("5",)
    six = ("6",)
    seven = ("7",)
    eight = ("8",)
    nine = ("9",)


"""
_FIRST_LETTERS: first letters of the spelled
integers one through nine.
used as a first-pass check
to see if it's worth doing a
full regex check
"""
_FIRST_LETTERS = {"o", "t", "f", "s", "e", "n"}
_DIGITS = set(string.digits)


@dataclass
class Digies:
    # data object for a given line's parsed digit values
    first: str = "0"
    last: str = "0"


def char_check(char: str, seq: set) -> bool:
    # check if a given character is in a given sequence
    return char in seq


def spelled_number_check(sequence: str) -> str | None:
    # check if any spelled number in SpelledNumbers enum is
    # found at _beginning_ of sequence string
    for token in SpelledNumbers:
        if bool(re.match(token.name, sequence)):
            return token.value
    return None


def check_position_for_value(position: int, obj: Digies, line: str, attr: str) -> bool:
    # do integer and spelled number checks for a given position in
    # a given sequence (string)
    # setattr allows us to use the same check logic for both first and
    # last numbers in the sequence
    if char_check(line[position], _DIGITS):
        setattr(obj, attr, line[position])
        return True
    elif char_check(line[position], _FIRST_LETTERS):
        _token = spelled_number_check(line[position:])
        if _token is not None:
            setattr(obj, attr, _token)
            return True
    return False


def get_digies(line) -> int:
    digies = Digies()
    position = 0

    # get first digit from line by iterating forward:
    while position < len(line):
        if bool(check_position_for_value(position, digies, line, "first")):
            break
        position += 1

    # get last digit from line by iterating backward:
    position = len(line) - 1
    while position >= 0:
        if bool(check_position_for_value(position, digies, line, "last")):
            break
        position -= 1

    if digies.first == 0:
        return int(digies.last)
    return int(digies.first + digies.last)


def parse_file(file: str) -> Generator[int]:
    assert Path(file).exists()
    with open(file) as f:
        for line in f.readlines():
            yield get_digies(line.strip())


def main():
    file = sys.argv[1]
    digies = list(parse_file(file))
    print(sum(digies))


if __name__ == "__main__":
    main()
