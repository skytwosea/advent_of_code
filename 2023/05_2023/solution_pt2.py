from dataclasses import dataclass
import sys
import math
from collections import namedtuple
from copy import deepcopy


ORDER = [
    "seed_to_soil",
    "soil_to_fertilizer",
    "fertilizer_to_water",
    "water_to_light",
    "light_to_temperature",
    "temperature_to_humidity",
    "humidity_to_location",
]


class Span:
    lower: int
    upper: int
    adjustment: int

    def __init__(self, lower, upper, adjustment):
        self.lower = lower
        self.upper = upper
        self.adjustment = adjustment

    @property
    def length(self) -> int:
        return self.upper - self.lower

    def __repr__(self):
        return f"Span({self.lower}, {self.upper}, {self.adjustment})"


SubSpan = namedtuple("SubSpan", ["start", "end"])


@dataclass
class Almanac:
    order: list[str]
    seed_ranges: list[Span]
    seed_to_soil: list[Span]
    soil_to_fertilizer: list[Span]
    fertilizer_to_water: list[Span]
    water_to_light: list[Span]
    light_to_temperature: list[Span]
    temperature_to_humidity: list[Span]
    humidity_to_location: list[Span]


def parse_map(line: str) -> Span:
    numbers = [int(n) for n in line.split(" ") if n.strip() not in {"", "\n"}]
    lower = numbers[1]
    upper = numbers[1] + numbers[2]
    adjustment = numbers[0] - numbers[1]
    return Span(lower, upper, adjustment)


def parse_seeds(line: str) -> list[Span]:
    seeds = line.replace("seeds: ", "")
    cast = [int(n) for n in seeds.split(" ") if n != ""]
    seed_ranges = []
    for i in range(0, len(cast), 2):
        seed_ranges.append(
            Span(lower=cast[i], upper=cast[i] + cast[i + 1], adjustment=0)
        )
    return seed_ranges


def parse_text(file) -> Almanac:
    builder = {}
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        if line == "\n":
            continue
        if "seeds:" in line:
            builder["seed_ranges"] = parse_seeds(line)
        elif "map:" in line:
            map_category = line.split(" ")[0].replace("-", "_").strip()
            maps = []
            while True:
                line = file.readline()
                if line in {"\n", ""}:
                    break
                maps.append(parse_map(line))
            builder[map_category] = maps
    builder["order"] = ORDER
    return Almanac(**builder)


def _assess_overlap(this: Span, other: Span, strict: bool = True) -> bool:
    # https://zayenz.se/blog/post/how-to-check-for-overlapping-intervals/
    # de Morgan's law flips the sensible-looking if statement into the
    # fucked up one
    # return not (this.upper <= other lower or other.upper <= this.lower)
    if strict:
        return (other.lower < this.upper and this.lower < other.upper)
    return (other.lower <= this.upper and this.lower <= other.upper)

def _assess_containment(this: Span, other: Span) -> bool:
    return (other.lower >= this.lower and other.upper <= this.upper)

def _purge_non_overlapping_ranges(sr: Span, working_maps: list[Span]) -> list[Span]:
    overlapping = []
    for mr in working_maps:
        if _assess_overlap(sr, mr, True):
            overlapping.append(mr)
    return overlapping

def _trim_overhangs(sr: Span, working_maps: list[Span]) -> list[Span]:
    for mr in working_maps:
        if mr.lower < sr.lower:
            mr.lower = sr.lower
        if mr.upper > sr.upper:
            mr.upper = sr.upper
    return working_maps

def _fill_gaps(sr: Span, working_maps: list[Span]) -> list[Span]:
    working_maps = sorted(working_maps, key=lambda obj: obj.lower)
    gaps = []
    for n, mr in enumerate(working_maps):
        if n == 0 and mr.lower > sr.lower:
            gaps.append(Span(lower=sr.lower, upper=mr.lower, adjustment=0))
        if n == len(working_maps) - 1:
            if sr.upper > mr.upper:
                gaps.append(Span(lower=mr.upper, upper=sr.upper, adjustment=0))
            break
        if mr.upper < working_maps[n+1].lower:
            gaps.append(Span(lower=mr.upper, upper=working_maps[n+1].lower, adjustment=0))
    working_maps.extend(gaps)
    working_maps.sort(key=lambda obj: obj.lower)
    return working_maps

def _apply_adjustments(working_maps: list[Span]) -> list[Span]:
    for mr in working_maps:
        mr.lower += mr.adjustment
        mr.upper += mr.adjustment
        mr.adjustment = 0
    return sorted(working_maps, key=lambda obj: obj.lower)

def _consolidate_maps(working_maps: list[Span]) -> list[Span]:
    if not working_maps or len(working_maps) == 1:
        return working_maps

    spans = sorted(working_maps, key=lambda obj: obj.lower)

    consolidated = []
    this = spans[0]
    lo = spans[0].lower
    hi = spans[0].upper

    for nxt in spans[1:]:
        if _assess_overlap(this, nxt, strict=False):
            if nxt.upper > this.upper:
                this = nxt
                hi = nxt.upper
        else:
            consolidated.append(Span(lo, hi, 0))
            this = nxt
            lo = nxt.lower
            hi = nxt.upper

    consolidated.append(Span(lo, hi, 0))
    return consolidated

def process_mapping(seed_range: list[Span], map_ranges: list[Span]) -> list[Span]:
    # I'm not sure if each iteration of processing a seed range will produce
    # multiple separate ranges for the next iteration. Treat input as a list
    # so we're prepared for that possibility:
    # if isinstance(seed_range, Span):
    #     seed_range = [
    #         seed_range,
    #     ]

    result = []

    # the map_ranges list gets mutated and adjusted through this function,
    # so create a deep copy to preserve the original:

    for sr in seed_range:
        working_maps = deepcopy(map_ranges)
        purged = _purge_non_overlapping_ranges(sr, working_maps)
        if not purged:
            result.append(sr)
            continue
        trimmed = _trim_overhangs(sr, purged)
        no_gaps = _fill_gaps(sr, trimmed)
        adjusted = _apply_adjustments(no_gaps)
        consolidated = _consolidate_maps(adjusted)
        result.extend(consolidated)

    full = _consolidate_maps(result)
    return full


def process_all_mappings(almanac: Almanac) -> int | None:
    lowest = math.inf
    for sr in almanac.seed_ranges:
        transformed = [sr]
        for attr in almanac.order:
            mapping = getattr(almanac, attr)
            transformed = process_mapping(transformed, mapping)
        candidates = [lowest] + [obj.lower for obj in transformed]
        lowest = min(candidates)
    return None if lowest is math.inf else lowest



def main():
    file = sys.argv[1]
    with open(file, "r") as f:
        almanac = parse_text(f)
    answer = process_all_mappings(almanac)
    known_solution = 79004094
    if answer == known_solution:
        print("pt 2: success")
    else:
        print(f"pt 2: fucking fuck: {answer} != {known_solution}")


if __name__ == "__main__":
    main()
