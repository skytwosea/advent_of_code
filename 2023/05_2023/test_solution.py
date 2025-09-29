from solution import *

def test_parse_seeds():
    line = "seeds: 79 14 55 13"
    assert parse_seeds(line) == [79, 14, 55, 13]

def test_parse_map():
    line = "50 98 2"
    assert parse_map(line) == Mapping(
        destination_start = 50,
        source_start = 98,
        range_length = 2
    )

def test_parse_text():
    with open("test_data.txt", "r") as tf:
        almanac = parse_text(tf)
    assert almanac.seed_to_soil == [
        Mapping(
            destination_start = 52,
            source_start = 50,
            range_length = 48
        ),
        Mapping(
            destination_start = 50,
            source_start = 98,
            range_length = 2
        )
    ]
    assert almanac.temperature_to_humidity == [
        Mapping(
            destination_start = 1,
            source_start = 0,
            range_length = 69
        ),
        Mapping(
            destination_start = 0,
            source_start = 69,
            range_length = 1
        )
    ]
    assert almanac.order == ORDER
    assert almanac.seeds == [79, 14, 55, 13]

def test_map_src_to_dest():
    mappings = [
        Mapping(
            destination_start = 52,
            source_start = 50,
            range_length = 48
        ),
        Mapping(
            destination_start = 50,
            source_start = 98,
            range_length = 2
        )
    ]
    answers = [81, 14, 57, 13]
    for n, value in enumerate([79, 14, 55, 13]):
        assert map_src_to_dest(value, mappings) == answers[n]

def test_get_closest_location_single_seeds():
    # part 1
    with open("test_data.txt", "r") as tf:
        almanac = parse_text(tf)
    assert process_seeds(almanac) == 35

def test_get_closest_location_seed_ranges_single_process():
    # part 2, single process
    with open("test_data.txt", "r") as tf:
        almanac = parse_text(tf)
    pt2_locations = []
    for seed_range in almanac.seed_ranges:
        pt2_locations.append(process_seeds(almanac, seed_range))
    assert min(pt2_locations) == 46

def test_get_closest_location_seed_ranges_multiprocess():
    # part 2, using ProcessPoolExecutor
    with open("test_data.txt", "r") as tf:
        almanac = parse_text(tf)
    assert accelerator(almanac=almanac) == 46
