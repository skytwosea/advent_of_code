import pytest
from time import sleep
import sys
# import traceback
import logging

logging.basicConfig(
    filename="sol.log",
    encoding="utf-8",
    filemode="w",
    level=logging.INFO,
)

class MapError(Exception):
    """Raised when there is no viable heading: see Guard._peek()"""
    pass

class Guard:

    _guard = '^'
    _open = '.'
    _blocked = '#'
    _visited = 'x'
    _headings = (
        "North",
        "East",
        "South",
        "West",
    )
    _gmarkers = ['^', '>', 'v', '<',]
    # _notouchy = ['^', '>', 'v', '<', '#',]

    def __init__(self, board):
        self.board = board
        self.position = self._find_self()
        self.start_pos = self.position.copy()
        self.heading = self._headings[0]
        self.obstructions = set()

    def _find_self(self) -> list:
        for r, row in enumerate(self.board):
            for c, col in enumerate(row):
                if col == self._guard:
                    return [r, c]
        raise ValueError("Guard not found!")

    def get_heading(self):
        return self.heading

    def get_position(self):
        return self.position

    def set_position(self, pos):
        self.position = pos

    def _turn_right(self, turn_count=1):
        if turn_count == 0:
            return
        turned_idx = (self._headings.index(self.heading) + turn_count) % 4
        self.heading = self._headings[turned_idx]

    def _shoulder_check_right(self, turn_count=1, index_only=False):
        if turn_count == 0:
            return self.heading
        turned_idx = (self._headings.index(self.heading) + turn_count) % 4
        if index_only:
            return turned_idx
        return self._headings[turned_idx]

    def _turn_left(self, turn_count=1):
        if turn_count == 0:
            return
        turned_idx = (self._headings.index(self.heading) - turn_count) % 4
        self.heading = self._headings[turned_idx]

    def _shoulder_check_left(self, turn_count=1):
        if turn_count == 0:
            return self.heading
        turned_idx = (self._headings.index(self.heading) - turn_count) % 4
        return self._headings[turned_idx]

    def _step(self, steps=1):
        match self.heading:
            case "North":
                self.position[0] -= steps
            case "East":
                self.position[1] += steps
            case "South":
                self.position[0] += steps
            case "West":
                self.position[1] -= steps
            case _:
                raise ValueError(f"bad heading in _step(): {self.heading}")

    # def _step(self, row, col, coords_only=False, heading=None, steps=1):
    #     if not heading:
    #         heading = self.heading
    #     match heading:
    #         case "North":
    #             row -= steps
    #         case "East":
    #             col += steps
    #         case "South":
    #             row += steps
    #         case "West":
    #             col -= steps
    #         case _:
    #             raise ValueError(f"bad heading in _step_probe(): {heading}")
    #     if coords_only:
    #         return (row, col)
    #     self.position[0] = row
    #     self.position[1] = col

    def _peek(self, row, col, turn_count=0, _heading=None, coords_only=False) -> int:
        """Return the number of 90 degree turns to find clear heading

        _shoulder_check_{right,left} allows _peek() to check all cardinal
        directions without turning the guard.
        If no valid heading is found, raise error: map can't be walked within
        the present constraints.
        """
        if turn_count >= 4:
            # should be unreachable: if we're actually trapped on all four sides,
            # the real problem is how we got into this trap
            raise MapError(f"all directions blocked at [{self.get_position()}]")
        if not _heading:
            _heading = self.heading 
        match _heading:
            case "North":
                next_row = row - 1
                next_col = col
            case "East":
                next_row = row
                next_col = col + 1
            case "South":
                next_row = row + 1
                next_col = col
            case "West":
                next_row = row
                next_col = col - 1
            case _:
                raise ValueError(f"bad heading in _step(): {_heading}")
        if not self._in_bounds(next_row, next_col):
            return None
        if coords_only:
            return (next_row, next_col)
        if self.board[next_row][next_col] == self._blocked:
            turn_count += 1
            swivel_to = self._shoulder_check_right(turn_count)
            return self._peek(row, col, turn_count, swivel_to)
        return turn_count

    def _is_cell_new(self, row, col):
        return self.board[row][col] != self._visited

    def _is_cell_tracked(self, row, col):
        return self.board[row][col] in self._gmarkers

    def _mark(self, row, col):
        self.board[row][col] = self._visited

    def _track(self, row, col):
        gmark = self._gmarkers[self._headings.index(self.heading)]
        self.board[row][col] = gmark

    def _in_bounds(self, row, col):
        return row >= 0 and row < len(self.board) and col >= 0 and col < len(self.board[0])

    # def _send_probe(self, row, col, heading, display=None, unique_steps=None):
    #     required_marker = self._gmarkers[self._headings.index(heading)]
    #     probe_steps = 0
    #     while probe_steps < 1000:
    #         row, col = self._step_probe(row, col, heading)
    #         probe_steps += 1
    #         if display is not False and display is not None:
    #             print(f"steps: {unique_steps} | probe: {probe_steps}{' '*10}", end='\r')
    #         if not self._in_bounds(row, col):
    #             return False
    #         _cell = self.board[row][col]
    #         if _cell == self._blocked:
    #             turn_count = self._peek(row, col)
    #             if turn_count is None:
    #                 return False
    #             heading = self._shoulder_check_right(turn_count)
    #             required_marker = self._gmarkers[self._headings.index(heading)]
    #         if _cell == required_marker:
    #             return True
    #     return False

    # def _check_rh_loop_candidate(self, row, col, display=None, unique_steps=None):
    #     """Check every right-hand-side orthogonal path for loop potential.

    #     If the guard can turn right and end up on an old track headed along-stream, then
    #     an obstruction straight ahead will force the guard into a loop.

    #     The right-hand-side path must have a tracking marker in the correct orientation:
    #     it must be oriented 90 degrees to the right of the guard's current heading.
    #     There also cannot be an obstruction between the guard and the potential marker.
        
    #     If the above conditions are met, then the cell immediately in front of the guard is an
    #     obstruction candidate. If it is not already an obstruction, we can add it to the
    #     list.

    #     _peek_bearing: take current heading and look 90 degrees right, without turning guard
    #     rhc_coord: peek() in the _peek_bearing direction to ensure that bearing is valid.
    #     fwd_coord: peek() immediately ahead of the guard to ensure that cell is valid (ie.
    #     not off grid) and does not already contain an obstruction.

    #     If all conditions are met, then add the hash of the coordinate tuple to a set.
    #     """
    #     _peek_bearing = self._shoulder_check_right()
    #     if rhc_coord := self._peek(row, col, _heading=_peek_bearing, coords_only=True):
    #         if fwd_coord := self._peek(row, col, coords_only=True):
    #             if fwd_coord != tuple(self.start_pos):
    #                 # if self.board[fwd_coord[0]][fwd_coord[1]] != self._blocked:
    #                 if self.board[fwd_coord[0]][fwd_coord[1]] not in self._notouchy:
    #                     if self._send_probe(row, col, _peek_bearing, display, unique_steps):
    #                         obstacle_with_approach = (fwd_coord[0], fwd_coord[1], _peek_bearing)
    #                         self.obstructions.add(obstacle_with_approach.__hash__())

    def march(self, limit=10000, display=False):
        unique_steps = 1
        while unique_steps < limit:
            row, col = self.get_position()
            if not self._is_cell_tracked(row, col):
                unique_steps += 1
            self._track(row, col)
            if display:
                self._print_display_window(row, col, unique_steps, delay=0.05)
            else:
                print(f"steps: {unique_steps}", end='\r')
            turn_count = self._peek(row, col)
            if turn_count is None:
                return unique_steps
            self._turn_right(turn_count)
            self._step()

    # def march_and_block(self, limit=10000, display=False):
    #     unique_steps = 1 # compensate for missing start cell when using this tracking method
    #     while unique_steps < limit:
    #         row, col = self.get_position()
    #         self._check_rh_loop_candidate(row, col, display, unique_steps)
    #         if not self._is_cell_tracked(row, col):
    #             unique_steps += 1
    #         self._track(row, col)
    #         if display:
    #             self._print_display_window(row, col, unique_steps, len(self.obstructions))
    #         else:
    #             print(f"steps: {unique_steps} | probe: 0{' '*10}", end='\r')
    #         turn_count = self._peek(row, col)
    #         if turn_count is None:
    #             return (unique_steps, len(self.obstructions))
    #         self._turn_right(turn_count)
    #         self._step()

    def _print_display_window(self, row, col, unique_steps, unique_obstructions=None, size=30, delay=1.5):
        _window, _side = self._create_display_window(row, col, size)
        if unique_steps > 1:
            print("\033[A"*(_side+4))
        print(_window)
        print(f"unique steps: {unique_steps}\nunique obstructions: {unique_obstructions}\ncoordinates: {(row,col)}")
        sleep(delay)

    def _create_display_window(self, row, col, size):
        gmark = self._gmarkers[self._headings.index(self.heading)]
        window = []
        for r in range(row-size, row+size+1):
            line = [self.board[r][c] if self._in_bounds(r, c) else ' ' for c in range(col-size, col+size+1)]
            window.append([' ' if c == '.' else c for c in line])
        window[size][size] = f"\033[30;45m{gmark}\033[0m"
        return ('\n'.join([' '.join(line) for line in window]), len(window))

