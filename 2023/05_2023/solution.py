from dataclasses import dataclass
import sys
from concurrent.futures import ProcessPoolExecutor, wait
from time import monotonic


ORDER = [
    "seed_to_soil",
    "soil_to_fertilizer",
    "fertilizer_to_water",
    "water_to_light",
    "light_to_temperature",
    "temperature_to_humidity",
    "humidity_to_location",
]


@dataclass
class Mapping:
    destination_start: int
    source_start: int
    range_length: int

@dataclass
class SeedRange:
    value: int
    length: int

@dataclass
class Almanac:
    order: list[str]
    seeds: list[int]
    seed_ranges: list[SeedRange]
    seed_to_soil: list[Mapping]
    soil_to_fertilizer: list[Mapping]
    fertilizer_to_water: list[Mapping]
    water_to_light: list[Mapping]
    light_to_temperature: list[Mapping]
    temperature_to_humidity: list[Mapping]
    humidity_to_location: list[Mapping]


def parse_seeds(line: str) -> list[int]:
    seeds = line.replace("seeds: ", "")
    return [int(n) for n in seeds.split(" ") if n != ""]

def parse_seed_ranges(line: str) -> list[SeedRange]:
    seed_string = line.replace("seeds: ", "")
    numbers = [int(n) for n in seed_string.split(" ") if n != ""]
    seed_ranges = []
    for i in range(0, len(numbers), 2):
        seed_ranges.append(SeedRange(
            value = numbers[i],
            length = numbers[i+1]
        ))
    return seed_ranges

def parse_map(line: str) -> Mapping:
    numbers = [int(n) for n in line.split(" ") if n.strip() not in {"", "\n"}]
    return Mapping(*numbers)

def parse_text(file) -> Almanac:
    builder = {}
    while True:
        line = file.readline()
        if len(line) == 0:
            break
        if line == "\n":
            continue
        if "seeds:" in line:
            builder["seeds"] = parse_seeds(line)
            builder["seed_ranges"] = parse_seed_ranges(line)
        elif "map:" in line:
            map_category = line.split(" ")[0].replace("-", "_").strip()
            maps = []
            while True:
                line = file.readline()
                if line in {"\n", ""}:
                    break
                maps.append(parse_map(line))
            builder[map_category] = sorted(maps, key=lambda mp: mp.source_start)
    builder["order"] = ORDER
    return Almanac(**builder)

def offset_value(value: int, mapping: Mapping) -> int:
    difference = value - mapping.source_start
    return mapping.destination_start + difference

def map_src_to_dest(value: int, maps: list[Mapping]) -> int:
    for mapping in maps:
        if value >= mapping.source_start and value < (mapping.source_start + mapping.range_length):
            return offset_value(value, mapping)
    return value

def process_single_seed(seed: int, almanac: Almanac) -> int:
    transient = seed
    for attr in almanac.order:
        transient = map_src_to_dest(transient, getattr(almanac, attr))
    return transient

def process_seeds(almanac: Almanac, seed_range: SeedRange|None = None) -> int:
    if not seed_range:
        min_location = process_single_seed(almanac.seeds[0], almanac)
        for seed in almanac.seeds[1:]:
            _loc = process_single_seed(seed, almanac)
            if _loc < min_location:
                min_location = _loc
    else:
        min_location = process_single_seed(seed_range.value, almanac)
        for seed in range(seed_range.value + 1, seed_range.value + seed_range.length):
            _loc = process_single_seed(seed, almanac)
            if _loc < min_location:
                min_location = _loc
    return min_location

def accelerator(almanac: Almanac) -> int:
    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(process_seeds, almanac, seed_range)
            for seed_range in almanac.seed_ranges
        ]
        wait(futures)
        return min([future.result() for future in futures])






def main():
    file = sys.argv[1]
    with open(file, "r") as f:
        almanac = parse_text(f)

    pt1_closest = process_seeds(almanac=almanac)
    print(f"part 1 closest location: {pt1_closest}", flush=True)

    # 4972.09s == 1h23m !!
    # see https://advent-of-code.xavd.id/writeups/2023/day/5/
    # for algorithmic improvements
    parallel_start = monotonic()
    pt2_acc_closest = accelerator(almanac=almanac)
    parallel_end = monotonic()
    print(f"part 2 parallel: closest = {pt2_acc_closest} | duration: {parallel_end - parallel_start: 4f} s", flush=True)

    # unknown time - haven't run this to completion
    # serial_start = monotonic()
    # pt2_locations = []
    # for seed_range in almanac.seed_ranges:
    #     pt2_locations.append(process_seeds(almanac, seed_range))
    # pt2_closest = min(pt2_locations)
    # serial_end = monotonic()
    # print(f"part 2 serial: closest = {pt2_closest} | duration: {serial_end - serial_start: 4f} s", flush=True)


if __name__ == "__main__":
    main()
