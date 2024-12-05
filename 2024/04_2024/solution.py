def _right(word, board, row, col, rmx, cmx, wln):
    if not cmx - col >= wln:
        return 0
    for i in range(1, wln):
        if board[row][col+i] != word[i]:
            return 0
    return 1

def _right_down(word, board, row, col, rmx, cmx, wln):
    if not cmx - col >= wln or not rmx - row >= wln:
        return 0
    for i in range(1, wln):
        if board[row+i][col+i] != word[i]:
            return 0
    return 1

def _down(word, board, row, col, rmx, cmx, wln):
    if not rmx - row >= wln:
        return 0
    for i in range(1, wln):
        if board[row+i][col] != word[i]:
            return 0
    return 1

def _down_left(word, board, row, col, rmx, cmx, wln):
    if not col >= wln-1 or not rmx - row >= wln:
        return 0
    for i in range(1, wln):
        if board[row+i][col-i] != word[i]:
            return 0
    return 1

def _left(word, board, row, col, rmx, cmx, wln):
    if not col >= wln-1:
        return 0
    for i in range(1, wln):
        if board[row][col-i] != word[i]:
            return 0
    return 1

def _left_up(word, board, row, col, rmx, cmx, wln):
    if not col >= wln-1 or not row >= wln-1:
        return 0
    for i in range(1, wln):
        if board[row-i][col-i] != word[i]:
            return 0
    return 1

def _up(word, board, row, col, rmx, cmx, wln):
    if not row >= wln-1:
        return 0
    for i in range(1, wln):
        if board[row-i][col] != word[i]:
            return 0
    return 1

def _up_right(word, board, row, col, rmx, cmx, wln):
    if not cmx - col >= wln or not row >= wln-1:
        return 0
    for i in range(1, wln):
        if board[row-i][col+i] != word[i]:
            return 0
    return 1

def _check_candidates(prefix, postfix, fn, board, row, col, rmx, cmx, wln):
    if fn(prefix, board, row, col, rmx, cmx, wln) == 1:
        return postfix
    if fn(postfix, board, row, col, rmx, cmx, wln) == 1:
        return prefix
    return None

def _check_cross(word, board, row, col):
    rmx = len(board) # max rows
    cmx = len(board[0]) # max cols
    wln = (len(word)//2)+1 # keep the pivot-point in the prefix/postfix strings
    prefix = word[:wln][::-1] # reverse the prefix to simplify indexing
    postfix = word[wln*-1:]
    # _check_candidates sees whether prefix or postfix is in the upper-left and
    # upper-right branches. It returns the value expected in each one's
    # the opposing branch, which still must be confirmed
    _dr = _check_candidates(prefix, postfix, _left_up, board, row, col, rmx, cmx, wln)
    if not _dr:
        return 0
    _dl = _check_candidates(prefix, postfix, _up_right, board, row, col, rmx, cmx, wln)
    if not _dl:
        return 0
    # confirm the corresponding lower branches:
    if _down_left(_dl, board, row, col, rmx, cmx, wln) == 1:
        if _right_down(_dr, board, row, col, rmx, cmx, wln) == 1:
            return 1
    return 0

directions = [
    _right,
    _right_down,
    _down,
    _down_left,
    _left,
    _left_up,
    _up,
    _up_right,
]

def _check_single(word, board, row, col):
    x_count = 0
    rmx = len(board) # max rows
    cmx = len(board[0]) # max cols
    wln = len(word)
    for dir_fn in directions:
        x_count += dir_fn(word, board, row, col, rmx, cmx, wln)
    return x_count

def _wc(board, word, fn, idx):
    counter = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == word[idx]:
                xcount = fn(word, board, row, col)
                counter += xcount
    return counter


def _get_data(src):
    with open(src, 'r') as f:
        board = [line.strip() for line in f.readlines()]
    return board

def word_count(src, word, fn, idx):
    board = _get_data(src)
    return _wc(board, word, fn, idx)

def main():
    print(f"word count: {word_count("data.txt", "XMAS", _check_single, 0)}")
    print(f"word count: {word_count("data.txt", "MAS", _check_cross, 1)}")

if __name__ == "__main__":
    main()



# TESTS

def _get_testboard():
    return [
        "MMMSXXMASM",
        "MSAMXMSMSA",
        "AMXSXMAAMM",
        "MSAMASMSMX",
        "XMASAMXAMM",
        "XXAMMXXAMA",
        "SMSMSASXSS",
        "SAXAMASAAA",
        "MAMMMXMMMM",
        "MXMXAXMASX",
    ]

def test_check_single():
    testboard = _get_testboard()
    assert _wc(testboard, "XMAS", _check_single, 0) == 18

def test_check_cross():
    testboard = _get_testboard()
    assert _wc(testboard, "MAS", _check_cross, 1) == 9