def _get_data(src):
    with open(src, 'r') as f:
        board = [[c for c in line.strip()] for line in f.readlines()]
    return board

def map_route(src):
    board = _get_data(src)
    guard = Guard(board)
    display = True if len(sys.argv) > 1 else False
    result = guard.march(display=display)
    if not display:
        print(f"\ntotal steps: {result}")

def main():
    map_route("data.txt")

if __name__ == "__main__":
    main()



# TESTS

@ pytest.fixture
def testboard():
    return _get_data("test_data.txt")

def test_get_data(testboard):
    assert testboard[0]  == ['.','.','.','.','#','.','.','.','.','.',]
    assert testboard[6]  == ['.','#','.','.','^','.','.','.','.','.',]
    assert testboard[-1] == ['.','.','.','.','.','.','#','.','.','.',]

def test_find_self(testboard):
    g = Guard(testboard)
    assert g.get_position() == [6, 4]
    assert g.start_pos == [6, 4]
    with pytest.raises(ValueError, match="Guard not found!"):
        h = Guard([['.','.','.',], ['.','.','.',], ['.','.','.',],])

def test_guard_step(testboard):
    g = Guard(testboard)
    g.set_position([5,5])
    g._step() # starts out facing north
    assert g.get_position() == [4,5]
    g._turn_right()
    g._step()
    assert g.get_position() == [4,6]
    g._turn_right()
    g._step()
    assert g.get_position() == [5,6]
    g._turn_right()
    g._step()
    assert g.get_position() == [5,5]

