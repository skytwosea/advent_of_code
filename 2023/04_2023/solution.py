from dataclasses import dataclass
from typing import TextIO
import sys


@dataclass
class Results:
    part_1: int
    part_2: int


@dataclass
class Card:
    id: int
    winners: set[int]
    choices: set[int]


@dataclass
class PointsMatches:
    points: int
    matchspan_lb: int
    matchspan_ub: int


def parse_line(line: str) -> Card:
    main_parts = line.split(":")
    number_parts = main_parts[-1].strip().split(" | ")

    id = int(main_parts[0].strip().split(" ")[-1])
    winners = {int(i) for i in number_parts[0].strip().split()}
    choices = {int(i) for i in number_parts[-1].strip().split()}

    return Card(id=id, winners=winners, choices=choices)


def card_parser(card: Card) -> PointsMatches:
    matches_count = len(card.winners.intersection(card.choices))
    if matches_count < 1:
        points = 0
    else:
        points = 2 ** (matches_count - 1)
    return PointsMatches(
        points=points,
        matchspan_lb=card.id + 1,
        matchspan_ub=card.id + 1 + matches_count,
    )


def process_text(file: TextIO) -> Results:
    card_sum = 0
    copy_tracker = dict()
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        card = parse_line(line)
        card_results = card_parser(card)

        # part 1: tally this card's won points
        card_sum += card_results.points
        # breakpoint()
        # part 2: add this card's id to the card tracker:
        copy_tracker[card.id] = copy_tracker.get(card.id, 0) + 1

        # part 2: add this card's won copies to the tracker,
        # multiplied by the number of copies of this card:
        card_copies = copy_tracker.get(card.id)
        for i in range(card_results.matchspan_lb, card_results.matchspan_ub):
            copy_tracker[i] = copy_tracker.get(i, 0) + card_copies

        # part 2: count number of cards:
        card_count = sum(copy_tracker.values())

    return Results(part_1=card_sum, part_2=card_count)


def main():
    file = sys.argv[1]
    with open(file, "r") as f:
        results = process_text(f)
    print(f"part 1: {results.part_1}\npart 2: {results.part_2}")


if __name__ == "__main__":
    main()
