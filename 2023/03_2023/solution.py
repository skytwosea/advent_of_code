import string
from typing import TextIO
from dataclasses import dataclass, field
import sys
from functools import reduce


DIGITS = string.digits
SYMBOLS = string.punctuation.replace(".", "")
GEAR = "*"


@dataclass
class SymbolElement:
    col: int
    row: int
    by: int = 0
    by_products: set[int] = field(default_factory=lambda: set())

    def __hash__(self):
        return hash(self.col * self.row)

    def get_tuple(self):
        return (self.col, self.row)


@dataclass(frozen=True)  # make it immutable so that it is default-hashable
class NumberElement:
    value: int
    length: int
    anchor_col: int
    anchor_row: int


@dataclass(frozen=True)
class ParsedLine:
    number_elements: set[NumberElement]
    symbols: set[SymbolElement]
    gears: set[SymbolElement]


@dataclass
class Results:
    part_1: int
    part_2: int


def generate_halo(
    obj: NumberElement, max_cols: int, max_rows: int
) -> set[tuple[int, int]]:
    """Generate the set of all coordinates that surround a number element's position

    Halo coordinates are all grid positions that directly touch the number, e.g.
    all coordinates of pound symbol:
        . . . . . . .
        . # # # # # .
        . # 1 2 3 # .
        . # # # # # .
        . . . . . . .

    Note that the mask eliminates coordinates that overprint the number's coordinates,
    as well as coordinates that are outside the boundary of the grid in which the number
    is found:
        # # # # .
        1 2 3 # .
        # # # # .
    """

    # restrict lower and upper bound to column index:
    if obj.anchor_col != 0:
        col_lb = obj.anchor_col - 1
    else:
        col_lb = 0
    if obj.anchor_col + obj.length > max_cols:
        col_ub = max_cols
    else:
        col_ub = obj.anchor_col + obj.length + 1

    # restrict lower and upper bound to row index:
    if obj.anchor_row != 0:
        row_lb = obj.anchor_row - 1
    else:
        row_lb = 0
    if obj.anchor_row + 2 > max_rows:
        row_ub = max_rows
    else:
        row_ub = obj.anchor_row + 2

    # generate set of overprinting coordinates:
    halo = set()
    col_vals = {i for i in range(col_lb, col_ub)}
    for i in range(row_lb, row_ub):
        for j in col_vals:
            halo.add((j, i))

    # generate mask of number's coordinates
    mask = {
        (i, obj.anchor_row) for i in range(obj.anchor_col, obj.anchor_col + obj.length)
    }

    return halo.difference(mask)


def parse_line(line: str, row: int) -> ParsedLine:
    record_on = False
    value_builder = []
    anchor_col = 0
    number_elements = set()
    symbols = set()
    gears = set()
    for col, char in enumerate(line):
        if char in DIGITS:
            value_builder.append(char)
            if not record_on:
                record_on = True
                anchor_col = col
        elif record_on:
            record_on = False
            number_elements.add(
                NumberElement(
                    value=int("".join(value_builder)),
                    length=len(value_builder),
                    anchor_col=anchor_col,
                    anchor_row=row,
                )
            )
            value_builder = []
        if char in SYMBOLS:
            symbols.add(SymbolElement(col=col, row=row))
        if char in GEAR:
            gears.add(SymbolElement(col=col, row=row))
    return ParsedLine(number_elements=number_elements, symbols=symbols, gears=gears)


def sum_numbers_with_adjacent_symbols(
    number_elements: set[NumberElement],
    symbols: set[SymbolElement],
    max_cols: int,
    max_rows: int,
) -> int:
    result = 0
    symbol_tuples = {s.get_tuple() for s in symbols}
    for nel in number_elements:
        _halo = generate_halo(nel, max_cols, max_rows)
        if len(_halo.intersection(symbol_tuples)) > 0:
            result += nel.value
    return result


def sum_gear_numbers(
    number_elements: set[NumberElement],
    gears: set[SymbolElement],
    max_cols: int,
    max_rows: int,
) -> int:
    for gear in gears:
        gear_coordinate = gear.get_tuple()
        for nel in number_elements:
            _halo = generate_halo(nel, max_cols, max_rows)
            if gear_coordinate in _halo:
                gear.by += 1
                gear.by_products.add(nel.value)
    _partial = {reduce(lambda x, y: x * y, g.by_products) for g in gears if g.by == 2}
    return reduce(lambda x, y: x + y, _partial)


def parse_text(file: TextIO) -> Results:
    number_elements = set()
    symbols = set()
    gears = set()

    line = file.readline()
    row_len = 0
    col_len = len(line)  # assuming all lines are equal length

    while True:
        if len(line) == 0:
            break
        line_elements = parse_line(line, row_len)
        number_elements.update(line_elements.number_elements)
        symbols.update(line_elements.symbols)
        gears.update(line_elements.gears)
        line = file.readline()
        row_len += 1

    return Results(
        part_1=sum_numbers_with_adjacent_symbols(
            number_elements, symbols, col_len, row_len
        ),
        part_2=sum_gear_numbers(number_elements, gears, col_len, row_len),
    )


def main():
    file = sys.argv[1]
    with open(file, "r") as f:
        results = parse_text(f)
    print(f"part 1: {results.part_1}\npart 2: {results.part_2}")


if __name__ == "__main__":
    main()
