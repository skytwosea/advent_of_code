import pytest
import logging

logging.basicConfig(
    filename="sol.log",
    encoding="utf-8",
    filemode="w",
    level=logging.INFO,
)

class Guard:

    _guard_marker = '^'
    _open_cell = '.'
    _blocked_cell = '#'
    _visited_cell = 'x'
    _headings = (
        "North",
        "East",
        "South",
        "West",
    )

    def __init__(self, board):
        self.board = board
        self.position = self._find_self()
        self.heading = self._headings[0]

    def _find_self(self) -> list:
        for r, row in enumerate(self.board):
            for c, col in enumerate(row):
                if col == self._guard_marker:
                    return [r, c]
        raise ValueError("Guard not found!")

    def get_head(self):
        return self.heading

    def get_pos(self):
        return self.position

    def set_pos(self, pos):
        self.position = pos

    def turn_right(self):
        turned_idx = (self._headings.index(self.heading) + 1) % 4
        self.heading = self._headings[turned_idx]

    def turn_left(self):
        turned_idx = (self._headings.index(self.heading) - 1) % 4
        self.heading = self._headings[turned_idx]

    def step(self, steps=1):
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
                raise ValueError(f"bad heading in step(): {self.heading}")

    def peek(self):
        match self.heading:
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
                raise ValueError(f"bad heading in step(): {self.heading}")
        try:
            if self.board[next_row][next_col] == self._blocked_cell:
                return False
            return True
        except IndexError as e:
            # next step is off-board
            raise

    def is_cell_new(self):
        row, col = self.get_pos()
        return self.board[row][col] != self._visited_cell

    def mark(self):
        row, col = self.get_pos()
        self.board[row][col] = self._visited_cell

    def march(self, limit=10000):
        total_steps = 0
        try:
            while total_steps < limit:
                if self.is_cell_new():
                    total_steps += 1
                    self.mark()
                if not self.peek():
                    self.turn_right()
                self.step()
        except IndexError as e:
            return total_steps

def _get_data(src):
    with open(src, 'r') as f:
        board = [[c for c in line.strip()] for line in f.readlines()]
    return board

def map_route(src):
    board = _get_data(src)
    guard = Guard(board)
    return guard.march()

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
    assert g.get_pos() == [6, 4]
    with pytest.raises(ValueError, match="Guard not found!"):
        h = Guard([['.','.','.',], ['.','.','.',], ['.','.','.',],])

def test_guard_step(testboard):
    g = Guard(testboard)
    g.set_pos([5,5])
    g.step() # starts out facing north
    assert g.get_pos() == [4,5]
    g.turn_right()
    g.step()
    assert g.get_pos() == [4,6]
    g.turn_right()
    g.step()
    assert g.get_pos() == [5,6]
    g.turn_right()
    g.step()
    assert g.get_pos() == [5,5]

def test_guard_turn_right(testboard):
    g = Guard(testboard)
    assert g.get_head() == "North"
    g.turn_right()
    assert g.get_head() == "East"
    g.turn_right()
    assert g.get_head() == "South"
    g.turn_right()
    assert g.get_head() == "West"

def test_guard_turn_left(testboard):
    g = Guard(testboard)
    assert g.get_head() == "North"
    g.turn_left()
    assert g.get_head() == "West"
    g.turn_left()
    assert g.get_head() == "South"
    g.turn_left()
    assert g.get_head() == "East"

def test_guard_peek(testboard):
    g = Guard(testboard)
    assert g.peek()
    g.turn_left()
    g.step(2)
    assert not g.peek()

def test_full_walk(testboard):
    g = Guard(testboard)
    ans = g.march()
    assert ans == 41
