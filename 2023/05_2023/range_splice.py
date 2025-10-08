from typing import Any
from dataclasses import dataclass
from collections import namedtuple


@dataclass
class RangeData:
    lower: int
    upper: int
    data: Any


@dataclass
class HalfRangeData:
    position: int
    data: Any
    end: bool

MinMax = namedtuple("MinMax", ["lowest", "highest"])


def _get_minmax_bounds_rd(input: list[RangeData]) -> MinMax:
    """Get lowest and highest bounds for input list.
    
    It is incumbent on the caller to merge lists if looking for
    min & max bounds from multiple lists of RangeData objects
    """
    lowest = min([obj.lower for obj in input])
    highest = max([obj.upper for obj in input])
    return MinMax(lowest=lowest, highest=highest)


def _sort_rd(input: list[RangeData]) -> list[RangeData]:
    """Sort list of RangeData objects by lower bound"""
    return sorted(input, key=lambda obj: obj.lower)


def _sort_hrd(input: list[HalfRangeData]) -> list[HalfRangeData]:
    """Sort list of HalfRangeData, by position
    """
    return sorted(input, key=lambda obj: obj.position)


def _fill_gaps(
    input: list[RangeData], lb: int, ub: int, neutral_attr: Any
) -> list[RangeData]:
    """Create RangeData objects needed to span gaps in range.

        v lowest bound
    l1: |-------|  |-------------|---------------------|     |-----|
    l2:    |--------------|---------|           |-------------------------|
                                                            highest bound ^

    Lists of ranges can have gaps, and may extend past each others' bounds.
    Given a single list of RangeData objects and lowest/highest bounds, return
    a list with the gaps filled. These new RangeData objects will have a
    neutral data attribute, e.g. if data attribute is integers, gap objects
    will have data=0

    Note that this function should take a single list at a time, not a
    merged pair of lists, so that gap-spanning objects are assigned the
    correct dimensions.
    """
    gap_objects = []
    rd_sorted = _sort_rd(input)
    if rd_sorted[0].lower > lb:
        gap_objects.append(
            RangeData(lower=lb, upper=rd_sorted[0].lower, data=neutral_attr)
        )
    if rd_sorted[-1].upper < ub:
        gap_objects.append(
            RangeData(lower=rd_sorted[-1].upper, upper=ub, data=neutral_attr)
        )
    for n, rd_obj in enumerate(rd_sorted):
        if n + 1 >= len(rd_sorted):
            break
        if rd_obj.upper < rd_sorted[n + 1].lower:
            gap_objects.append(
                RangeData(
                    lower=rd_obj.upper, upper=rd_sorted[n + 1].lower, data=neutral_attr
                )
            )
    return _sort_rd(rd_sorted + gap_objects)


def _rd_to_hrd(input: list[RangeData]) -> list[HalfRangeData]:
    """Convert from list of RangeData obj to list of HalfRangeData objects
    """
    output = []
    for obj in input:
        if obj.lower == obj.upper:
            continue
        output.append(HalfRangeData(position=obj.lower, data=obj.data, end=False))
        output.append(HalfRangeData(position=obj.upper, data=obj.data, end=True))
    return output


def _generate_ranges_from_hrd_sequence(input: list[HalfRangeData]) -> list[RangeData]:
    """Build RangeData sequence with correctly allocated attributes from HalfRangeData sequence

    Assumes incoming sequence of HalfRangeData is not sorted.

    The HalfRangeData sequence, once sorted, can be represented by the diagram below,
    where one HalfRangeData object is represented in a triplet column:
    [
        0     0     5     5     10     10     15     15     ...    # obj.position: int
        e  ,  e  ,  a  ,  e  ,  e   ,  a   ,  ""  ,  e   ,  ...    # obj.data: Any
        F     F     F     T     F      T      F      T      ...    # obj.end: bool
    ]

    This function/algorithm is the heart of the splicing logic.
    We do a single pass through the list of HalfRangeData objects, which is sorted by
    position (only). For each:
      - if the position value is _different_ than the previous one, then we
        issue a RangeData object where the previous pos. value is LOWER, current
        pos. value is UPPER, and current data tracker value is DATA
      - adjust the data tracker:
        if obj.end signifies the HalfRangeData object is the end of a range,
            then we take its data value away from the data tracker
        elif obj.end signifies the HalfRangeData object is the start of a range,
            then we add its value to the data tracker

    There are some inefficiencies: for example:
        - we still compute on hrd objects that have a zero data value,
          which represent the filled gaps, and do not
          have any impact on the data tracker. These can likely be eliminated.
        - for each hrd object that adds something to the data tracker, we
          have its inverse object. There may be a way to eliminate these too.
    """
    sorted_input = _sort_hrd(input)
    result = []
    position = sorted_input[0].position
    data = 0
    for hrd in sorted_input:
        # if position of next equals previous position,
        # yield a RangeData object:
        if hrd.position != position:
            result.append(
                RangeData(
                    lower=position,
                    upper=hrd.position,
                    data=data
                )
            )
        # update position state for subsequent comparison:
        position = hrd.position
        # adjust DATA according to boundary:
        # if END, then remove data;
        # if START, then add data
        if hrd.end:
            data = data - hrd.data
        else:
            data = data + hrd.data
    return result


# intended to be the logic aggregator/orchestrator: main
def splice_ranges(l1: list[RangeData], l2: list[RangeData], neutral_attr: Any) -> list[RangeData]:
    """Fill gaps in two lists of RangeData objects, then merge them and convert to HalfRangeData
    """
    minmax = _get_minmax_bounds_rd(l1 + l2)
    l1_prepped = _fill_gaps(l1, minmax.lowest, minmax.highest, neutral_attr)
    l2_prepped = _fill_gaps(l2, minmax.lowest, minmax.highest, neutral_attr)
    hrd_seq = _rd_to_hrd(l1_prepped + l2_prepped)
    new_range_seq = _generate_ranges_from_hrd_sequence(hrd_seq)
    return new_range_seq


# TODO: write function that applies a list of RangeData transformations to a range of values
#       the seed ranges are a start and a length range of values.
#       within that range, values need to be adjusted by the final list of RangeData objects.
#       then, the minimum of these adjusted values should be the answer we're looking for...
#       finally.
