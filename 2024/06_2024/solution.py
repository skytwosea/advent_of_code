import pytest
from time import sleep
import sys
# import traceback
# import logging

# logging.basicConfig(
#     filename="sol.log",
#     encoding="utf-8",
#     filemode="w",
#     level=logging.INFO,
# )

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

    def __init__(self, board):
        self.board = board
        self.position = self._find_self()
        self.heading = self._headings[0]

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

    def _shoulder_check_right(self, turn_count=1):
        if turn_count == 0:
            return self.heading
        turned_idx = (self._headings.index(self.heading) + turn_count) % 4
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

    def _peek(self, turn_count=0, _heading=None) -> int:
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
                next_row = self.position[0] - 1
                next_col = self.position[1]
            case "East":
                next_row = self.position[0]
                next_col = self.position[1] + 1
            case "South":
                next_row = self.position[0] + 1
                next_col = self.position[1]
            case "West":
                next_row = self.position[0]
                next_col = self.position[1] - 1
            case _:
                raise ValueError(f"bad heading in _step(): {_heading}")
        if not self._in_bounds(next_row, next_col):
            return None
        if self.board[next_row][next_col] == self._blocked:
            turn_count += 1
            swivel_to = self._shoulder_check_right(turn_count)
            return self._peek(turn_count, swivel_to)
        return turn_count

    def _is_cell_new(self, row, col):
        return self.board[row][col] != self._visited

    def _mark(self, row, col):
        self.board[row][col] = self._visited

    def _in_bounds(self, row, col):
        return row >= 0 and row < len(self.board) and col >= 0 and col < len(self.board[0])

    def march(self, limit=10000, display=False):
        unique_steps = 0
        while unique_steps < limit:
            row, col = self.get_position()
            if self._is_cell_new(row, col):
                unique_steps += 1
                self._mark(row, col)
            if display:
                self._print_display_window(row, col, unique_steps)
            turn_count = self._peek()
            if turn_count is None:
                return unique_steps
            self._turn_right(turn_count)
            self._step()

    def _create_display_window(self, row, col, size=5):
        gmark = self._gmarkers[self._headings.index(self.heading)]
        window = []
        for r in range(row-size, row+size+1):
            window.append([self.board[r][c] if self._in_bounds(r, c) else ' ' for c in range(col-size, col+size+1)])
        window[size][size] = f"\033[30;45m{gmark}\033[0m"
        return ('\n'.join([' '.join(line) for line in window]), len(window))

    def _print_display_window(self, row, col, us, size=15, delay=0.025):
        _window, _side = self._create_display_window(row, col, size)
        if us > 1:
            print("\033[A"*(_side+2))
        print(_window)
        print(f"unique steps: {us}")
        sleep(delay)

def _get_data(src):
    with open(src, 'r') as f:
        board = [[c for c in line.strip()] for line in f.readlines()]
    return board

def map_route(src):
    board = _get_data(src)
    guard = Guard(board)
    display = True if len(sys.argv) > 1 else False
    return guard.march(display=display)

def main():
    print(f"total steps: {map_route("data.txt")}")

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
    assert g._peek() == 0
    g._turn_left()
    g._step(2)
    assert g._peek() == 1

def test_guard_peek_one_closed_heading():
    board_turn_twice = [
        ['.','#','.',],
        ['.','^','#',],
        ['.','.','.',],
    ]
    g = Guard(board_turn_twice)
    assert g._peek() == 2

def test_guard_peek_two_closed_headings():
    board_turn_thrice = [
        ['.','#','.',],
        ['.','^','#',],
        ['.','#','.',],
    ]
    g = Guard(board_turn_thrice)
    assert g._peek() == 3

def test_guard_peek_one_closed_heading():
    board_turn_fource = [
        ['.','#','.',],
        ['#','^','#',],
        ['.','#','.',],
    ]
    g = Guard(board_turn_fource)
    with pytest.raises(MapError):
        assert g._peek() == _

def test_full_walk(testboard):
    g = Guard(testboard)
    ans = g.march()
    assert ans == 41

def test_create_display_window(testboard):
    g = Guard(testboard)
    assert g._create_display_window(6, 4, size=3) == (". # . . . . .\n. . . . . . #\n. . . . . . .\n# . . \033[30;45m^\033[0m . . .\n. . . . . . .\n. . . . . . .\n. . . . . # .", 7)