def test_guard_turn_right(testboard):
    g = Guard(testboard)
    assert g.get_heading() == "North"
    g._turn_right()
    assert g.get_heading() == "East"
    g._turn_right()
    assert g.get_heading() == "South"
    g._turn_right()
    assert g.get_heading() == "West"
    g._turn_right(3)
    assert g.get_heading() == "South"
    g._turn_right(4)
    assert g.get_heading() == "South"
    g._turn_right(7)
    assert g.get_heading() == "East"

def test_guard_turn_left(testboard):
    g = Guard(testboard)
    assert g.get_heading() == "North"
    g._turn_left()
    assert g.get_heading() == "West"
    g._turn_left()
    assert g.get_heading() == "South"
    g._turn_left()
    assert g.get_heading() == "East"
    g._turn_left(2)
    assert g.get_heading() == "West"
    g._turn_left(4)
    assert g.get_heading() == "West"
    g._turn_left(7)
    assert g.get_heading() == "North"

def test_guard_peek_next_heading_open(testboard):
    g = Guard(testboard)
    row, col = g.get_position()
    assert g._peek(row, col) == 0
    g._turn_left()
    g._step(2)
    row, col = g.get_position()
    assert g._peek(row, col) == 1

def test_guard_peek_one_closed_heading():
    board_turn_twice = [
        ['.','#','.',],
        ['.','^','#',],
        ['.','.','.',],
    ]
    g = Guard(board_turn_twice)
    row, col = g.get_position()
    assert g._peek(row, col) == 2

def test_guard_peek_two_closed_headings():
    board_turn_thrice = [
        ['.','#','.',],
        ['.','^','#',],
        ['.','#','.',],
    ]
    g = Guard(board_turn_thrice)
    row, col = g.get_position()
    assert g._peek(row, col) == 3

def test_guard_peek_one_closed_heading():
    board_turn_fource = [
        ['.','#','.',],
        ['#','^','#',],
        ['.','#','.',],
    ]
    g = Guard(board_turn_fource)
    with pytest.raises(MapError):
        row, col = g.get_position()
        assert g._peek(row, col) == _

def test_march_only(testboard):
    g = Guard(testboard)
    ans = g.march()
    assert ans == 41

def test_create_display_window(testboard):
    g = Guard(testboard)
    assert g._create_display_window(6, 4, size=3) == ("  #          \n            #\n             \n#     \033[30;45m^\033[0m      \n             \n             \n          #  ", 7)

# def test_march_and_block(testboard):
#     g = Guard(testboard)
#     srow, scol = g.start_pos
#     steps, obstructions = g.march_and_block()
#     assert steps == 41
#     assert obstructions == 6
#     erow, ecol = g.start_pos
#     assert srow == erow
#     assert scol == ecol

# def test_check_rh_loop_candidate_once():
#     board_check_rh_candidates = [
#         ['.','.','.',],
#         ['.','^','>',],
#         ['.','.','.',],
#     ]
#     g = Guard(board_check_rh_candidates)
#     row, col = g.get_position()
#     g._check_rh_loop_candidate(row, col)
#     assert len(g.obstructions) == 1

# def test_check_rh_loop_candidate_twice():
#     board_check_rh_candidates = [
#         ['.','.','.','.',],
#         ['^','>','v','v',],
#         ['.','.','.','.',],
#         ['.','.','.','.',],
#     ]
#     g = Guard(board_check_rh_candidates)
#     row, col = g.get_position()
#     g._check_rh_loop_candidate(row, col)
#     assert len(g.obstructions) == 1
#     g._step()
#     g._turn_right()
#     g._step()
#     g._step()
#     row, col = g.get_position()
#     g._check_rh_loop_candidate(row, col)
#     assert len(g.obstructions) == 2
#     g._step()
#     row, col = g.get_position()
#     g._check_rh_loop_candidate(row, col)
#     assert len(g.obstructions) == 2

# def test_check_rh_loop_candidate_with_gap():
#     board_check_rh_candidates = [
#         ['.','.','.','.',],
#         ['^','.','.','>',],
#         ['.','.','.','.',],
#         ['.','.','.','.',],
#     ]
#     g = Guard(board_check_rh_candidates)
#     row, col = g.get_position()
#     g._check_rh_loop_candidate(row, col)
#     assert len(g.obstructions) == 1

# def test_check_rh_loop_candidate_with_block():
#     board_check_rh_candidates = [
#         ['.','.','.','.',],
#         ['.','.','.','.',],
#         ['^','.','#','>',],
#         ['.','.','.','.',],
#     ]
#     g = Guard(board_check_rh_candidates)
#     row, col = g.get_position()
#     g._check_rh_loop_candidate(row, col)
#     assert len(g.obstructions) == 0
